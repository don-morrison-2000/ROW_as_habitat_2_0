import arcpy
import os, sys
from arcgis.gis import GIS
import row.usr.logger
logger = row.usr.logger.get('row_log')
import keyring

import row.usr.constants as c


def login_as_admin ():
    return GIS("https://www.arcgis.com", c.AGOL_OWNER_ID, keyring.get_password('AGOL', c.AGOL_OWNER_ID))


def is_folder_exists (gis, folder_name):
    return folder_name in [f['title'] for f in gis.users.me.folders]


def get_org_group_from_tag (gis, org_id, tag):
    #groups = [g for g in gis.users.me.groups if tag in g.tags and org_id in g.tags]
    groups = [g for g in gis.groups.search(f"owner:ROW_Admin AND tags:{org_id.lower()},{tag}")]
    if len(groups) == 0:
        return None
    elif len(groups) == 1:
        return groups[0]
    else:
        raise Exception ("{org_id.lower()} and {tag} tags used in multiple groups: {groups}")


def get_clone_tag (item):
    clone_tags = [t for t in item.tags if t.startswith(c.ITEM_TAG_ROOT)]
    if len(clone_tags) == 0:
        return None
    elif len(clone_tags) == 1:
        return clone_tags[0]
    else:
        raise Exception ("{item} has duplicate item clone tags: {target_items}") 
    

def get_group_tag (group):
    group_tags = [g for g in group.tags if g.startswith(c.GROUP_TAG_ROOT)]
    if len(group_tags) == 0:
        return None
    elif len(group_tags) == 1:
        return group_tags[0]
    else:
        raise Exception ("{item} has duplicate group tags: {target_items}")        



def get_item_registry_spec (item):
    tag = [t for t in item.tags if t.startswith(c.ITEM_TAG_ROOT)][0]
    item_specs =  [r for r in c.ORG_ITEMS_REGISTRY if r['tag'] == tag]
    if len(item_specs) == 1:
        return item_specs[0]
    elif len(item_specs) == 0:
        raise Exception (f"Add tag with '{c.ITEM_TAG_ROOT}' prefix for {item.type} '{item.title}' in the item registry.")
    else:
        raise Exception (f"{item.type} '{item.title}' has multiple propagation tags: {item.tags}")



def get_org_spec (org_id):
    return c.ORGS[org_id]        