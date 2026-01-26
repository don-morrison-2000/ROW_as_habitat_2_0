import arcpy
import os, sys
from arcgis.gis import GIS
from  arcgis.gis import SharingLevel
import row.adm.adm_utils
import row.logger
logger = row.logger.get('row_log')


import row.constants as c
import row.registry


GROUP_DISPLAY_SETTINGS = {  'Application':      'apps',
                            'CSV':              'files',
                            'Web Map':          'maps',
                            'Layer':            'layers',
                            'Web Scene':        'scenes',
                            'Locator Package':  'tools'
               }

def create(gis, source_group, target_org_id):
    tag = row.adm.adm_utils.get_registry_tag_from_group (source_group)
    target_group = row.adm.adm_utils.get_group_from_registry_tag (gis, target_org_id, tag)
    if target_group is None:
        logger.info (f"{target_org_id}: Creating new group item with tag {tag}")
        target_group = gis.groups.create(title=f"{tag},{target_org_id.lower()}", tags=f"{tag}, {target_org_id.lower()}", description='tbd', users_update_items=False)
    return target_group



def update (gis, source_group, target_group, source_org_id, target_org_id):
    source_org_name = row.adm.adm_utils.get_org_spec(source_org_id)['name']
    target_org_name = row.adm.adm_utils.get_org_spec(target_org_id)['name']
    title = source_group.title.replace(source_org_id, target_org_id).replace(source_org_name,target_org_name)

    logger.info (f"{target_org_id}: Updating group '{title}'")
    target_group.update (
        title = title,
        description = source_group.title.replace(source_org_id, target_org_id).replace(source_org_name,target_org_name) if source_group.description is not None else '',
        snippet  = source_group.snippet.replace(source_org_id, target_org_id).replace(source_org_name,target_org_name) if source_group.snippet is not None else '',
        is_invitation_only = source_group.isInvitationOnly,
        sort_field = source_group.sortField,
        sort_order = source_group.sortOrder, 
        is_view_only = source_group.isViewOnly, 
        #max_file_size = source_group.maxFileSize, 
        #users_update_items = source_group.users_update_items, 
        #clear_empty_fields = source_group.clear_empty_fields, 
        display_settings = GROUP_DISPLAY_SETTINGS[source_group.displaySettings['itemTypes']] if source_group.displaySettings['itemTypes'] in GROUP_DISPLAY_SETTINGS.keys() else 'all', 
        #is_open_data = source_group.is_open_data, 
        #leaving_disallowed = source_group.leaving_disallowed, 
        #member_access = source_group.member_access, 
        hidden_members = source_group.hiddenMembers, 
        #membership_access = source_group.is_open_data, 
        autojoin = source_group.autoJoin)
    return




# def update_org_group_properties (gis, source_org_id, target_org_id):
#     for tag in [g['tag'] for g in row.registry.ORG_GROUPS_REGISTRY]:
#         source_org_name = row.adm.adm_utils.get_org_spec(source_org_id)['name']
#         target_org_name = row.adm.adm_utils.get_org_spec(target_org_id)['name']

#         source_group = row.adm.adm_utils.get_group_from_registry_tag (gis, source_org_id, tag)
#         target_group = row.adm.adm_utils.get_group_from_registry_tag (gis, target_org_id, tag)
#         title = source_group.title.replace(source_org_id, target_org_id).replace(source_org_name,target_org_name)
#         if target_group is None:
#             tags = f"{tag}, {target_org_id.lower()}"
#             logger.debug (f"{target_org_id}: Creating group '{title}'")
#             target_group = gis.groups.create(title='tbd', tags=tags, description='tbd', users_update_items=False)
 
#         logger.debug (f"{target_org_id}: Updating group '{title}'")
#         target_group.update (
#             title = title,
#             description = source_group.title.replace(source_org_id, target_org_id).replace(source_org_name,target_org_name) if source_group.description is not None else '',
#             snippet  = source_group.snippet.replace(source_org_id, target_org_id).replace(source_org_name,target_org_name) if source_group.snippet is not None else '',
#             is_invitation_only = source_group.isInvitationOnly,
#             sort_field = source_group.sortField,
#             sort_order = source_group.sortOrder, 
#             is_view_only = source_group.isViewOnly, 
#             #max_file_size = source_group.maxFileSize, 
#             #users_update_items = source_group.users_update_items, 
#             #clear_empty_fields = source_group.clear_empty_fields, 
#             display_settings = GROUP_DISPLAY_SETTINGS[source_group.displaySettings['itemTypes']] if source_group.displaySettings['itemTypes'] in GROUP_DISPLAY_SETTINGS.keys() else 'all', 
#             #is_open_data = source_group.is_open_data, 
#             #leaving_disallowed = source_group.leaving_disallowed, 
#             #member_access = source_group.member_access, 
#             hidden_members = source_group.hiddenMembers, 
#             #membership_access = source_group.is_open_data, 
#             autojoin = source_group.autoJoin)
#     return
