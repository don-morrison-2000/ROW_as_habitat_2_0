# Use an existing Row 1.0 org create a set of model objects in a specified folder

# Export source org to file geodatabse
# Remove junk (obsolete relations and tables)
# Do the copy (no data)

import arcpy
import os, sys
from arcgis.gis import GIS
from arcgis.features import FeatureLayerCollection
import row.usr.logger
logger = row.usr.logger.get('row_log')

import row.usr.constants as c
import row.migration.migration_specs 

import shutil
import zipfile
from pathlib import Path
import time
import random
import keyring
from datetime import datetime as dt

SOURCE_ORG_ID = 'DEVOrgB'
DB_DIR = r'C:\Users\dmorri28\Documents\ArcGIS\Projects\MyProject\CC-SQL2k16-ERC-SDE.sde'
DB_PREFIX = 'ROW_Habitat.SDE.'

# For data layers
# Import xml to file geo database
# Publish each file as web layer and then combine based on struct
# 

def __import_sde_schema(export_xml_file):
    row_fgdb = os.path.join(arcpy.env.scratchFolder, f'row_export_{random.randint(10000000, 99999999)}.gdb')
    if arcpy.Exists(row_fgdb):
        arcpy.Delete_management(row_fgdb)
    logger.debug (f"Importing ROW schema to {row_fgdb}")
    arcpy.CreateFileGDB_management(os.path.dirname(row_fgdb), os.path.basename(row_fgdb))
    arcpy.ImportXMLWorkspaceDocument_management(row_fgdb, export_xml_file, 'SCHEMA_ONLY')
    return row_fgdb



def __remove_obsolete_sde_objects(row_fgdb, migration_spec):
    # Find sde object to keep (feature classes, tables, related tables)
    keep_objects = []
    for l_spec in [l for l in migration_spec['layers'] if 'sde_source' in l.keys()]:
        keep_objects.append(l_spec['sde_source']) 
        keep_objects.extend(*[l_spec['sde_relations']])
    logger.debug (f"SDE Objects to keep: {keep_objects}")

    arcpy.env.workspace = row_fgdb
    arcpy.Delete_management([os.path.join(row_fgdb, o) for o in (arcpy.ListFeatureClasses() + arcpy.ListTables() + arcpy.ListRasters()) if o not in keep_objects])
    arcpy.env.workspace = arcpy.env.scratchGDB
    return


def __backup_schema (gis, fcs):
    title = f"Feature Layer Archive {dt.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    output_gdb = os.path.join(arcpy.env.scratchFolder, f"{title}.gdb")

    if not arcpy.Exists(output_gdb):
        arcpy.management.CreateFileGDB(os.path.dirname(output_gdb), os.path.basename(output_gdb))

    # Copy the feature class to the new geodatabase
    arcpy.conversion.FeatureClassToGeodatabase([fc for fc in fcs if arcpy.Describe(fc).dataType=="FeatureClass"], output_gdb)
    arcpy.conversion.TableToGeodatabase([fc for fc in fcs if arcpy.Describe(fc).dataType=="Table"], output_gdb)
    arcpy.ClearWorkspaceCache_management(output_gdb)

    item_fgdb_zip = os.path.join(arcpy.env.scratchFolder, f"{title}.zip")
    shutil.make_archive(os.path.splitext(item_fgdb_zip)[0], 'zip', root_dir=os.path.dirname(output_gdb), base_dir=os.path.basename(output_gdb))

    logger.debug (f"Uploading {item_fgdb_zip} to ArcGIS Online")
    item_properties = {
        "title": title,
        "description": "Archived data schema",
        "tags": f"{c.MODEL_ORG_ID}",
        "type": "File Geodatabase", 
        "snippet": "Archived data schema"
    } 
    job = gis.content.folders.get(c.MODEL_ORG_ID).add(item_properties=item_properties, file=item_fgdb_zip)
    map(os.remove, [item_fgdb_zip] + list(set(os.path.dirname(fc) for fc in fcs)))
    return



def __publish_fgdb (gis, fgdb, migration_spec):
    service_name = migration_spec['tag']

    try:
        # If a sd has already been published, it has to be moved to root folder for the overwrite to work
        sd_item = [i for i in gis.users.me.items(folder=c.MODEL_ORG_ID, max_items=1000) if i.title==migration_spec['title'] and i.type=='Service Definition'][0]
        sd_item.move('/')
    except Exception:
        pass
   
    logger.debug (f"Creating a map with the file geodatbase layers")
    aprx_path = os.path.join(arcpy.env.scratchFolder, 'blank_project.aprx')
    aprx = arcpy.mp.ArcGISProject(os.path.join(c.CODE_BASE, 'row', 'adm', 'templates', 'blank_project.aprx'))
    aprxMap = aprx.listMaps()[0]

    m_cim = aprxMap.getDefinition("V3")
    m_cim.useServiceLayerIDs = True
    aprxMap.setDefinition(m_cim)

    for layer_spec in [l for l in migration_spec['layers'] if len(l['sde_source']) > 0]:
        lyr = aprxMap.addDataFromPath(os.path.join(fgdb, layer_spec['sde_source']))
        l_cim = lyr.getDefinition("V3")
        l_cim.name = layer_spec['title']
        if arcpy.Describe(os.path.join(DB_DIR, DB_PREFIX + layer_spec['sde_source'])).dataType == "FeatureClass":
            l_cim.serviceLayerID = layer_spec['idx']
        else:
            l_cim.serviceTableID = layer_spec['idx']
        lyr.setDefinition(l_cim)
    aprx.saveACopy(aprx_path)

    aprx = arcpy.mp.ArcGISProject(aprx_path) 
    aprxMap = aprx.listMaps()[0] 

    sddraft_path = os.path.join(arcpy.env.scratchFolder, service_name + ".sddraft")
    sd_path = os.path.join(arcpy.env.scratchFolder, service_name + ".sd")
    arcpy.Delete_management([sddraft_path, sd_path])

    logger.debug (f"Creating a sharing draft")
    sharing_draft = aprxMap.getWebLayerSharingDraft("HOSTING_SERVER", "FEATURE", service_name)
    sharing_draft.summary = migration_spec['snippet'].replace('{ORG_NAME}', c.MODEL_ORG_NAME).replace('{ORG_ID}', c.MODEL_ORG_ID)
    sharing_draft.tags = f"{migration_spec['tag']},{c.MODEL_ORG_ID.lower()}"
    sharing_draft.description = migration_spec['description'].replace('{ORG_NAME}', c.MODEL_ORG_NAME).replace('{ORG_ID}', c.MODEL_ORG_ID)
    sharing_draft.overwriteExistingService = True
    sharing_draft.exportToSDDraft(sddraft_path)
 
    logger.debug (f"Staging the sharing draft")
    arcpy.StageService_server(sddraft_path, sd_path)

    logger.debug (f"Publishing the hosted feature layer")
    arcpy.SignInToPortal("https://www.arcgis.com", c.AGOL_OWNER_ID, keyring.get_password('AGOL', c.AGOL_OWNER_ID))
    published_item_id = arcpy.UploadServiceDefinition_server(sd_path, "My Hosted Services")[3]
    published_item = gis.content.get(published_item_id)
    published_item.update({'title': migration_spec['title']})
    published_item.move(c.MODEL_ORG_ID)
    sd_item = [i for i in gis.users.me.items(folder=None, max_items=1000) if i.title==service_name and i.type=='Service Definition'][0]
    sd_item.update({'title': migration_spec['title'].replace('{ORG_NAME}', c.MODEL_ORG_NAME).replace('{ORG_ID}', c.MODEL_ORG_ID), 'tags': c.MODEL_ORG_ID.lower()})
    sd_item.move(c.MODEL_ORG_ID)
    return



def run():
    logger.info ("Logging to %s" % row.usr.logger.LOG_FILE)

    gis = GIS("https://www.arcgis.com", c.AGOL_OWNER_ID, keyring.get_password('AGOL', c.AGOL_OWNER_ID))

    # Collect the pre-updated feature classes so they can be backed up
    fcs = []

    export_xml_file = os.path.join(arcpy.env.scratchFolder, 'export_xml_file.xml')
    # if os.path.exists(export_xml_file):
    #     os.remove(export_xml_file)
    # logger.info (f"Exporting ROW sde schema to {export_xml_file}")
    # arcpy.management.ExportXMLWorkspaceDocument(
    #     in_data=AppInfo.path_db_dir,
    #     out_file=export_xml_file,
    #     export_type="SCHEMA_ONLY",
    #     storage_type="BINARY",
    #     export_metadata="METADATA")
    for x in range (1,2):
        print (str(x))
        for migration_spec in [m for m in row.migration.migration_specs.MIGRATION_SPECS if m['type'] == 'Feature Service']:

            if len([r for r in c.ORG_ITEMS_REGISTRY if r['tag'] == migration_spec['tag']]) != 1:
                raise Exception (f"Migration spec and organization registry are out of sync with tag: {migration_spec['tag']}")

            logger.info (f"Processing {migration_spec['title']}. Importing SDE objects") 
            row_fgdb = __import_sde_schema(export_xml_file)
        
            logger.info (f"Removing unnecessary SDE object from {row_fgdb}") 
            __remove_obsolete_sde_objects(row_fgdb, migration_spec)

            arcpy.env.workspace = row_fgdb
            fcs += [os.path.join(row_fgdb, fc) for fc in arcpy.ListFeatureClasses() + arcpy.ListTables()]

            logger.info (f"Publishing {migration_spec['title']}") 
            __publish_fgdb (gis, row_fgdb, migration_spec)

    __backup_schema (gis, fcs)

    logger.info ('Done')


    return





if __name__ == '__main__':
    run()

