# -*- coding: utf-8 -*-

{
    'name': "Aspire Attendance Extension",

    'description': """
        Hr Attendance Aspire
    """,
    'author': "Aspire Softserv Private Limited",
    'website': "http://www.aspiresoftware.in",
    'category': 'Attendance',
    'version': '15.0.0.0.4',
    'license': 'LGPL-3',
    'external_dependencies': {'python': ['openpyxl', 'pymssql']},
    # pip3 install openpyxl
    # pip3 install pymssql
    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'hr_holidays', 'hr_attendance', 'hr_timesheet_sheet_attendance'],
    # always loaded
    'data': [
        'security/user_group.xml',
        'security/ir.model.access.csv',
        'views/attendance_biometric_files_view.xml',
        # 'data/attendance_daily_summary.xml',
        # 'data/attendance_monthly_summary.xml',
        # 'data/attendance_biometric_process.xml',
        # 'data/attnedance_work_from_home.xml',
        'data/work_from_home_mail.xml',
        'data/attendance_log_cron.xml',
        'data/attendance_history_cron.xml',
        'data/attnedance_work_from_home.xml',
        # 'report/monthly_report_view.xml',
        # 'report/monthly_summary_report.xml',
        # 'report/report_paperFormat.xml',
        'report/attendance_report_daywise.xml',
        'report/attendance_summary.xml',
        'views/hr_attendance_views.xml',
        'views/attendance_log_view.xml',
        # 'views/assets_backend.xml',
        # 'views/attendance_daily_summary_view.xml',
        'views/attendance_work_from_home_view.xml',
        # 'views/attendance_monthly_summary_report.xml',
        # 'views/attendance_report.xml',
        # 'views/attendance_monthly_summary_view.xml',
        # 'views/hr_attendance_menu.xml',
        'views/attendance_corrections.xml',
        'views/connector_setup.xml',
        'views/inherit_hr_employee_view.xml',
        'views/hr_employee.xml',
        'wizard/attendance_wizard.xml',
        # 'data/attendance_setting_demo_data_view.xml',
    ],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
