import row.constants as c
import row.registry
import row.usr.usr_utils
import row.utils
from arcgis.gis import GIS
import arcpy
import os
import sys
import traceback
import datetime as dt
import keyring

TOOL_NAME = 'Geoprocessing Test'

def run (gis, org_id, fl_tag):

    lf = row.usr.usr_utils.open_log_file ("row_log_file.html", TOOL_NAME)
    print (f"Logging to {lf.name}")

    # Output parameters
    log_file = {"url": lf.name}
    result = records = ''

    try:
        row.usr.usr_utils.log (lf, f"org_id: {org_id} fl_tag: {fl_tag}")

        item = row.utils.get_item_from_registry_tag (gis, row.registry.ORG_ITEM_TAG_SCORECARDS, org_id)
        test_lyr = row.utils.get_layer (gis, item, 0)
        
        records = f'ORG ID: {org_id}\n'
        for f in test_lyr.query(where='1=1', out_fields='OBJECTID, Notes', return_geometry=False):
            records += f"{f.attributes}\n"
        
        row.usr.usr_utils.log (lf,records) 
        row.usr.usr_utils.log (lf,f"'ENB_JOBID': {('ENB_JOBID' in os.environ)}")
        result = 'Success'

    except Exception as ex:
        row.usr.usr_utils.log (lf,f"Exception: {str(ex)}")
        row.usr.usr_utils.log (lf,traceback.format_exc())
        result = f"Failure: {str(ex)}"
        row.usr.usr_utils.log (lf, "Adding Warning Message")
        arcpy.AddWarning(result)

    finally:
        row.usr.usr_utils.log(lf, f"Updating tool completion {result}")
        row.usr.usr_utils.log_tool_completion (gis, result,  org_id, gis.users.me.username, TOOL_NAME)
        row.usr.usr_utils.close_log_file (lf)
        return result, records, log_file["url"]

if __name__ == '__main__':
    if "ENB_JOBID" not in os.environ:
        gis = GIS("https://www.arcgis.com", c.AGOL_OWNER_ID, keyring.get_password('AGOL', c.AGOL_OWNER_ID))
        result, records, log_file = run(gis, c.MODEL_ORG_ID, 'row2item_org_centerlines')
        print (str(result))
        print (str(records))
        print (str(log_file))

    

