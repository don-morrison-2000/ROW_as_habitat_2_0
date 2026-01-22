import arcpy
import os, sys
from arcgis.gis import GIS
from  arcgis.gis import SharingLevel
import row.constants as c
import row.adm.adm_utils
import row.logger
logger = row.logger.get('row_log')
import json
from datetime import datetime as dt, UTC


def propagate_item (gis, source_item, target_item, source_org_id, target_org_id, replacement_list):
    logger.debug (f"{target_org_id}: Finding text replacements for {target_item.type} '{target_item.title}'")
    text_replacements = replacement_list.copy()


    logger.debug (f"{target_org_id}: Updating item header")
    target_item.update({
        'title':        row.adm.adm_utils.fixup_json (source_item.title, text_replacements, []), 
        'snippet':      row.adm.adm_utils.fixup_json (source_item.snippet, text_replacements, []), 
        'description':  row.adm.adm_utils.fixup_json (source_item.description, text_replacements, []),
        'tags':         [row.adm.adm_utils.get_item_registry_tag (source_item), target_org_id.lower()], 
        'typeKeywords': source_item.typeKeywords,
        'categories':   source_item.categories,
        })

    logger.debug (f"{target_org_id}: Updating item data")
    target_item.update({'text': row.adm.adm_utils.fixup_json (source_item.get_data(), [r for r in text_replacements if r[0] != r[1]], [])})

    #update_item_resource_files (gis, source_item, target_item)
    propagate_item_resources (gis, source_item, target_item)
    update_item_sharing_level (gis, target_item, target_org_id)

    return


def propagate_item_resources (gis, source_item, target_item):
    target_item = gis.content.get(target_item.id)

    source_resources = {r['resource']:r for r in source_item.resources.list()}
    target_resources = {r['resource']:r for r in target_item.resources.list()} 
       
    logger.debug (f"Updating {len(source_resources)} {source_item.type} resource files")
    adds = [r for r in source_resources.keys() if r not in target_resources.keys()]
    updates = [r for r in source_resources.keys() if r in target_resources.keys()]
    deletes = [r for r in target_resources.keys() if r not in source_resources.keys()]

    for r in deletes:
        target_item.resources.remove(r)

    for r in adds:
        f = source_item.resources.get(r,  try_json = False)
        target_item.resources.add(file=f, folder_name=os.path.dirname(r),  file_name=os.path.basename(r), access=source_resources[r]['access'])

    for r in updates:
        f = source_item.resources.get(r, try_json = False)
        target_item.resources.update(file=f, folder_name=os.path.dirname(r),  file_name=os.path.basename(r))

    return




def update_item_sharing_level (gis, target_item, target_org_id):
    org_spec = row.adm.adm_utils.get_org_spec (target_org_id)
    item_spec = row.adm.adm_utils.get_item_registry_spec (target_item)
    if item_spec['allow_extended_sharing']:
        new_sharing_level = org_spec['extended_sharing_level']
    else:
        new_sharing_level = SharingLevel.PRIVATE
    if target_item.sharing.sharing_level != new_sharing_level:
        logger.info (f"Updating {target_item.type} '{target_item.title}' sharing level to '{new_sharing_level}'")
        target_item.sharing.sharing_level = new_sharing_level
    return


def propagate_field_infos (source_field_infos, target_field_infos, target_feature_layer_manager):
    source_fields = {f['name']: f for f in source_field_infos}
    target_fields = {f['name']: f for f in target_field_infos}
    deletes = [target_fields[f] for f in target_fields.keys() if f not in source_fields.keys()]
    adds = [source_fields[f] for f in source_fields.keys() if f not in target_fields.keys()]
    edits = [source_fields[f] for f in source_fields.keys() if f in target_fields.keys() and source_fields[f] != target_fields[f]]
    if len(adds) > 0:
        logger.debug (f"Adding fields to layer/table {target_feature_layer_manager.properties.name}: {adds}")
        target_feature_layer_manager.add_to_definition({"fields": adds})
    if len(deletes)> 0:
        logger.debug (f"Deleting fields from layer/table {target_feature_layer_manager.properties.name}: {deletes}")
        target_feature_layer_manager.delete_from_definition({"fields": deletes})
    if len(edits) > 0:
        logger.debug (f"Editing fields in layer/table {target_feature_layer_manager.properties.name}: {edits}")     
        target_feature_layer_manager.update_definition({"fields": edits})
    return
