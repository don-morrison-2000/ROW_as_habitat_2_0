import os
import row.constants as c


GROUP_TAG_ROOT = 'row2group_'
GROUP_TAG_FIELDWORKER =f'{GROUP_TAG_ROOT}org_fieldworker'
GROUP_TAG_MANAGEMENT = f'{GROUP_TAG_ROOT}org_management'
ORG_GROUPS_REGISTRY = [
        {'tag': GROUP_TAG_FIELDWORKER, 'title': '!ORG_ID! Fieldworker Group', 'description': 'Fieldworker group'},
        {'tag': GROUP_TAG_MANAGEMENT, 'title': '!ORG_ID! Management Group', 'description': 'Management group'},
]


ORG_ITEM_TAG_ROOT = 'row2item_'
ORG_ITEM_TAG_CENTERLINES = f'{ORG_ITEM_TAG_ROOT}org_centerlines'
ORG_ITEM_TAG_MGT_AREAS = f'{ORG_ITEM_TAG_ROOT}org_mgt_areas'
ORG_ITEM_TAG_SCORECARDS = f'{ORG_ITEM_TAG_ROOT}org_scorecards'
ORG_ITEM_TAG_BEE_OCCURRENCE = f'{ORG_ITEM_TAG_ROOT}org_bee_occurrence'
ORG_ITEM_BEE_HABITAT = f'{ORG_ITEM_TAG_ROOT}org_bee_habitat'
ORG_ITEM_BEE_REPORT = f'{ORG_ITEM_TAG_ROOT}org_bee_report'
ORG_ITEM_STATS = f'{ORG_ITEM_TAG_ROOT}org_stats'
ORG_ITEM_ORG = f'{ORG_ITEM_TAG_ROOT}org_org'
ORG_ITEMS_REGISTRY = [
        # FEATURE LAYERS
        {'tag': ORG_ITEM_TAG_CENTERLINES, 'type': 'Feature Service', 
                'group_sharing': [GROUP_TAG_MANAGEMENT, GROUP_TAG_FIELDWORKER],
                'allow_extended_sharing': True,
                'premium': False,
        },
        {'tag': ORG_ITEM_TAG_MGT_AREAS, 'type': 'Feature Service', 
                'group_sharing': [GROUP_TAG_MANAGEMENT, GROUP_TAG_FIELDWORKER],
                'allow_extended_sharing': True,
                'premium': False,
        },        
        {'tag': ORG_ITEM_TAG_SCORECARDS, 'type': 'Feature Service', 
                'group_sharing': [GROUP_TAG_MANAGEMENT, GROUP_TAG_FIELDWORKER],
                'allow_extended_sharing': True,
                'premium': False,
        },        
        {'tag': ORG_ITEM_TAG_BEE_OCCURRENCE, 'type': 'Feature Service', 
                'group_sharing': [GROUP_TAG_MANAGEMENT],
                'allow_extended_sharing': False,
                'premium': False,
        },
        {'tag': ORG_ITEM_BEE_HABITAT, 'type': 'Feature Service', 
                'group_sharing': [GROUP_TAG_MANAGEMENT],
                'allow_extended_sharing': False,
                'premium': False,
        },        
        {'tag': ORG_ITEM_BEE_REPORT, 'type': 'Feature Service', 
                'group_sharing': [GROUP_TAG_MANAGEMENT],
                'allow_extended_sharing': False,
                'premium': False,
        },        
        {'tag': ORG_ITEM_STATS, 'type': 'Feature Service', 
                'group_sharing': [GROUP_TAG_MANAGEMENT],
                'allow_extended_sharing': False,
                'premium': False,
        },        
        {'tag': ORG_ITEM_ORG, 'type': 'Feature Service', 
                'group_sharing': [GROUP_TAG_MANAGEMENT],
                'allow_extended_sharing': False,
                'premium': False,
        },        


        # WEB MAPS
        {'tag': f'{ORG_ITEM_TAG_ROOT}org_webmap', 'type': 'Web Map', 
                'group_sharing': [GROUP_TAG_MANAGEMENT],
                'allow_extended_sharing': False,
                'premium': False,
        },

        # WEB EXPERIENCES
        {'tag': f'{ORG_ITEM_TAG_ROOT}org_webexperience', 'type': 'Web Experience', 
                'group_sharing': [GROUP_TAG_MANAGEMENT],
                'allow_extended_sharing': False,
                'premium': False,
        },
]


ADMIN_ITEM_TAG_ROOT = 'row2admin_'
ADMIN_ITEM_TAG_ADMIN_EVENTS = f'{ADMIN_ITEM_TAG_ROOT}admin_events'
ADMIN_ITEM_TAG_ORGANIZATION = f'{ADMIN_ITEM_TAG_ROOT}organization'
ADMIN_ITEMS_REGISTRY = [
        # FEATURE LAYERS
        {'tag': ADMIN_ITEM_TAG_ADMIN_EVENTS, 'type': 'Feature Service', 
                'group_sharing': [],
                'allow_extended_sharing': False,
                'premium': False,
        }, 
        {'tag': ADMIN_ITEM_TAG_ORGANIZATION, 'type': 'Feature Service', 
                'group_sharing': [],
                'allow_extended_sharing': False,
                'premium': False,
        },    
]


CODE_TAG_ROOT = 'row2code_'
CODE_TAG_TEST_NOTEBOOK = f'{CODE_TAG_ROOT}test_code_1'
CODE_ITEMS_REGISTRY = [
        {'tag': CODE_TAG_TEST_NOTEBOOK, 'files': 
                [
                        os.path.join(c.ROW_BASE, 'constants.py'),
                        os.path.join(c.ROW_BASE, 'registry.py'),
                        os.path.join(c.ROW_BASE, 'utils.py'),
                        os.path.join(c.ROW_BASE, 'notebook', '*.py'),
                ]
        }
]