import arcpy
import os, sys
from arcgis.gis import GIS

# Ensure we can import all of the row modules
CODE_BASE  = r'C:\ROW\ROW2.0\GitRepos\ROW_as_habitat_2_0'
if CODE_BASE not in sys.path:
    sys.path += [CODE_BASE]

import row.utils
import row.registry
import row.constants as c
import row.usr.usr_utils
import row.usr.tools.nb_test.nb_test_3
import row.usr.tools.nb_test_logging.nb_test_4

import importlib

import row.logger
logger = row.logger.get('row_log')

class Toolbox:
    def __init__(self):
        self.label = "User Tools"
        self.alias = "usertools"

        # List of tool classes associated with this toolbox
        self.tools = [Test, TestLogger]

g_gis = GIS("Pro")
g_org_ids = list(c.ORGS.keys())

class Test:
    def __init__(self):
        self.label = "Test Notebook"
        self.description = ""

    def getParameterInfo(self):
        importlib.reload(row.usr.tools.nb_test.nb_test_3)
        importlib.reload(row.usr.usr_utils)
        org_id = arcpy.Parameter("org_id", "Org ID", "Input", "String", "Required")
        org_id.filter.type = "ValueList"
        org_id.filter.list = [o for o in g_org_ids if o != row.constants.MODEL_ORG_ID]
        org_id.value = org_id.filter.list[0]

        fl_tag = arcpy.Parameter("fl_id", "Feature Layer", "Input", "String", "Required")
        fl_tag.filter.type = "ValueList"
        fl_tag.filter.list = [row.usr.usr_utils.get_desc_from_tag(g_gis, r['tag']) for r in row.registry.ORG_ITEMS_REGISTRY if r['type'] == 'Feature Service']
        fl_tag.value = fl_tag.filter.list[0]

        result = arcpy.Parameter('result', 'Result', 'Output', 'String', 'Derived')
        records = arcpy.Parameter('records', 'Records', 'Output', 'String', 'Derived')
        log_file = arcpy.Parameter('log_file', 'Log File', 'Output', 'DEFile', 'Derived')

        return [org_id, fl_tag, result, records, log_file]

    def isLicensed(self):
        return True
    def updateParameters(self, parameters):
        return
    def updateMessages(self, parameters):
        return
    
    def execute(self, parameters, messages):
        importlib.reload(row.usr.tools.nb_test.nb_test_3) 
        importlib.reload(row.usr.usr_utils)
        result, records, log_file = row.usr.tools.nb_test.nb_test_3.run (g_gis, parameters[0].value, row.usr.usr_utils.get_tag_from_desc(g_gis, parameters[1].value))
        parameters[2].value = result
        parameters[3].value = records       
        parameters[4].value = log_file

    def postExecute(self, parameters):
        return


class TestLogger:
    def __init__(self):
        self.label = "Test Logger"
        self.description = ""

    def getParameterInfo(self):
        importlib.reload(row.usr.tools.nb_test_logging.nb_test_4)
        importlib.reload(row.usr.usr_utils)
        org_id = arcpy.Parameter("org_id", "Org ID", "Input", "String", "Required")
        org_id.filter.type = "ValueList"
        org_id.filter.list = [o for o in g_org_ids if o != row.constants.MODEL_ORG_ID]
        org_id.value = org_id.filter.list[0]

        fl_tag = arcpy.Parameter("fl_id", "Feature Layer", "Input", "String", "Required")
        fl_tag.filter.type = "ValueList"
        fl_tag.filter.list = [row.usr.usr_utils.get_desc_from_tag(g_gis, r['tag']) for r in row.registry.ORG_ITEMS_REGISTRY if r['type'] == 'Feature Service']
        fl_tag.value = fl_tag.filter.list[0]

        result = arcpy.Parameter('result', 'Result', 'Output', 'String', 'Derived')
        records = arcpy.Parameter('records', 'Records', 'Output', 'String', 'Derived')
        log_file = arcpy.Parameter('log_file', 'Log File', 'Output', 'DEFile', 'Derived')

        return [org_id, fl_tag, result, records, log_file]

    def isLicensed(self):
        return True
    def updateParameters(self, parameters):
        return
    def updateMessages(self, parameters):
        return
    
    def execute(self, parameters, messages):
        importlib.reload(row.usr.tools.nb_test_logging.nb_test_4) 
        importlib.reload(row.usr.usr_utils)
        result, records, log_file = row.usr.tools.nb_test_logging.nb_test_4.run (g_gis, parameters[0].value, row.usr.usr_utils.get_tag_from_desc(g_gis, parameters[1].value))
        parameters[2].value = result
        parameters[3].value = records       
        parameters[4].value = log_file

    def postExecute(self, parameters):
        return