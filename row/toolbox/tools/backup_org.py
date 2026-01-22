import arcpy
import os, sys
from arcgis.gis import GIS
import row.constants as c
import row.adm.adm_utils
import row.logger
logger = row.logger.get('row_log')
import keyring
from datetime import datetime as dt



def run (gis, org_id, is_schema_only):

    org_items = [i for i in gis.users.me.items(folder=org_id)]

    target_folder_name = f"{org_id}_BACKUP_{dt.now().strftime('%Y-%m-%d_%H-%M-%S')}"

    if row.adm.adm_utils.is_folder_exists (target_folder_name):
        logger.info (f"Deleting folder and contents: {target_folder_name}")
        target_folder_id = [f['id'] for f in gis.users.me.folders if f['title'] == target_folder_name][0]
        gis.content.delete_folder(target_folder_id)

    
    logger.info (f"Creating folder: {target_folder_name}")
    target_folder_id = gis.content.folders.create(target_folder_name)

    for org_item in org_items:
        try:
            logger.info (f"Cloning: {org_item.type} '{org_item.title}'")
            cloned_items = gis.content.clone_items([org_item], folder=target_folder_name, search_existing_items=True)
        except:
             logger.info ("Failed")

    return



if __name__ == '__main__':
    ORG_ID = c.MODEL_ORG_ID
    SCHEME_ONLY = True
    
    logger.info ("Logging to %s" % row.logger.LOG_FILE)
    gis = GIS("https://www.arcgis.com", c.AGOL_OWNER_ID, keyring.get_password('AGOL', c.AGOL_OWNER_ID))

    
    run (gis, ORG_ID, SCHEME_ONLY)