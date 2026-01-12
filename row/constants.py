AGOL_OWNER_ID = 'ROW_Admin'
MODEL_ORG_ID = 'ROW2_Model_Org'
MODEL_ORG_NAME = 'ROW2.0 ModelOrganization'

CODE_BASE = r'C:\ROW\ROW2.0\GitRepos\ROW_as_habitat_2_0'
BACKUP_DIR = r'\\ercrowarcgis\ROW\DEV\backup'

SINGLETONS_FOLDER = 'ROW2_Singletons'
ADMIN_FOLDER = 'ROW2_Admin'

CLONE_TAG_ROOT = 'ROW2ITEM_'   # Prefix to item tags to indicate the items should be propagated to all orgs

ORGS = {
                'ROW2_Model_Org': {'name': MODEL_ORG_NAME},
                'ROW2_DEVOrgB': {'name': 'Test Organization B'}    
        }


ITEM_SPECS = [
        {'id': 'ORG_CENTERLINES', 'title': 'Centerlines', 'type': 'Feature Service', 
                'snippet': '{ORG_ID} centerlines',
                'description': '{ORG_NAME} centerlines',
                'layers': 
                [     
                        {'id': 'ORG_CENTERLINES_LYR', 'idx': 0, 'title': 'Centerline', 'sde_source': 'Centerline', 'sde_relations': []},
                ]
        },
        {'id': 'ORG_MGT_AREAS', 'title': 'Management Areas', 'type': 'Feature Service', 
                'snippet': '{ORG_ID} management areas',
                'description': '{ORG_NAME} management areas',
                'layers': 
                [     
                        {'id': 'ORG_MGT_AREAS_LYR', 'idx': 0, 'title': 'ManagementArea', 'sde_source': 'ManagementArea', 'sde_relations': []},
                ]
        },        
        {'id': 'ORG_SCORECARDS', 'title': 'Pollinator Scorecards', 'type': 'Feature Service', 
                'snippet': '{ORG_ID} pollinator scorecards',
                'description': '{ORG_NAME} pollinator scorecards',
                'layers': 
                [     
                        {'id': 'ORG_SCORECARDS_LYR', 'idx': 0, 'title': 'PollinatorScorecard', 'sde_source': 'PollinatorScorecard', 'sde_relations': ['PollinatorScorecard__ATTACH']},
                ]
        },        
        {'id': 'ORG_BEE_OCCURRENCE', 'title': 'Bee Occurrence Areas', 'type': 'Feature Service', 
                'snippet': '{ORG_ID} bee occurrence areas',
                'description': '{ORG_NAME} bee occurrence areas',
                'layers': 
                [ 
                        {'id': 'ORG_BEE_OCCURRENCE_LYR', 'idx': 0, 'title': 'Bee Occurrence Areas', 'sde_source': 'Analysis_BeeOccurrenceAreas', 'sde_relations': []},
                ]
        },
        {'id': 'ORG_BEE_HABITAT', 'title': 'Bee Habitat', 'type': 'Feature Service', 
                'snippet': '{ORG_ID} bee habitat',
                'description': '{ORG_NAME} bee habitat',
                'layers': 
                [ 
                        {'id': 'ORG_BEE_HABITAT_LYR', 'idx': 0, 'title': 'Bee Habitat', 'sde_source': 'Analysis_BeeHabitat', 'sde_relations': []},
                ]
        },        
        {'id': 'ORG_BEE_REPORT', 'title': 'Bee Report', 'type': 'Feature Service', 
                'snippet': '{ORG_ID} bee report',
                'description': '{ORG_NAME} bee report',
                'layers': 
                [ 
                        {'id': 'ORG_BEE_REPORT_LYR', 'idx': 0, 'title': 'Bee Report', 'sde_source': 'Analysis_BeeReportView', 'sde_relations': []},
                ]
        },        
        {'id': 'ORG_STATS', 'title': 'Statistics', 'type': 'Feature Service', 
                'snippet': '{ORG_ID} statistics',
                'description': '{ORG_NAME} statistics',
                'layers': 
                [ 
                        {'id': 'ORG_STATS_LYR', 'idx': 0, 'title': 'Statistics', 'sde_source': 'Analysis_OrgStatsView', 'sde_relations': []},
                ]
        },        
        {'id': 'ORG_ORG', 'title': 'Organization Profile', 'type': 'Feature Service', 
                'snippet': '{ORG_ID} profile',
                'description': '{ORG_NAME} profile',
                'layers': 
                [ 
                        {'id': 'ORG_ORG_LYR', 'idx': 0, 'title': 'Organization Profile', 'sde_source': 'Organization', 'sde_relations': []},    
                ]
        },        
]
 