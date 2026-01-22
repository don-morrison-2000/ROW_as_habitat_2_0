import arcpy
import os, sys
from arcgis.gis import GIS
import row.constants as c
import row.utils
import row.registry
import keyring
from datetime import datetime as dt, UTC
import time

import row.logger
logger = row.logger.get('row_log')


def login_as_admin ():
    return GIS("https://www.arcgis.com", c.AGOL_OWNER_ID, keyring.get_password('AGOL', c.AGOL_OWNER_ID))


def is_folder_exists (gis, folder_name):
    return folder_name in [f['title'] for f in gis.users.me.folders]


def get_group_from_registry_tag (gis, org_id, tag):
    groups = [g for g in gis.groups.search(f"owner:{c.AGOL_OWNER_ID} AND tags:{org_id.lower()},{tag}")]
    if len(groups) == 0:
        return None
    elif len(groups) == 1:
        return groups[0]
    else:
        raise Exception ("{org_id.lower()} and {tag} tags used in multiple groups: {groups}")


def get_item_registry_tag (item):
    registered_tags = [r['tag'] for r in row.registry.ORG_ITEMS_REGISTRY]
    tags = [t for t in item.tags if t in registered_tags]
    if len(tags) == 0:
        return None
    elif len(tags) == 1:
        return tags[0]
    else:
        raise Exception ("{item} has multiple registered tags: {tags}") 
    

def get_group_registry_tag (group):
    registered_tags = [r['tag'] for r in row.registry.ORG_GROUPS_REGISTRY]
    group_tags = [g for g in group.tags if g in registered_tags]
    if len(group_tags) == 0:
        return None
    elif len(group_tags) == 1:
        return group_tags[0]
    else:
        raise Exception ("{item} has multiple registered group tags: {group_tags}")        


def get_item_registry_spec (item):
    registered_tag = get_item_registry_tag (item)
    if registered_tag is None:
        raise Exception (f"Item {item.type} '{item.title}' has no registered item tag. Current tags: {item.tags}")
    else:
        return [r for r in row.registry.ORG_ITEMS_REGISTRY if r['tag'] == registered_tag][0]
    

def get_registered_items (gis, org_id):  
    return [i for i in gis.users.me.items(folder=org_id, max_items=1000) if get_item_registry_tag(i) is not None]


def get_org_spec (org_id):
    return c.ORGS[org_id]        


# Add an entry to the list
def log_admin_event (gis, event, org_id, notes=None, result=None):
    tbl = row.utils.get_layer_from_tag (gis, c.ADMIN_ITEM_TAG_ADMIN_EVENTS, 0)
    new_record = {'attributes': {'Org_ID': org_id, 'Event': event, 'UserName': gis.users.me.username, 'DateTime': dt.now(UTC), 'Notes': notes}}
    return tbl.edit_features(adds=[new_record])['addResults'][0]['objectId']


# Set the results field    
def log_admin_event_result (gis, oid, result):
    tbl = row.utils.get_layer_from_tag (gis, c.ADMIN_ITEM_TAG_ADMIN_EVENTS, 0)
    tbl.edit_features(updates=[{'attributes': {'objectId': oid, 'Result': result[:255]}}])
    return


def is_system_index (index_spec):
    if index_spec.name.startswith('PK__'):
        return True  # Primary Key
    if index_spec.indexType == 'Spatial':
        return True # One on only spatial index
    if index_spec.fields in ['GlobalID', 'Shape__Length', 'created_date', 'created_user', 'last_edited_date', 'last_edited_user']:
        return True # Prebuilt system indexes
    return False

# Recursively scan all json nodes replacing any strings that show up in the
# list of replacement 2-tuples (old,new)
def fixup_json (json_node, replacements, path):
    if type(json_node).__name__ == 'dict':
        for k in json_node.keys():
            path.append(k)
            json_node[k] = fixup_json(json_node[k], replacements, path)
            path.pop()
    elif type(json_node).__name__ == 'list':
        for i in list(range(0,len(json_node))):
            path.append(i)
            json_node[i] = fixup_json(json_node[i], replacements, path)
            path.pop()
    elif type(json_node).__name__ == 'str':
        for r_before, r_after  in replacements:
            json_node_orig = json_node
            json_node = json_node.replace(r_before, r_after)
            if json_node_orig != json_node:
                logger.debug (f"Path  : {path}")
                logger.debug (f"Before: {r_before}")
                logger.debug (f"After : {r_after}")
    return json_node


def wait_on_job (job):
    while not job.done():
        time.sleep(0.1)
    return job.result()
