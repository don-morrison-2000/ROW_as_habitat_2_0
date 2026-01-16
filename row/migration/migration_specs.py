import row.usr.constants as c


MIGRATION_SPECS = [
        {'tag': f'{c.ITEM_TAG_ROOT}org_centerlines', 'title': 'Centerlines', 'type': 'Feature Service', 
                'snippet': '{ORG_ID} centerlines',
                'description': '{ORG_NAME} centerlines',
                'layers': 
                [     
                        {'id': 'ORG_CENTERLINES_LYR', 'idx': 0, 'title': 'Centerline', 'sde_source': 'Centerline', 'sde_relations': []},
                ]
        },
        {'tag': f'{c.ITEM_TAG_ROOT}org_mgt_areas', 'title': 'Management Areas', 'type': 'Feature Service', 
                'snippet': '{ORG_ID} management areas',
                'description': '{ORG_NAME} management areas',
                'layers': 
                [     
                        {'id': 'ORG_MGT_AREAS_LYR', 'idx': 0, 'title': 'ManagementArea', 'sde_source': 'ManagementArea', 'sde_relations': []},
                ]
        },        
        {'tag': f'{c.ITEM_TAG_ROOT}org_scorecards', 'title': 'Pollinator Scorecards', 'type': 'Feature Service', 
                'snippet': '{ORG_ID} pollinator scorecards',
                'description': '{ORG_NAME} pollinator scorecards',
                'layers': 
                [     
                        {'id': 'ORG_SCORECARDS_LYR', 'idx': 0, 'title': 'PollinatorScorecard', 'sde_source': 'PollinatorScorecard', 'sde_relations': ['PollinatorScorecard__ATTACH']},
                ]
        },        
        {'tag': f'{c.ITEM_TAG_ROOT}org_bee_occurrence', 'title': 'Bee Occurrence Areas', 'type': 'Feature Service', 
                'snippet': '{ORG_ID} bee occurrence areas',
                'description': '{ORG_NAME} bee occurrence areas',
                'layers': 
                [ 
                        {'id': 'ORG_BEE_OCCURRENCE_LYR', 'idx': 0, 'title': 'Bee Occurrence Areas', 'sde_source': 'Analysis_BeeOccurrenceAreas', 'sde_relations': []},
                ]
        },
        {'tag': f'{c.ITEM_TAG_ROOT}org_bee_habitat', 'title': 'Bee Habitat', 'type': 'Feature Service', 
                'snippet': '{ORG_ID} bee habitat',
                'description': '{ORG_NAME} bee habitat',
                'layers': 
                [ 
                        {'id': 'ORG_BEE_HABITAT_LYR', 'idx': 0, 'title': 'Bee Habitat', 'sde_source': 'Analysis_BeeHabitat', 'sde_relations': []},
                ]
        },        
        {'tag': f'{c.ITEM_TAG_ROOT}org_bee_report', 'title': 'Bee Report', 'type': 'Feature Service', 
                'snippet': '{ORG_ID} bee report',
                'description': '{ORG_NAME} bee report',
                'layers': 
                [ 
                        {'id': 'ORG_BEE_REPORT_LYR', 'idx': 0, 'title': 'Bee Report', 'sde_source': 'Analysis_BeeReportView', 'sde_relations': []},
                ]
        },        
        {'tag': f'{c.ITEM_TAG_ROOT}org_stats', 'title': 'Statistics', 'type': 'Feature Service', 
                'snippet': '{ORG_ID} statistics',
                'description': '{ORG_NAME} statistics',
                'layers': 
                [ 
                        {'id': 'ORG_STATS_LYR', 'idx': 0, 'title': 'Statistics', 'sde_source': 'Analysis_OrgStatsView', 'sde_relations': []},
                ]
        },        
        {'tag': f'{c.ITEM_TAG_ROOT}org_org', 'title': 'Organization Profile', 'type': 'Feature Service', 
                'snippet': '{ORG_ID} profile',
                'description': '{ORG_NAME} profile',
                'layers': 
                [ 
                        {'id': 'ORG_ORG_LYR', 'idx': 0, 'title': 'Organization Profile', 'sde_source': 'Organization', 'sde_relations': []},    
                ]
        },        
]