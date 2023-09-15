# -*- coding: utf-8 -*-

{
    'name': "Aspire Project Task Extension",
    'summary': """
    To Control The Project Module
    """,
    'description': """""",
    'author': "Aspire Softserv Pvt Ltd",
    'website': "http://aspiresoftware.co.in",
    'category': 'Tools',
    'version': '15.0.0.0.0',
    'license': 'LGPL-3',
    # any module necessary for this one to work correctly
    'depends': ['base', 'project', 'hr', 'project_task_milestone'],  # deprecated 'hr_timesheet_sheet',
    # always loaded
    'data': [
        
        'security/ir.model.access.csv',
        'views/project_task_view.xml',
        'views/task_type_addition.xml',
        'views/project_task_kanban.xml',
        
    ],
    # 'external_dependencies': {'python': ['api']},  # pip3 install api
    'installable': True,
    'application': True,
    'auto_install': False,
}
