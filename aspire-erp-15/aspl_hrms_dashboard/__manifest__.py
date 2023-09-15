{
    'name': "ASPL HR Dashboard",
    'version': '15.0.1.1.0',
    'summary': """Open HRMS - HR Dashboard""",
    'description': """Open HRMS - HR Dashboard""",
    'category': 'Generic Modules/Human Resources',
    'author': 'Aspire SoftServe PVT. LTD.,Open HRMS',
    'company': 'Aspire SoftServe PVT. LTD.',
    'maintainer': 'Aspire SoftServe PVT. LTD.',
    'website': "https://www.aspiresoftserv.com/",
    'depends': ['website','hr','hr_contract','hr_holidays','hr_timesheet','hr_attendance','hr_timesheet_attendance','aspl_hr_employee','aspl_hr_recruitment', 'account', 'hr_payroll_community', 'base'],
    # 'external_dependencies': {
    #     'python': ['pandas'],
    # },
    'data': [
        'security/ir.model.access.csv',
        'views/dashboard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [

            'aspl_hrms_dashboard/static/src/css/hr_dashboard.css',
            'aspl_hrms_dashboard/static/src/css/recruitment_dashboard.css',
            'aspl_hrms_dashboard/static/src/css/aspl_account_admin_dashboard.css',
            'aspl_hrms_dashboard/static/src/css/lib/nv.d3.css',
            'aspl_hrms_dashboard/static/src/js/hr_dashboard.js',
            'aspl_hrms_dashboard/static/src/js/recruitment_dashboard.js',
            'aspl_hrms_dashboard/static/src/js/aspl_account_admin_dashboard.js',
            'aspl_hrms_dashboard/static/src/js/lib/d3.min.js',
        ],
        'web.assets_qweb': [
            'aspl_hrms_dashboard/static/src/xml/hr_dashboard.xml',
            'aspl_hrms_dashboard/static/src/xml/recruitment_dashboard.xml',
            'aspl_hrms_dashboard/static/src/xml/aspl_account_admin_dashboard.xml',
        ],
    },

    'license': "AGPL-3",
    'installable': True,
    'application': True,
    "sequence" : -100,

}
