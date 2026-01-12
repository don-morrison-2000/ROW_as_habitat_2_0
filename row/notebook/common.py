# Common functions
import os
import sys
import re
import shutil
import html
import pytz
import datetime as dt
import arcpy

import row.notebook.constants as c

def get_item_spec (item_spec_id):
    return [s for s in c.ITEM_SPECS if s['id'] == item_spec_id][0]

def get_item_layer_spec (item_spec, item_layer_spec_id):
    return [l for l in item_spec['layers'] if l['id'] == item_layer_spec_id][0]

def get_org_layer (gis, item_spec_id, item_layer_spec_id, org_id):
    item_spec = get_item_spec (item_spec_id)
    item_layer_spec = get_item_layer_spec (item_spec, item_layer_spec_id)
    org_item = get_org_item (gis, item_spec['title'],  item_spec['type'], org_id)
    if len(org_item.layers) > 0:
        org_layer = [l for l in org_item.layers if l.properties['name'] == item_layer_spec['title']]
        if len(org_layer) == 1:
            return org_layer[0]
    if len(org_item.tables) > 0:
        org_table = [t for t in org_item.tables if t.properties['name'] == item_layer_spec['title']]
        if len(org_table) == 1:
            return org_table[0]
    raise Exception (f"Could not find {org_id} layer '{item_layer_spec['title']}' in {item_spec['type']} '{item_spec['title']}'")
            

def get_org_item (gis, title, item_type, org_id):
    query_string = f"title:{title} AND owner:row_admin AND tags:{org_id.lower()} AND type:{item_type}"
    for item in gis.content.search(query=query_string, max_items=-1):
        if item.title == title and item.owner == 'ROW_Admin' and org_id.lower() in item.tags:
            return gis.content.get(item.id)
    raise Exception (f"Can not access {org_id} {item_type} '{title}' as user {gis.users.me.username}")


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

    
def open_log_file (fn, tool_name):
    if "ENB_JOBID" in os.environ:
        #lf = open(os.path.join(arcpy.env.scratchFolder, fn), 'w',encoding='utf-8') # Running in notebook-based geoprocessing task
        lf = open(os.path.join('/tmp', fn), 'w',encoding='utf-8') # Running in notebook-based geoprocessing task        
    else:
        if  os.path.isdir('/arcgis/home'):
            lf = open(os.path.join('/arcgis/home', fn), 'w',encoding='utf-8')        # Running in notebook
        else:
            lf = open(os.path.join(arcpy.env.scratchFolder, fn), 'w',encoding='utf-8') # Running from command line

    lf.write('<!DOCTYPE html><html><head><style>log_output {font-family: monospace}</style></head><body style="font-family: monospace;"><hr><p>Log<br><log_output>')
    log (lf, f"{tool_name} starting")
    log (lf, f"log file: {os.path.abspath(lf.name)}")
    log (lf, f"os.getcwd(): {os.getcwd()}")
    log (lf, f"os.listdir(os.getcwd()): {os.listdir(os.getcwd())}")
    log (lf, f"arcpy.env.scratchFolder: {arcpy.env.scratchFolder}")
    log (lf, f"os.listdir(arcpy.env.scratchFolder): {os.listdir(arcpy.env.scratchFolder)}")
    log (lf, f"os.path.abspath(arcpy.env.scratchFolder): {os.path.abspath(arcpy.env.scratchFolder)}")
    return lf
    

def close_log_file (lf):
    lf.close()
    return

def log(lf,msg):
    debug (msg)
    lf.write(f'<br>{dt.datetime.now(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")} {html.escape(msg)}')
    
def debug (msg):
    # if DEBUG:
    if 1:
        print (msg)
    return