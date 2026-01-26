import arcpy
import os, sys
from arcgis.gis import GIS
from arcgis.gis import ItemProperties, ItemTypeEnum
import row.constants as c
import row.adm.adm_utils
import row.adm.obj.item
import row.logger
logger = row.logger.get('row_log')


def create (gis, source_item, target_org_id):
    tag = row.adm.adm_utils.get_registry_tag_from_item(source_item)
    logger.info (f"{target_org_id}: Creating new {source_item.type} item with tag {tag}")
    # new_item = gis.content.add(item_properties={'title': 'tbd', 'type': source_item.type, 'tags': f"{tag},{target_org_id.lower()}"}, folder=target_org_id)
    item_properties = {
        "title": f"{tag}_{target_org_id.lower()}",
        "tags": f"{tag},{target_org_id.lower()}",
        "text": '{}',
        "type": source_item.type
    }
    new_item = row.adm.adm_utils.wait_on_job (gis.content.folders.get(target_org_id, c.AGOL_OWNER_ID).add(item_properties))
    return new_item


def update(gis, source_item, target_item, source_org_id, target_org_id, replacement_list):
    logger.info (f"{target_org_id}: Updating {source_item.type} item '{source_item.title}'")
    row.adm.obj.item.propagate_item(gis, source_item, target_item, source_org_id, target_org_id, replacement_list)
    return