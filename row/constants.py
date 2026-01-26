from  arcgis.gis import SharingLevel
import os


AGOL_OWNER_ID = 'ROW_Admin'
MODEL_ORG_ID = 'ROW2_Model_Org'
MODEL_ORG_NAME = 'ROW2.0 ModelOrganization'

CODE_BASE = r'C:\ROW\ROW2.0\GitRepos\ROW_as_habitat_2_0'
ROW_BASE = os.path.join(CODE_BASE, 'row')
BACKUP_DIR = r'\\ercrowarcgis\ROW\DEV\backup'

SINGLETONS_FOLDER = 'ROW2_Singletons'
ADMIN_FOLDER = 'ROW2_Admin'

ORGS = {
                'ROW2_Model_Org': {'name': MODEL_ORG_NAME, 'extended_sharing_level': SharingLevel.PRIVATE},
                'ROW2_DEVOrgA': {'name': 'Test Organization A', 'extended_sharing_level': SharingLevel.PRIVATE},
                'ROW2_DEVOrgB': {'name': 'Test Organization B', 'extended_sharing_level': SharingLevel.PRIVATE},
                'ROW2_DEVOrgC': {'name': 'Test Organization C', 'extended_sharing_level': SharingLevel.PRIVATE},        
        }




ADMIN_EVENT_CREATE_ORG = 'CreateOrg'
ADMIN_EVENT_UPDATE_ORG = 'UpdateOrg'
ADMIN_EVENT_DELETE_ORG = 'DeleteOrg'
ADMIN_EVENT_BACKUP_ORG = 'BackupOrg'
ADMIN_EVENT_CHANGE_ORGID = 'ChangeOrgId'
ADMIN_EVENT_CHANGE_ORG_CONTACT = 'ChangeOrgContact'
ADMIN_EVENT_CREATE_USER = 'CreateUser'
ADMIN_EVENT_DELETE_ORG_DATA = 'DeleteOrgData'
ADMIN_EVENT_ADMIN_ALERT = "AdminAlert"
ADMIN_EVENT_CHANGE_PREMIUM = 'ChangePremiumContent'

 