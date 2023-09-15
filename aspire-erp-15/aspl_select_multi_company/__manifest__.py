# -*- coding: utf-8 -*-
{
    "name": "Multi Company Selection",
    'category': 'base',
    "summary": "Multi Company Selection",
    'version': '15.0.1.0',
    "license": "OPL-1",
    "description": """
Set All company to enable all companies, Set Disable to enable User current company
    """,
    "author": "Aspire Softserv Pvt. Ltd",
    "website": "https://aspiresoftware.in",
    "depends": [
        'web',
    ],
    'assets': {
        'web.assets_backend': [
            'aspl_select_multi_company/static/src/js/company_service.js',
            'aspl_select_multi_company/static/src/js/switch_company_menu.js'
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
}

