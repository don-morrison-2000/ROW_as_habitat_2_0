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

# def clone_item (gis, source_item, target_folder_name, tags):
#     logger.info (f"Cloning: {source_item.type} '{source_item.title}'")
#     cloned_item = gis.content.clone_items([source_item], folder=target_folder_name, search_existing_items=True)[0]
#     cloned_item.update({'typeKeywords'  : [k for k  in cloned_item.typeKeywords if not k.startswith('source-')],
#                         'tags'          : tags,
#                     }) 
#     return cloned_item


def propagate_item (gis, source_item, target_item, source_org_id, target_org_id, replacement_list):
    logger.debug (f"{target_org_id}: Finding text replacements for {target_item.type} '{target_item.title}'")
    text_replacements = replacement_list.copy()


    logger.debug (f"{target_org_id}: Updating item header")
    target_item.update({
        'title':        row.adm.adm_utils.fixup_json (source_item.title, text_replacements, []), 
        'snippet':      row.adm.adm_utils.fixup_json (source_item.snippet, text_replacements, []), 
        'description':  row.adm.adm_utils.fixup_json (source_item.description, text_replacements, []),
        'tags':         [row.adm.adm_utils.get_registry_tag_from_item (source_item), target_org_id.lower()], 
        'typeKeywords': source_item.typeKeywords,
        'categories':   source_item.categories,
        })

    logger.debug (f"{target_org_id}: Updating item data")
    target_item.update({'text': row.adm.adm_utils.fixup_json (source_item.get_data(), [r for r in text_replacements if r[0] != r[1]], [])})

    __propagate_item_resources (gis, source_item, target_item)
    __propagate_item_sharing_level (gis, target_org_id, target_item)
    __propagate_item_group_sharing (gis, target_org_id, target_item)

    return


def __propagate_item_resources (gis, source_item, target_item):
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




def __propagate_item_sharing_level (gis, target_org_id, target_item):
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



def __propagate_item_group_sharing (gis, target_org_id, target_item):
    current_org_groups = {g.id: g for g in gis.groups.search(f"owner:ROW_Admin AND tags:{target_org_id}")}
    current_item_shares  = {g.id: g for g in target_item.sharing.groups.list()}
    sharing_tags = row.adm.adm_utils.get_item_registry_spec(target_item)['group_sharing']
    for group_id in current_org_groups.keys():
        group_tag = row.adm.adm_utils.get_registry_tag_from_group(current_org_groups[group_id])
        if group_tag is not None:
            if group_tag not in sharing_tags and group_id in current_item_shares.keys():
                logger.debug (f"{target_org_id}: Removing {target_item.type} '{target_item.title}' from group '{current_org_groups[group_id]}'")
                target_item.sharing.groups.remove(current_org_groups[group_id])
            elif group_tag in sharing_tags and group_id not in current_item_shares.keys():
                logger.debug (f"{target_org_id}: Adding {target_item.type} '{target_item.title}' to group '{current_org_groups[group_id]}'")
                target_item.sharing.groups.add(current_org_groups[group_id])

    return
