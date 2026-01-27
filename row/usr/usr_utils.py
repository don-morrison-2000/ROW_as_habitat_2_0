# Common functions
import os
import sys
import re
import shutil
import html
import pytz
import datetime as dt
import arcpy

import row.constants as c
import row.registry
import row.utils

import row.logger
logger = row.logger.get('row_log')

def get_item_registry_spec (item_registry_tag):
    return [s for s in row.registry.ORG_ITEMS_REGISTRY if s['tag'] == item_registry_tag][0]


def write_output_parameter_string (parm_name, value):
    if "ENB_JOBID" in os.environ:
        out_param_file = os.path.join(
            os.environ["ENB_JOBID"], "value_" + parm_name + ".dat")
        with open(out_param_file, "w") as writer:
            writer.write(str(value))
    return

def write_output_parameter_file (parm_name, url):
    if "ENB_JOBID" in os.environ:
        if not re.match(r"^https://", url):
            out_param_dir = os.path.join(os.environ["ENB_JOBID"], "outputs")
            os.makedirs(out_param_dir, exist_ok=True)
            shutil.copy(src=url, dst=out_param_dir)
            url = os.path.basename(url)
        with open(os.path.join(os.environ["ENB_JOBID"], "value_" + parm_name + ".dat"), "w") as writer:
            writer.write(str({"url": url}))
    return
      

def log_tool_completion (gis, msg, org_id, user, tool_name):
    try:
        log_item_layer = gis.content.get('90d1e1e132ab4fcab5e37d4b908d0d5e').tables[0]
        log_item_layer.edit_features(adds=[{'attributes': {'date_': dt.datetime.now(pytz.UTC), 'Org_ID': org_id, 'UserName': user, 'Tool': tool_name, 'message': msg}}]) 
    except:
        pass
    return

    
# def open_log_file (fn, tool_name):
#     if "ENB_JOBID" in os.environ:
#         #lf = open(os.path.join(arcpy.env.scratchFolder, fn), 'w',encoding='utf-8') # Running in notebook-based geoprocessing task
#         lf = open(os.path.join('/tmp', fn), 'w',encoding='utf-8') # Running in notebook-based geoprocessing task        
#     else:
#         if  os.path.isdir('/arcgis/home'):
#             lf = open(os.path.join('/arcgis/home', fn), 'w',encoding='utf-8')        # Running in notebook
#         else:
#             lf = open(os.path.join(arcpy.env.scratchFolder, fn), 'w',encoding='utf-8') # Running from command line

#     lf.write('<!DOCTYPE html><html><head><style>log_output {font-family: monospace}</style></head><body style="font-family: monospace;"><hr><p>Log<br><log_output>')
#     log (lf, f"{tool_name} starting")
#     log (lf, f"log file: {os.path.abspath(lf.name)}")
#     log (lf, f"os.getcwd(): {os.getcwd()}")
#     log (lf, f"os.listdir(os.getcwd()): {os.listdir(os.getcwd())}")
#     log (lf, f"arcpy.env.scratchFolder: {arcpy.env.scratchFolder}")
#     log (lf, f"os.listdir(arcpy.env.scratchFolder): {os.listdir(arcpy.env.scratchFolder)}")
#     log (lf, f"os.path.abspath(arcpy.env.scratchFolder): {os.path.abspath(arcpy.env.scratchFolder)}")
#     return lf
    

# def get_desc_from_tag (gis, tag):
#     return f"{row.utils.get_item_from_registry_tag (gis, tag, c.MODEL_ORG_ID).title}.  tag: {tag}"

# def get_tag_from_desc (gis, desc):
#     return desc.split()[-1]

def get_desc_from_tag (gis, tag, org_id=None):
    item = row.utils.get_item_from_registry_tag (gis, tag, org_id)
    if item is not None:
        return f"{item.title}.  tag: {tag}"
    else:
        return f"tag: {tag}"

def get_tag_from_desc (gis, desc):
    return desc.split()[-1]


def log(lf,msg):
    debug (msg)
    lf.write(f'<br>{dt.datetime.now(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")} {html.escape(msg)}')
    
def debug (msg):
    # if DEBUG:
    if 1:
        print (msg)
    return