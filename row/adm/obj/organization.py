import arcpy
import os, sys
from arcgis.gis import GIS
import row.utils
import row.registry
import row.constants as c
import row.adm.adm_utils
import row.adm.obj.group
import row.adm.obj.feature_layer
import row.adm.obj.web_map
import row.adm.obj.web_experience

import datetime as dt


import row.logger
logger = row.logger.get('row_log')


MODEL_CLONE_FOLDER_ROOT = f"{c.MODEL_ORG_ID}_Clone_"
MODEL_CLONE_FOLDER_RETENTION_MAX = 2

TYPE_TO_OBJ = {'Feature Service': row.adm.obj.feature_layer,
               'Web Map': row.adm.obj.web_map,
               'Web Experience': row.adm.obj.web_experience,
}

    
def create (gis, target_org_id):
    logger.info (f"{target_org_id}: Creating new organization")

    target_folder = gis.content.folders.get(folder=target_org_id, owner=c.AGOL_OWNER_ID)
    if target_folder is not None:
        raise Exception ("Organization folder {target_org_id} already exists")

    logger.debug (f"{target_org_id}: Creating folder")    
    gis.content.folders.create(target_org_id)

    for source_group in row.adm.adm_utils.get_registered_groups (gis, c.MODEL_ORG_ID):
        row.adm.obj.group.create(gis, source_group, target_org_id)

    for source_item in row.adm.adm_utils.get_registered_items (gis, c.MODEL_ORG_ID):
        TYPE_TO_OBJ[source_item.type].create(gis, source_item, target_org_id)

    update (gis, target_org_id, [r['tag'] for r in row.registry.ORG_ITEMS_REGISTRY], [r['tag'] for r in row.registry.ORG_GROUPS_REGISTRY])

    return


def update (gis, target_org_id, item_registration_tags=[], group_registration_tags=[]):
    logger.info (f"{target_org_id}: Updating organization")

    # Update org groups
    for source_group in [row.adm.adm_utils.get_group_from_registry_tag (gis, c.MODEL_ORG_ID, t) for t in group_registration_tags]:
        target_group = row.adm.adm_utils.get_group_from_registry_tag (gis, target_org_id, row.adm.adm_utils.get_registry_tag_from_group (source_group))
        if target_group is None:
            target_group = row.adm.obj.group.create(gis, source_group, target_org_id)
        row.adm.obj.group.update (gis, source_group, target_group, c.MODEL_ORG_ID, target_org_id)

    # Update the target org items
    text_replacement_list = __get_text_replacement_list(gis, c.MODEL_ORG_ID, target_org_id)
    logger.debug (f"{target_org_id}: Text replacements: {text_replacement_list}")
    for source_item in [row.utils.get_item_from_registry_tag(gis, t, c.MODEL_ORG_ID) for t in item_registration_tags]:
        target_item = row.utils.get_item_from_registry_tag(gis, row.adm.adm_utils.get_registry_tag_from_item(source_item), target_org_id)
        if target_item is None:
            target_item =TYPE_TO_OBJ[source_item.type].create(gis, source_item, target_org_id)
        TYPE_TO_OBJ[source_item.type].update(gis, source_item, target_item, c.MODEL_ORG_ID, target_org_id, text_replacement_list)

    __delete_extraneous_items (gis, target_org_id)

    return


def delete (gis, target_org_id, delete_org_record, backup_data):
    logger.info (f"{target_org_id}: Deleting organization") 

    if target_org_id == c.MODEL_ORG_ID:
        raise Exception ("Can not delete model organization") 

    for target_group in row.adm.adm_utils.get_registered_groups (gis, target_org_id):
       logger.info (f"{target_org_id}: Deleting group: {target_group.title}")
       target_group.delete()

    target_folder = gis.content.folders.get(folder=target_org_id, owner=c.AGOL_OWNER_ID)
    if target_folder is not None:
        logger.info (f"{target_org_id}: Deleting organization folder and content")
        target_folder.delete(True)



def clone_model_org_items (gis):
    # Get existing clones sorted in reverse order
    existing_clone_numbers = sorted([int(f['title'].split('_')[-1]) for f in gis.users.me.folders if f['title'].startswith(MODEL_CLONE_FOLDER_ROOT)], reverse=True)
    if len(existing_clone_numbers) == 0:
        new_clone_number = 1
    else:
        new_clone_number = existing_clone_numbers[0] + 1
    new_clone_folder_name = f"{MODEL_CLONE_FOLDER_ROOT}{new_clone_number}"

    logger.info (f"Cloning model organization items to folder: {new_clone_folder_name}")
    target_folder_id = gis.content.folders.create(new_clone_folder_name)

    cloned_items = []
    for org_item in row.adm.adm_utils.get_registered_items (gis, c.MODEL_ORG_ID):
        try:
            logger.info (f"Cloning: {org_item.type} '{org_item.title}'")
            cloned_items += gis.content.clone_items([org_item], folder=new_clone_folder_name, search_existing_items=True)
        except:
             logger.info ("Failed")

    for cloned_item in cloned_items:
        cloned_item.update({'typeKeywords'  : [k for k  in cloned_item.typeKeywords if not k.startswith('source-')],
                            'tags'          : [t.replace(c.MODEL_ORG_ID.lower(), new_clone_folder_name.lower()) for t in cloned_item.tags],
                        }) 

    if len(existing_clone_numbers) > MODEL_CLONE_FOLDER_RETENTION_MAX-1:
        for i in range (MODEL_CLONE_FOLDER_RETENTION_MAX-1, len(existing_clone_numbers)):
            logger.info (f"Deleting clone {existing_clone_numbers[i]}")
            clone_folder = row.adm.adm_utils.get_folder(gis, f"{MODEL_CLONE_FOLDER_ROOT}{existing_clone_numbers[i]}")
            clone_folder.delete(True)
    

    return




# Returns a list of text changes that are needed for item propagation from the model organization
def __get_text_replacement_list (gis, source_org_id, target_org_id):
    replacement_list = [
                        (c.ORGS[source_org_id]['name'], c.ORGS[target_org_id]['name']),
                        (source_org_id, target_org_id),
                    ]

    source_items = row.adm.adm_utils.get_registered_items (gis, source_org_id)
    target_items = [i for i in gis.users.me.items(folder=target_org_id, max_items=1000)]
    for source_item in source_items:
        tag = row.adm.adm_utils.get_registry_tag_from_item(source_item)
        if tag is not None:
            target_match_items = [i for i in target_items if row.adm.adm_utils.get_registry_tag_from_item(i) == tag]
            if len(target_match_items) == 1:
                replacement_list.append ( (source_item.id, target_match_items[0].id) )
                replacement_list.append ( (source_item.url, target_match_items[0].url) ) if None not in [source_item.url, target_match_items[0].url] else None
            elif len(target_match_items) > 1:
                raise Exception (f"Multiple items tagged with '{tag}': {target_match_items}")
    return replacement_list


def __delete_extraneous_items (gis, target_org_id):
    target_folder_items = [i for i in gis.users.me.items(folder=target_org_id, max_items=1000)]
    delete_items = [i for i in target_folder_items if row.adm.adm_utils.get_registry_tag_from_item(i) is None]
    for delete_item in delete_items:
        logger.debug (f"Deleting: {delete_item}")
        gis.delete_item.delete(permanent=True)
    return


if __name__ == '__main__':
    logger.info ("Logging to %s" % row.logger.LOG_FILE)
    gis = row.adm.adm_utils.login_as_admin ()

    #create (gis, 'ROW2_DEVOrgB')

    #update (gis, 'ROW2_DEVOrgB', ['row2item_org_webexperience'], [])


    # UPDATE ALL
    update (gis, 'ROW2_DEVOrgB', [r['tag'] for r in row.registry.ORG_ITEMS_REGISTRY], [r['tag'] for r in row.registry.ORG_GROUPS_REGISTRY])

    #delete (gis, 'ROW2_DEVOrgB', False, False)

    #backup (gis, 'ROW2_DEVOrgB', False)

    #clone_model_org_items(gis)
    

