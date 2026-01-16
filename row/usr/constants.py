from  arcgis.gis import SharingLevel


AGOL_OWNER_ID = 'ROW_Admin'
MODEL_ORG_ID = 'ROW2_Model_Org'
MODEL_ORG_NAME = 'ROW2.0 ModelOrganization'

CODE_BASE = r'C:\ROW\ROW2.0\GitRepos\ROW_as_habitat_2_0'
BACKUP_DIR = r'\\ercrowarcgis\ROW\DEV\backup'

SINGLETONS_FOLDER = 'ROW2_Singletons'
ADMIN_FOLDER = 'ROW2_Admin'

ITEM_TAG_ROOT = 'row2item_'   # Prefix to item tags to indicate the items should be propagated to all orgs
GROUP_TAG_ROOT = 'row2group_'

GROUP_SPECS = [
        {'tag': 'org_fieldworker', 'title': '!ORG_ID! Fieldworker Group', 'description': 'Fieldworker group'},
        {'tag': 'org_management', 'title': '!ORG_ID! Management Group', 'description': 'Management group'},
]

ORGS = {
                'ROW2_Model_Org': {'name': MODEL_ORG_NAME, 'extended_sharing_level': SharingLevel.PRIVATE},
                'ROW2_DEVOrgB': {'name': 'Test Organization B', 'extended_sharing_level': SharingLevel.PRIVATE}    
        }


ORG_ITEMS_REGISTRY = [
    
        # FEATURE LAYERS
        {'tag': f'{ITEM_TAG_ROOT}org_centerlines', 'type': 'Feature Service', 
                'group_sharing': [f'{GROUP_TAG_ROOT}ORG_MANAGEMENT', f'{GROUP_TAG_ROOT}ORG_FIELDWORKER'],
                'allow_extended_sharing': True,
                'premium': False,
        },
        {'tag': f'{ITEM_TAG_ROOT}org_mgt_areas', 'type': 'Feature Service', 
                'group_sharing': [f'{GROUP_TAG_ROOT}ORG_MANAGEMENT', f'{GROUP_TAG_ROOT}ORG_FIELDWORKER'],
                'allow_extended_sharing': True,
                'premium': False,
        },        
        {'tag': f'{ITEM_TAG_ROOT}org_scorecards', 'type': 'Feature Service', 
                'group_sharing': [f'{GROUP_TAG_ROOT}ORG_MANAGEMENT', f'{GROUP_TAG_ROOT}ORG_FIELDWORKER'],
                'allow_extended_sharing': True,
                'premium': False,
        },        
        {'tag': f'{ITEM_TAG_ROOT}org_bee_occurrence', 'type': 'Feature Service', 
                'group_sharing': [f'{GROUP_TAG_ROOT}ORG_MANAGEMENT'],
                'allow_extended_sharing': False,
                'premium': False,
        },
        {'tag': f'{ITEM_TAG_ROOT}org_bee_habitat', 'type': 'Feature Service', 
                'group_sharing': [f'{GROUP_TAG_ROOT}ORG_MANAGEMENT'],
                'allow_extended_sharing': False,
                'premium': False,
        },        
        {'tag': f'{ITEM_TAG_ROOT}org_bee_report', 'type': 'Feature Service', 
                'group_sharing': [f'{GROUP_TAG_ROOT}ORG_MANAGEMENT'],
                'allow_extended_sharing': False,
                'premium': False,
        },        
        {'tag': f'{ITEM_TAG_ROOT}org_stats', 'type': 'Feature Service', 
                'group_sharing': [f'{GROUP_TAG_ROOT}ORG_MANAGEMENT'],
                'allow_extended_sharing': False,
                'premium': False,
        },        
        {'tag': f'{ITEM_TAG_ROOT}org_org', 'type': 'Feature Service', 
                'group_sharing': [f'{GROUP_TAG_ROOT}ORG_MANAGEMENT'],
                'allow_extended_sharing': False,
                'premium': False,
        },        


        # WEB MAPS
        {'tag': f'{ITEM_TAG_ROOT}ORG_WEB_MAP', 'type': 'Web Map', 
                'group_sharing': [f'{GROUP_TAG_ROOT}ORG_MANAGEMENT'],
                'allow_extended_sharing': False,
                'premium': False,
        },

        # WEB EXPERIENCES
        {'tag': f'{ITEM_TAG_ROOT}ORG_WEB_EXPERIENCE', 'type': 'Web Experience', 
                'group_sharing': [f'{GROUP_TAG_ROOT}ORG_MANAGEMENT'],
                'allow_extended_sharing': False,
                'premium': False,
        },
]

# ITEM_SPECS = [
#         {'id': 'ORG_CENTERLINES', 'title': 'Centerlines', 'type': 'Feature Service', 
#                 'snippet': '{ORG_ID} centerlines',
#                 'description': '{ORG_NAME} centerlines',
#                 'sharing_level': 'Organization',
#                 'group_sharing': ['ORG_FIELDWORKER', 'ORG_MANAGEMENT'],
#                 'layers': 
#                 [     
#                         {'id': 'ORG_CENTERLINES_LYR', 'idx': 0, 'title': 'Centerline', 'sde_source': 'Centerline', 'sde_relations': []},
#                 ]
#         },
#         {'id': 'ORG_MGT_AREAS', 'title': 'Management Areas', 'type': 'Feature Service', 
#                 'snippet': '{ORG_ID} management areas',
#                 'description': '{ORG_NAME} management areas',
#                 'sharing_level': 'Public',
#                 'group_sharing': [],
#                 'layers': 
#                 [     
#                         {'id': 'ORG_MGT_AREAS_LYR', 'idx': 0, 'title': 'ManagementArea', 'sde_source': 'ManagementArea', 'sde_relations': []},
#                 ]
#         },        
#         {'id': 'ORG_SCORECARDS', 'title': 'Pollinator Scorecards', 'type': 'Feature Service', 
#                 'snippet': '{ORG_ID} pollinator scorecards',
#                 'description': '{ORG_NAME} pollinator scorecards',
#                 'sharing_level': 'None',
#                 'group_sharing': [],
#                 'layers': 
#                 [     
#                         {'id': 'ORG_SCORECARDS_LYR', 'idx': 0, 'title': 'PollinatorScorecard', 'sde_source': 'PollinatorScorecard', 'sde_relations': ['PollinatorScorecard__ATTACH']},
#                 ]
#         },        
#         {'id': 'ORG_BEE_OCCURRENCE', 'title': 'Bee Occurrence Areas', 'type': 'Feature Service', 
#                 'snippet': '{ORG_ID} bee occurrence areas',
#                 'description': '{ORG_NAME} bee occurrence areas',
#                 'sharing_level': 'None',
#                 'group_sharing': [],
#                 'layers': 
#                 [ 
#                         {'id': 'ORG_BEE_OCCURRENCE_LYR', 'idx': 0, 'title': 'Bee Occurrence Areas', 'sde_source': 'Analysis_BeeOccurrenceAreas', 'sde_relations': []},
#                 ]
#         },
#         {'id': 'ORG_BEE_HABITAT', 'title': 'Bee Habitat', 'type': 'Feature Service', 
#                 'snippet': '{ORG_ID} bee habitat',
#                 'description': '{ORG_NAME} bee habitat',
#                 'sharing_level': 'None',
#                 'group_sharing': [],
#                 'layers': 
#                 [ 
#                         {'id': 'ORG_BEE_HABITAT_LYR', 'idx': 0, 'title': 'Bee Habitat', 'sde_source': 'Analysis_BeeHabitat', 'sde_relations': []},
#                 ]
#         },        
#         {'id': 'ORG_BEE_REPORT', 'title': 'Bee Report', 'type': 'Feature Service', 
#                 'snippet': '{ORG_ID} bee report',
#                 'description': '{ORG_NAME} bee report',
#                 'sharing_level': 'None',
#                 'group_sharing': [],
#                 'layers': 
#                 [ 
#                         {'id': 'ORG_BEE_REPORT_LYR', 'idx': 0, 'title': 'Bee Report', 'sde_source': 'Analysis_BeeReportView', 'sde_relations': []},
#                 ]
#         },        
#         {'id': 'ORG_STATS', 'title': 'Statistics', 'type': 'Feature Service', 
#                 'snippet': '{ORG_ID} statistics',
#                 'description': '{ORG_NAME} statistics',
#                 'sharing_level': 'None',
#                 'group_sharing': [],
#                 'layers': 
#                 [ 
#                         {'id': 'ORG_STATS_LYR', 'idx': 0, 'title': 'Statistics', 'sde_source': 'Analysis_OrgStatsView', 'sde_relations': []},
#                 ]
#         },        
#         {'id': 'ORG_ORG', 'title': 'Organization Profile', 'type': 'Feature Service', 
#                 'snippet': '{ORG_ID} profile',
#                 'description': '{ORG_NAME} profile',
#                 'sharing_level': 'None',
#                 'group_sharing': [],
#                 'layers': 
#                 [ 
#                         {'id': 'ORG_ORG_LYR', 'idx': 0, 'title': 'Organization Profile', 'sde_source': 'Organization', 'sde_relations': []},    
#                 ]
#         },        
# ]
 