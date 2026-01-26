

import row.constants as c

def get_item_from_registry_tag (gis, registry_tag, org_id=None):
    expected_tags = [registry_tag] + ([org_id.lower()] if org_id is not None else [])
    query_string = f"owner:{c.AGOL_OWNER_ID} AND tags:{registry_tag}" if org_id is None else f"owner:{c.AGOL_OWNER_ID} AND tags:{','.join(expected_tags)}"
    
    items = [i for i in gis.content.search(query=query_string, max_items=-1) if i.owner == c.AGOL_OWNER_ID and set(expected_tags).issubset(set(i.tags))]
    if len (items) == 0:
        return None
    elif len (items) == 1:
        return items[0]
    else:
        raise Exception (f"{expected_tags}  tags used in multiple items: {items} {[i.id for i in items]}")
    return


def get_layer (gis, item, layer_idx):
    layer = [l for l in item.layers + item.tables if l.properties.id == layer_idx]
    if len(layer) == 1:
        return layer[0]
    raise Exception (f"Could not find layer '{item.type}' in {item.type} '{item.title}'")


def get_layer_from_tag (gis, registry_tag, layer_idx, org_id=None):
    item = get_item_from_registry_tag (gis, registry_tag, org_id)
    return get_layer (gis, item, layer_idx)

