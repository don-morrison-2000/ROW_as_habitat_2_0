import arcpy
import os, sys

# Ensure we can import all of the row modules
CODE_BASE  = r'C:\ROW\ROW2.0\GitRepos\ROW_as_habitat_2_0'
if CODE_BASE not in sys.path:
    sys.path += [CODE_BASE]

import row.utils
import row.registry
import row.constants as c
import row.adm.adm_utils
import row.adm.obj.organization
import row.adm.tools.upload_notebook_libraries
import row.adm.tools.create_org
import row.adm.tools.delete_org
import row.adm.tools.backup_org
import row.usr.usr_utils
import importlib


import row.logger
logger = row.logger.get('row_log')


g_gis = row.adm.adm_utils.login_as_admin ()
g_org_ids = list(row.constants.ORGS.keys())

class Toolbox:
    def __init__(self):
        self.label = "Admin Tools"
        self.alias = "admintools"

        # List of tool classes associated with this toolbox
        self.tools = [PropagateModelOrg, CreateOrg, DeleteOrg, UploadNotebookLibraries]





class PropagateModelOrg:
    def __init__(self):
        self.label = "Propagate Model Organization Items"
        self.description = ""

    def getParameterInfo(self):
        importlib.reload(row.adm.obj.organization)
        org_id = arcpy.Parameter("org_id", "Org ID", "Input", "String", "Required")
        org_id.filter.type = "ValueList"
        org_id.filter.list = [o for o in g_org_ids if o != row.constants.MODEL_ORG_ID]
        org_id.value = org_id.filter.list[0]

        check_boxes = []
        for tag in row.registry.ORG_ITEMS_REGISTRY.keys():
            check_box = arcpy.Parameter(tag, row.adm.adm_utils.get_item_desc_from_tag (g_gis, tag, c.MODEL_ORG_ID), "Input", "GPBoolean", "Required")
            check_box.value = False
            check_boxes.append(check_box)
        for tag in row.registry.ORG_GROUPS_REGISTRY.keys():
            check_box = arcpy.Parameter(tag, row.adm.adm_utils.get_group_desc_from_tag (g_gis, tag, c.MODEL_ORG_ID), "Input", "GPBoolean", "Required")
            check_box.value = False
            check_boxes.append(check_box)

        return [org_id] + check_boxes

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        return

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        importlib.reload(row.adm.obj.organization)
        item_tags = [p.name for p in parameters if p.name in row.registry.ORG_ITEMS_REGISTRY.keys() and p.value == True]
        group_tags = [p.name for p in parameters if p.name in row.registry.ORG_GROUPS_REGISTRY.keys() and p.value == True]
        row.adm.obj.organization.update (g_gis, parameters[0].value, item_tags, group_tags)

    def postExecute(self, parameters):
        return

class CreateOrg:
    def __init__(self):
        self.label = "Create Organization"
        self.description = ""

    def getParameterInfo(self):
        importlib.reload(row.adm.tools.create_org)
        org_id = arcpy.Parameter("org_id", "Org ID", "Input", "String", "Required")
        org_id.filter.type = "ValueList"
        org_id.filter.list = [o for o in g_org_ids if o != row.constants.MODEL_ORG_ID]
        org_id.value = org_id.filter.list[0]
        return [org_id]

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        return

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        importlib.reload(row.adm.tools.create_org) 
        row.adm.tools.create_org.run (g_gis, parameters[0].value)

    def postExecute(self, parameters):
        return


class DeleteOrg:
    def __init__(self):
        self.label = "Delete Organization"
        self.description = ""

    def getParameterInfo(self):
        importlib.reload(row.adm.tools.delete_org)
        org_id = arcpy.Parameter("org_id", "Org ID", "Input", "String", "Required")
        org_id.filter.type = "ValueList"
        org_id.filter.list = [o for o in g_org_ids if o != row.constants.MODEL_ORG_ID]
        org_id.value = org_id.filter.list[0]
        return [org_id]

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        return

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        importlib.reload(row.adm.tools.delete_org) 
        row.adm.tools.delete_org.run (g_gis, parameters[0].value)

    def postExecute(self, parameters):
        return



class UploadNotebookLibraries:
    def __init__(self):
        self.label = "Upload Notebook Libraries"
        self.description = ""

    def getParameterInfo(self):
        importlib.reload(row.adm.tools.upload_notebook_libraries)
        nb_id = arcpy.Parameter("notebook", "Notebook", "Input", "String", "Required")
        nb_id.filter.type = "ValueList"
        nb_id.filter.list = [f"{row.adm.adm_utils.get_item_desc_from_tag (g_gis, tag)}" for tag in row.registry.CODE_ITEMS_REGISTRY.keys()]
        nb_id.value = nb_id.filter.list[0]
        return [nb_id]

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        return

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        importlib.reload(row.adm.tools.upload_notebook_libraries)
        tag = parameters[0].value.split()[-1]
        row.adm.tools.upload_notebook_libraries.run (g_gis, tag)

    def postExecute(self, parameters):
        return
