import os, sys
import zipfile
import arcpy
from arcgis.gis import GIS
import row.constants as c
import row.utils
import row.registry
import row.adm.adm_utils
import row.usr.usr_utils
from glob import glob
import re

import row.logger
logger = row.logger.get('row_log')

def run (gis, code_registry_spec):
    logger.info ("Logging to %s" % row.logger.LOG_FILE)
    logger.info (f"code_registry_spec: {code_registry_spec}")

    if gis is None:
        gis = row.adm.adm_utils.login_as_admin ()

    output_path = os.path.join(arcpy.env.scratchFolder, f"notebook_upload_{code_registry_spec['tag']}.zip")
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for path in code_registry_spec['files']:
            for file_path in glob(path):
                zipf.write(file_path, file_path.removeprefix(c.CODE_BASE))
    logger.info (f"Files zipped to {output_path}")

    gis_code_item = row.utils.get_item_from_registry_tag (gis, code_registry_spec['tag'])
    if gis_code_item is None:
        logger.info (f"Creating a new code item with tag '{code_registry_spec['tag']}'. Please update the title and description in ArcGIS Online")
        gis_code_item = gis.content.add(item_properties={'title': 'please give me a title', 'type': 'Code Sample', 'tags': code_registry_spec['tag']}, folder=c.SINGLETONS_FOLDER)

    update_result = gis_code_item.update(data=output_path)
    if update_result:
        logger.info (f"Successfully updated item '{gis_code_item.title}' with the new zip file.")
    else:
        logger.info ("Failed to update the item.")

    return



if __name__ == '__main__':
    logger.info ("Logging to %s" % row.logger.LOG_FILE)

    gis = row.adm.adm_utils.login_as_admin ()
    for code_spec in row.registry.CODE_ITEMS_REGISTRY:
        row.usr.usr_utils.get_desc_from_tag (gis, code_spec['tag'])
        run (gis, code_spec)    
