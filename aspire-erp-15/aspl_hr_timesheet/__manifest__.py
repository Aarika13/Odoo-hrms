# -*- coding: utf-8 -*-
{
    'name': "Aspire Hr Timesheet ",
    'summary': """
        Modified Project and timesheets as per Aspire requirement
       """,
    'description': """
    """,
    'author': "Aspire Softserv Pvt Ltd",
    'website': "http://aspiresoftware.co.in",
    'category': 'Projects',
    'version': '15.0.0.0.0',
    'license': 'LGPL-3',
    # any module necessary for this one to work correctlyexit
    'depends': ['base','hr_attendance', 'project', 'hr', 'product','hr_timesheet_sheet','hr_timesheet_attendance','hr_timesheet_sheet_attendance'],  # , 'hr_timesheet_sheet', 'sale'
    # always loaded
    'data': [
        'security/custom_timesheet_security.xml',
        'security/ir.model.access.csv',
        'data/add_my_timesheeets_view.xml',
        # 'data/approved_employee_my_timesheet.xml',
        'views/inherit_analytic_account.xml',
        'views/inherit_hr_timesheet_sheet_view.xml', # N2F
        'views/timesheet_link_cron.xml'
    ],

}
