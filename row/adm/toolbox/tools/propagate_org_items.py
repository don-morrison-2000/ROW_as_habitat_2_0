import arcpy
import os, sys
from arcgis.gis import GIS
import arcgis.features
from  arcgis.gis import SharingLevel
import row.adm.utils
import row.usr.logger
logger = row.usr.logger.get('row_log')
import json


import row.usr.constants as c


    
# Recursively scan all json nodes replacing any strings that show up in the
# list of replacement 2-tuples (old,new)
def __fixup_item_spec (json_node, replacements, path):
    if type(json_node).__name__ == 'dict':
        for k in json_node.keys():
            path.append(k)
            json_node[k] = __fixup_item_spec(json_node[k], replacements, path)
            path.pop()
    elif type(json_node).__name__ == 'list':
        for i in list(range(0,len(json_node))):
            path.append(i)
            json_node[i] =__fixup_item_spec(json_node[i], replacements, path)
            path.pop()
    elif type(json_node).__name__ == 'str':
        for r_before, r_after  in replacements:
            json_node_orig = json_node
            json_node = json_node.replace(r_before, r_after)
            if json_node_orig != json_node:
                logger.debug (f"{r_before} changed to {r_after}. Path: {path}")
    return json_node






# Maps clone tag to a source item a target item
def get_clone_tag_map (source_items, target_items):
    clone_tag_map = dict()
    for source_item in source_items:
        tag = row.adm.utils.get_clone_tag(source_item)
        if tag is not None:
            target_match_items = [t for t in target_items if row.adm.utils.get_clone_tag(t) == tag]
            if len(target_match_items) == 1:
                clone_tag_map[tag] = (source_item.id, target_match_items[0].id)
            elif len(target_match_items) > 1:
                raise Exception (f"Multiple items tagged with '{tag}': {target_match_items}")
    return clone_tag_map


def __create_new_item (gis, source_item, folder):
    logger.info (f"Creating new {source_item.type} item")
    if source_item.type == 'Feature Service':
        new_item = gis.content.clone_items([source_item], folder=folder, search_existing_items=False)[0]
        for new_item_layer in new_item.layers + new_item.tables:
            new_item_layer.manager.truncate()
    elif source_item.type in ['Web Map', 'Dashboard', 'Web Experience']:
        #cloned_target_item = source_item.copy()
        new_item = gis.content.add(item_properties={'title': 'tbd', 'type': source_item.type}, folder=folder)
    else:
        raise Exception (f"Item type {source_item.type} not yet implemented")
    return new_item



def __update_item_resource_files (source_item, target_item):
    logger.debug (f"Updating {source_item.type} resource file")    
    target_item.resources.remove()
    for r in source_item.resources.list():
        local_copy = os.path.join(arcpy.env.scratchFolder, os.path.basename(r['resource']))
        source_item.resources.get(r['resource'], try_json=False, out_folder=arcpy.env.scratchFolder)
        if r['resource'] == 'config/config.json':
            with open(local_copy, 'w') as local_copy_fp:
                json.dump(target_item.get_data(), local_copy_fp)
        target_item.resources.add(file=local_copy, folder_name=os.path.dirname(r['resource']),  file_name=os.path.basename(r['resource']), access=r['access'])
    return


def __propagate_field_infos (source_field_infos, target_field_infos, target_feature_layer_manager):
    source_fields = {f['name']: f for f in source_field_infos}
    target_fields = {f['name']: f for f in target_field_infos}
    deletes = [target_fields[f] for f in target_fields.keys() if f not in source_fields.keys()]
    adds = [source_fields[f] for f in source_fields.keys() if f not in target_fields.keys()]
    edits = [source_fields[f] for f in source_fields.keys() if f in target_fields.keys() and source_fields[f] != target_fields[f]]
    if len(adds) > 0:
        logger.info (f"Adding fields to layer/table {target_feature_layer_manager.properties.name}: {adds}")
        target_feature_layer_manager.add_to_definition({"fields": adds})
    if len(deletes)> 0:
        logger.info (f"Deleting fields from layer/table {target_feature_layer_manager.properties.name}: {deletes}")
        target_feature_layer_manager.delete_from_definition({"fields": deletes})
    if len(edits) > 0:
        logger.info (f"Editing fields in layer/table {target_feature_layer_manager.properties.name}: {edits}")     
        target_feature_layer_manager.update_definition({"fields": edits})
    return



def __propagate_feature_layer_collection_properties (source_flc_manager, target_flc_manager):
    # Propagate service-wide settings - those found on the Setting tab of the item. Note that some setting on that tab ARE
    # layer-specific such as: 1) Manager geometry updates 2) Optimize layer drawing and 3) Manage indexes)
    exclude_properties = ['adminServiceInfo', 'description', 'layers', 'tables']
    include_properties = [p for p in source_flc_manager.properties.serviceAdminOperationsOptions.updateDefinition if p not in exclude_properties]
    source_properties = {p: source_flc_manager.properties[p] for p in source_flc_manager.properties if p in include_properties}
    target_properties = {p: target_flc_manager.properties[p] for p in target_flc_manager.properties if p in include_properties} 
    edits = {p: source_properties[p] for p in source_properties.keys() if p not in target_properties.keys() or source_properties[p] != target_properties[p]}
    if len(edits) > 0:
        logger.info (f"Editing properties in feature layer collection {target_flc_manager.url}. New values: {edits}")  
        target_flc_manager.update_definition(edits)
    return

def __is_system_index (index_spec):
    if index_spec.name.startswith('PK__'):
        return True  # Primary Key
    if index_spec.indexType == 'Spatial':
        return True # One on only spatial index
    if index_spec.fields in ['GlobalID', 'Shape__Length', 'created_date', 'created_user', 'last_edited_date', 'last_edited_user']:
        return True # Prebuilt system indexes
    return False

def __propagate_feature_layer_indexes (source_fl_manager, target_fl_manager):
    # Propagate layer-specific indexes
    source_indexes = {i['name']: i for i in source_fl_manager.properties.indexes}
    target_indexes = {i['name']: i for i in target_fl_manager.properties.indexes}
    deletes = [{'name': target_indexes[i].name} for i in target_indexes.keys() if i not in source_indexes.keys() and not __is_system_index(target_indexes[i])]
    adds = [dict(source_indexes[i]) for i in source_indexes.keys() if i not in target_indexes.keys() and not __is_system_index(source_indexes[i])]
    edits = [dict(source_indexes[i]) for i in source_indexes.keys() if i in target_indexes.keys() and source_indexes[i] != target_indexes[i] and not __is_system_index(source_indexes[i])]
    if len(deletes)> 0:
        logger.info (f"Deleting indexes from layer/table {target_fl_manager.properties.name}: {deletes}")
        target_fl_manager.delete_from_definition({"indexes": deletes})
    if len(adds) > 0:
        logger.info (f"Adding indexes to layer/table {target_fl_manager.properties.name}: {adds}")
        target_fl_manager.add_to_definition({"indexes": adds})
    if len(edits) > 0:
        logger.info (f"Editing indexes in layer/table {target_fl_manager.properties.name}: {edits}")     
        target_fl_manager.update_definition({"indexes": edits})



def __update_feature_service (source_item, target_item):
    logger.info (f"Updating service for {target_item.type} '{target_item.title}'")
    source_flc = arcgis.features.FeatureLayerCollection(source_item.url, gis)
    target_flc = arcgis.features.FeatureLayerCollection(target_item.url, gis)
    __propagate_feature_layer_collection_properties (source_flc.manager, target_flc.manager)

    for i in range(0,len(source_item.layers)):
        __propagate_feature_layer_indexes (source_item.layers[i].manager, target_item.layers[i].manager)
        __propagate_field_infos (source_item.layers[i].properties['fields'], target_item.layers[i].properties['fields'], target_item.layers[i].manager)
    for i in range(0,len(source_item.tables)):        
        __propagate_field_infos (source_item.tables[i].properties['fields'], target_item.tables[i].properties['fields'], target_item.tables[i].manager)

    return




def __update_item_sharing_level (gis, target_item, target_org_id):
    org_spec = row.adm.utils.get_org_spec (target_org_id)
    item_spec = row.adm.utils.get_item_registry_spec (target_item)
    if item_spec['allow_extended_sharing']:
        new_sharing_level = org_spec['extended_sharing_level']
    else:
        new_sharing_level = SharingLevel.PRIVATE
    if target_item.sharing.sharing_level != new_sharing_level:
        logger.info (f"Updating {target_item.type} '{target_item.title}' sharing level to '{new_sharing_level}'")
        target_item.sharing.sharing_level = new_sharing_level
    return


def __update_item_group_sharing_level (gis, target_org_id, target_item):

    for group_spec in c.GROUP_SPECS:
        group = row.adm.utils.get_org_group_from_tag (gis, target_org_id, group_spec['tag'])
        if group is None:
            title = group_spec['title'].replace('!ORG_ID!', target_org_id).replace('!ORG_NAME!', target_org_id)
            tags = f"{c.GROUP_TAG_ROOT}{group_spec['tag']}, {target_org_id}"
            description=group_spec['description'].replace('!ORG_ID!', target_org_id).replace('!ORG_NAME!', target_org_id)
            logger.info (f"Creating {target_org_id} group '{title}'")
            group = gis.groups.create(title, tags, description)

    current_org_groups = {g.id: g for g in gis.groups.search(f"owner:ROW_Admin AND tags:{target_org_id}")}
    current_item_shares  = {g.id: g for g in target_item.sharing.groups.list()}
    sharing_tags = row.adm.utils.get_item_registry_spec(target_item)['group_sharing']
    for group_id in current_org_groups.keys():
        group_tag = row.adm.utils.get_group_tag(current_org_groups[group_id])
        if group_tag is not None:
            if group_tag not in sharing_tags and group_id in current_item_shares.keys():
                logger.info (f"Removing {target_item.type} '{target_item.title}' from group '{current_org_groups[group_id]}'")
                target_item.sharing.groups.remove(current_org_groups[group_id])
            elif group_tag in sharing_tags and group_id not in current_item_shares.keys():
                logger.info (f"Adding {target_item.type} '{target_item.title}' to group '{current_org_groups[group_id]}'")
                target_item.sharing.groups.add(current_org_groups[group_id])

    return



def run(gis, source_org_id, target_org_id):

    if not row.adm.utils.is_folder_exists (gis, target_org_id):
        logger.info (f"Creating folder: {target_org_id}")
        gis.content.folders.create(target_org_id)

    source_items = [i for i in gis.users.me.items(folder=source_org_id, max_items=1000)]
    target_items = [i for i in gis.users.me.items(folder=target_org_id, max_items=1000)]

    clone_tag_map = get_clone_tag_map (source_items, target_items)

    text_replacements = [(source_org_id, target_org_id), (c.ORGS[source_org_id]['name'], c.ORGS[target_org_id]['name'])]

    for source_item in [i for i in source_items if row.adm.utils.get_clone_tag(i) is not None]:
        clone_tag = row.adm.utils.get_clone_tag(source_item)

        target_match_items = [i for i in target_items if row.adm.utils.get_clone_tag(i) == clone_tag]
        if len(target_match_items) == 0:
            target_item = __create_new_item (gis, source_item, target_org_id)
            clone_tag_map[clone_tag] = (source_item.id, target_item.id)
        elif len(target_match_items) == 1:
            target_item = target_match_items[0]
            if source_item.type == 'Feature Service':
                __update_feature_service (source_item, target_item)
        else:
            raise Exception (f"{target_org_id} has duplicate clone tags: {target_match_items}")
        
        target_item.update({
            'title':        __fixup_item_spec (source_item.title, text_replacements, []), 
            'snippet':      __fixup_item_spec (source_item.snippet, text_replacements, []), 
            'description':  __fixup_item_spec (source_item.description, text_replacements, []),
            'tags':         [clone_tag, target_org_id.lower()], 
            'typeKeywords': source_item.typeKeywords,
            'categories':   source_item.categories,
            })

        text_replacements += [(source_item.id, target_item.id)]
        text_replacements += [(source_item.url, target_item.url)] if None not in [source_item.url, target_item.url] else []

    for source_item_id, target_item_id  in clone_tag_map.values():
        source_item = gis.content.get(source_item_id)
        target_item = gis.content.get(target_item_id)
        logger.info (f"Updating {target_item.type} '{target_item.title}'")
        target_item.update({'text': __fixup_item_spec (source_item.get_data(), [r for r in text_replacements if r[0] != r[1]], [])})

        __update_item_resource_files (source_item, target_item)

        __update_item_sharing_level (gis, target_item, target_org_id)

        __update_item_group_sharing_level (gis, target_org_id, target_item)

    delete_items = [i for i in target_items if i.id not in [id[1] for id in clone_tag_map.values()]]
    for delete_item in delete_items:
        logger.info (f"Deleting: {delete_item}")
        delete_item.delete(permanent=True)

    return



if __name__ == '__main__':
    SOURCE_SDE_ORG = c.MODEL_ORG_ID
    TARGET_AGOL_ORG = 'ROW2_DEVOrgB'

    logger.info ("Logging to %s" % row.usr.logger.LOG_FILE)
    gis = row.adm.utils.login_as_admin ()

    #run(gis, SOURCE_SDE_ORG, TARGET_AGOL_ORG)
    run (gis, SOURCE_SDE_ORG, TARGET_AGOL_ORG)