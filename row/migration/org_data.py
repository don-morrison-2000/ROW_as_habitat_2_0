
import arcpy
import os, sys
from arcgis.gis import GIS
import row.logger
logger = row.logger.get('row_log')
import keyring
import row.constants as c
import row.migration.migration_specs


DB_DIR = r'C:\Users\dmorri28\Documents\ArcGIS\Projects\MyProject\CC-SQL2k16-ERC-SDE.sde'
DB_PREFIX = 'ROW_Habitat.SDE.'

def run(gis, source_org_id, target_org_id):

    for migration_spec in [m for m in row.migration.migration_specs.MIGRATION_SPECS if m['type'] ==  'Feature Service']:
            logger.info (f"Processing: {migration_spec['title']}")
            agol_item = [i for i in gis.users.me.items(folder=target_org_id, max_items=1000) if i.title==migration_spec['title'] and i.type==migration_spec['type']][0]
            for layer_spec in migration_spec['layers']:

                logger.info (f"Processing layer: {layer_spec['title']}")
                db_path = os.path.join(DB_DIR, DB_PREFIX + layer_spec['sde_source'])

                desc = arcpy.Describe(db_path)
                if desc.dataType == "FeatureClass":
                    org_sde_lyr = arcpy.MakeFeatureLayer_management(db_path, "org_sde_lyr", f"Org_ID = '{source_org_id}'", None)[0]
                elif desc.dataType == "Table":
                     org_sde_lyr = arcpy.MakeTableView_management(db_path, "org_sde_lyr", f"Org_ID = '{source_org_id}'")[0]
            
                agol_url = f"{agol_item.url}/{layer_spec['idx']}"

                arcpy.Append_management(org_sde_lyr, agol_url, 'NO_TEST')
                arcpy.Delete_management (org_sde_lyr.name)

                if source_org_id != target_org_id:
                     arcpy.management.CalculateField(agol_url, 'Org_ID', f"'{target_org_id}'", "PYTHON3", '')

    logger.info ('Done')


    return




if __name__ == '__main__':
    SOURCE_SDE_ORG = 'DEVOrgB'
    #TARGET_AGOL_ORG = c.MODEL_ORG_ID
    TARGET_AGOL_ORG = 'ROW2_DEVOrgA'
    
    logger.info ("Logging to %s" % row.logger.LOG_FILE)
    gis = GIS("https://www.arcgis.com", c.AGOL_OWNER_ID, keyring.get_password('AGOL', c.AGOL_OWNER_ID))

    run (gis, SOURCE_SDE_ORG, TARGET_AGOL_ORG)

