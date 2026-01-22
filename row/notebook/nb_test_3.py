import row.constants as c
import row.registry
import row.notebook.common
import row.utils
from arcgis.gis import GIS
import arcpy
import os
import sys
import traceback
import datetime as dt
import keyring

TOOL_NAME = 'Geoprocessing Test'

def run (gis, org_id):

    lf = row.notebook.common.open_log_file ("row_log_file.html", TOOL_NAME)
    print (f"Logging to {lf.name}")

    # Output parameters
    log_file = {"url": lf.name}
    result = records = ''

    try:

        item = row.utils.get_item (gis, row.registry.ORG_ITEM_TAG_SCORECARDS, org_id)
        test_lyr = row.utils.get_layer (gis, item, 0)
        
        records = f'ORG ID: {org_id}\n'
        for f in test_lyr.query(where='1=1', out_fields='OBJECTID, Notes', return_geometry=False):
            records += f"{f.attributes}\n"
        
        row.notebook.common.log (lf,records) 
        row.notebook.common.log (lf,f"'ENB_JOBID': {('ENB_JOBID' in os.environ)}")
        result = 'Success'

    except Exception as ex:
        row.notebook.common.log (lf,f"Exception: {str(ex)}")
        row.notebook.common.log (lf,traceback.format_exc())
        result = f"Failure: {str(ex)}"
        row.notebook.common.log (lf, "Adding Warning Message")
        arcpy.AddWarning(result)

    finally:
        row.notebook.common.log(lf, f"Updating tool completion {result}")
        row.notebook.common.log_tool_completion (gis, result,  org_id, gis.users.me.username, TOOL_NAME)
        row.notebook.common.close_log_file (lf)
        return result, records, log_file["url"]

if __name__ == '__main__':
    if "ENB_JOBID" not in os.environ:
        gis = GIS("https://www.arcgis.com", c.AGOL_OWNER_ID, keyring.get_password('AGOL', c.AGOL_OWNER_ID))
        result, records, log_file = run(gis, c.MODEL_ORG_ID)
        print (str(result))
        print (str(records))
        print (str(log_file))

    

