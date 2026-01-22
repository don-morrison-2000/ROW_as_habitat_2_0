import arcpy
import os, sys
from arcgis.gis import GIS
import row.constants as c
import row.adm.adm_utils
import row.adm.obj.item
import json

import row.logger
logger = row.logger.get('row_log')


def create (gis, source_item, target_org_id):
    tag = row.adm.adm_utils.get_item_registry_tag(source_item)
    logger.info (f"{target_org_id}: Creating new {source_item.type} item with tag {tag}")
    # new_item = gis.content.add(item_properties={'title': 'tbd', 'type': source_item.type, 'tags': f"{tag},{target_org_id.lower()}"}, folder=target_org_id)
    item_properties = {
        "title": "tbd",
        "tags": f"{tag},{target_org_id.lower()}",
        "text": '{}',
        "type": source_item.type
    }
    new_item = row.adm.adm_utils.wait_on_job (gis.content.folders.get(target_org_id, c.AGOL_OWNER_ID).add(item_properties))
    return new_item


def update(gis, source_item, target_item, source_org_id, target_org_id, replacement_list):
    logger.info (f"{target_org_id}: Updating {source_item.type} item '{source_item.title}'")
    row.adm.obj.item.propagate_item(gis, source_item, target_item, source_org_id, target_org_id, replacement_list)

    # Copy the published json to the draft version (config/config.json resource file) 
    logger.debug (f"{target_org_id}: Updating resource config.json (draft version)")
    local_copy = os.path.join(arcpy.env.scratchFolder, 'config.json')
    with open(local_copy, 'w') as local_copy_fp:
        json.dump(target_item.get_data(), local_copy_fp)
    target_item.resources.update(file=local_copy, folder_name='config',  file_name='config.json')
    return