import arcpy
import os, sys
from arcgis.gis import GIS
import arcgis.features
import row.constants as c
import row.adm.adm_utils
import row.adm.obj.item
import row.logger
logger = row.logger.get('row_log')


def create(gis, source_item, target_org_id):
    tag = row.adm.adm_utils.get_item_registry_tag(source_item)
    logger.info (f"{target_org_id}: Creating new {source_item.type} item with tag {tag}")
    target_item = gis.content.clone_items([source_item], folder=target_org_id, search_existing_items=False)[0]
    target_item.update( {'tags': f"{tag},{target_org_id.lower()}"} )
    for new_item_layer in target_item.layers + target_item.tables:
        new_item_layer.manager.truncate()
    return target_item


def update(gis, source_item, target_item, source_org_id, target_org_id, replacement_list):
    logger.info (f"{target_org_id}: Updating {source_item.type} item '{source_item.title}'")
    __update_feature_service (gis, source_item, target_item)
    row.adm.obj.item.propagate_item(gis, source_item, target_item, source_org_id, target_org_id, replacement_list)
    return


def __update_feature_service (gis, source_item, target_item):
    logger.debug (f"Updating service for {target_item.type} '{target_item.title}'")
    source_flc = arcgis.features.FeatureLayerCollection(source_item.url, gis)
    target_flc = arcgis.features.FeatureLayerCollection(target_item.url, gis)
    __propagate_feature_layer_collection_properties (gis, source_flc.manager, target_flc.manager)

    for i in range(0,len(source_item.layers)):
        __propagate_feature_layer_indexes (gis, source_item.layers[i].manager, target_item.layers[i].manager)
        row.adm.obj.item.propagate_field_infos (source_item.layers[i].properties['fields'], target_item.layers[i].properties['fields'], target_item.layers[i].manager)
    for i in range(0,len(source_item.tables)):        
        row.adm.obj.item.propagate_field_infos (source_item.tables[i].properties['fields'], target_item.tables[i].properties['fields'], target_item.tables[i].manager)

    return


def __propagate_feature_layer_collection_properties (gis, source_flc_manager, target_flc_manager):
    # Propagate service-wide settings - those found on the Setting tab of the item. Note that some setting on that tab ARE
    # layer-specific such as: 1) Manager geometry updates 2) Optimize layer drawing and 3) Manage indexes)
    exclude_properties = ['adminServiceInfo', 'description', 'layers', 'tables']
    include_properties = [p for p in source_flc_manager.properties.serviceAdminOperationsOptions.updateDefinition if p not in exclude_properties]
    source_properties = {p: source_flc_manager.properties[p] for p in source_flc_manager.properties if p in include_properties}
    target_properties = {p: target_flc_manager.properties[p] for p in target_flc_manager.properties if p in include_properties} 
    edits = {p: source_properties[p] for p in source_properties.keys() if p not in target_properties.keys() or source_properties[p] != target_properties[p]}
    if len(edits) > 0:
        logger.debug (f"Editing properties in feature layer collection {target_flc_manager.url}. New values: {edits}")  
        target_flc_manager.update_definition(edits)
    return



def __propagate_feature_layer_indexes (gis, source_fl_manager, target_fl_manager):
    # Propagate layer-specific indexes
    source_indexes = {i['name']: i for i in source_fl_manager.properties.indexes}
    target_indexes = {i['name']: i for i in target_fl_manager.properties.indexes}
    deletes = [{'name': target_indexes[i].name} for i in target_indexes.keys() if i not in source_indexes.keys() and not __is_system_index(target_indexes[i])]
    adds = [dict(source_indexes[i]) for i in source_indexes.keys() if i not in target_indexes.keys() and not __is_system_index(source_indexes[i])]
    edits = [dict(source_indexes[i]) for i in source_indexes.keys() if i in target_indexes.keys() and source_indexes[i] != target_indexes[i] and not __is_system_index(source_indexes[i])]
    if len(deletes)> 0:
        logger.debug (f"Deleting indexes from layer/table {target_fl_manager.properties.name}: {deletes}")
        target_fl_manager.delete_from_definition({"indexes": deletes})
    if len(adds) > 0:
        logger.debug (f"Adding indexes to layer/table {target_fl_manager.properties.name}: {adds}")
        target_fl_manager.add_to_definition({"indexes": adds})
    if len(edits) > 0:
        logger.debug (f"Editing indexes in layer/table {target_fl_manager.properties.name}: {edits}")     
        target_fl_manager.update_definition({"indexes": edits})


def __is_system_index (index_spec):
    if index_spec.name.startswith('PK__'):
        return True  # Primary Key
    if index_spec.indexType == 'Spatial':
        return True # One on only spatial index
    if index_spec.fields in ['GlobalID', 'Shape__Length', 'created_date', 'created_user', 'last_edited_date', 'last_edited_user']:
        return True # Prebuilt system indexes
    return False

