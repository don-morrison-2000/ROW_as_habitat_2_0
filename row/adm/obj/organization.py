import arcpy
import os, sys
from arcgis.gis import GIS
import row.utils
import row.constants as c
import row.adm.adm_utils
import row.adm.obj.group
import row.adm.obj.feature_layer
import row.adm.obj.web_map
import row.adm.obj.web_experience

import row.logger
logger = row.logger.get('row_log')



TYPE_TO_OBJ = {'Feature Service': row.adm.obj.feature_layer,
               'Web Map': row.adm.obj.web_map,
               'Web Experience': row.adm.obj.web_experience,
}

    
def create (gis, target_org_id):
    logger.info (f"{target_org_id}: Creating new organization")
    source_items = row.adm.adm_utils.get_registered_items (gis, c.MODEL_ORG_ID)

    target_folder = gis.content.folders.get(folder=target_org_id, owner=c.AGOL_OWNER_ID)
    if target_folder is not None:
        logger.debug (f"{target_org_id}: Deleting exiting folder and content")
        target_folder.delete(True)

    logger.debug (f"{target_org_id}: Creating folder:")    
    gis.content.folders.create(target_org_id)

    for source_item in source_items:
        TYPE_TO_OBJ[source_item.type].create(gis, source_item, target_org_id)

    update (gis, target_org_id)

    return


def update (gis, target_org_id, item_registration_tags=[]):
    logger.info (f"{target_org_id}: Updating organization")
    source_items = row.adm.adm_utils.get_registered_items (gis, c.MODEL_ORG_ID)

    # Create org groups
    row.adm.obj.group.update_org_group_properties (gis, c.MODEL_ORG_ID, target_org_id)

    # Get the strings the need to be replaced when propagating the items from the model organization
    text_replacement_list = __get_text_replacement_list(gis, c.MODEL_ORG_ID, source_items, target_org_id)
    logger.debug (f"{target_org_id}: Text replacments: {text_replacement_list}")

    # Update the target org items
    source_item_subset = [row.utils.get_item(gis, t, c.MODEL_ORG_ID) for t in item_registration_tags]
    for source_item in [i for i in (source_items if len(source_item_subset) == 0 else source_item_subset)]:
        target_item = row.utils.get_item(gis, row.adm.adm_utils.get_item_registry_tag(source_item), target_org_id)
        if target_item is None:
            target_item =TYPE_TO_OBJ[source_item.type].create(gis, source_item, target_org_id)
        TYPE_TO_OBJ[source_item.type].update(gis, source_item, target_item, c.MODEL_ORG_ID, target_org_id, text_replacement_list)
    
        # Update item sharing
        row.adm.obj.group.update_item_group_sharing (gis, target_org_id, target_item)

    __delete_extraneous_items (gis, target_org_id)

    return

def delete (target_org_id):
    logger.info (f"{target_org_id}: Deleting organization")  




# Returns a list of text changes that are needed for item propagation from the model organization
def __get_text_replacement_list (gis, source_org_id, source_items, target_org_id):
    replacement_list = [
                        (source_org_id, target_org_id),
                        (c.ORGS[source_org_id]['name'], c.ORGS[target_org_id]['name']) 
                    ]

    target_items = [i for i in gis.users.me.items(folder=target_org_id, max_items=1000)]
    for source_item in source_items:
        tag = row.adm.adm_utils.get_item_registry_tag(source_item)
        if tag is not None:
            target_match_items = [i for i in target_items if row.adm.adm_utils.get_item_registry_tag(i) == tag]
            if len(target_match_items) == 1:
                replacement_list.append ( (source_item.id, target_match_items[0].id) )
                replacement_list.append ( (source_item.url, target_match_items[0].url) ) if None not in [source_item.url, target_match_items[0].url] else None
            elif len(target_match_items) > 1:
                raise Exception (f"Multiple items tagged with '{tag}': {target_match_items}")
    return replacement_list


def __delete_extraneous_items (gis, target_org_id):
    target_folder_items = [i for i in gis.users.me.items(folder=target_org_id, max_items=1000)]
    delete_items = [i for i in target_folder_items if row.adm.adm_utils.get_item_registry_tag(i) is None]
    for delete_item in delete_items:
        logger.debug (f"Deleting: {delete_item}")
        gis.delete_item.delete(permanent=True)
    return


if __name__ == '__main__':
    logger.info ("Logging to %s" % row.logger.LOG_FILE)
    gis = row.adm.adm_utils.login_as_admin ()
    update(gis, 'ROW2_DEVOrgB', ['row2item_org_webexperience'])

