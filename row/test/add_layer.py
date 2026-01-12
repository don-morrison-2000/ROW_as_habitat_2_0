# Copy layer from one hosted feature layer to another
import keyring
from arcgis.gis import GIS

source_fc_id = '33fdf1d454ed47e59e6c49da82ea7382'
source_layer_index = 0
target_fc_id = 'ca7804bff5fa4851a081e6bca3e0e481'

gis = GIS("https://www.arcgis.com", "ROW_Admin", keyring.get_password('AGOL', "ROW_Admin"))

from arcgis.features import FeatureLayerCollection
target_fc = gis.content.get(target_fc_id)
source_fc = gis.content.get(source_fc_id )
source_fc_layer = source_fc.layers[source_layer_index]
source_fc_layer_def = dict(source_fc_layer.properties)
target_flc = FeatureLayerCollection.fromitem(target_fc)
target_flc.manager.add_to_definition({'layers': [source_fc_layer_def]})
