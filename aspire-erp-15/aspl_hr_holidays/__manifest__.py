# -*- coding: utf-8 -*-
{
    'name': "Aspire Leave Management",
    'version': '15.0.0.0.',
    'author': 'Aspire Softserv Private Limited',
    'category': 'Human Resources',
    'sequence': 27,
    'summary': 'Holidays, Allocation and Leave Requests',
    'website': 'https://aspiresoftware.in',
    'description': """
Manage leaves and allocation requests
=====================================

This application controls the holiday schedule of your company. It allows employees to request holidays. Then,
 managers can review requests for holidays and approve or reject them. 
 This way you can control the overall holiday planning for the company or department.

You can configure several kinds of leaves (sickness, holidays, paid days, ...) and allocate leaves 
to an employee or department quickly using allocation requests. An employee can also make a request 
for more days off by making a new Allocation. It will increase the total of available days for that 
leave type (if the request is accepted).

You can keep track of leaves in different ways by following reports: 

* Leaves Summary
* Leaves by Department
* Leaves Analysis

A synchronization with an internal agenda (Meetings of the CRM module) is also possible in order to automatically 
create a meeting when a holiday request is accepted by setting up a type of meeting in Leave Type.
""",

    'depends': ['hr_holidays', 'calendar', 'resource', 'hr', 'aspl_hr_employee'],  # report

    # always loaded
    'data': [
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        'data/add_leaves.xml',
        'data/hr_holidays_data.xml',
        'data/leave_mail.xml',
        'views/hr_holiday_view.xml',
        'views/hr_leave_menu.xml',
        'views/inherit_res_company.xml',
        'views/hr_holidays_status_view.xml',
        'views/hr_employee_view.xml',
        'views/hr_public_holiday.xml',
        'views/mail_template.xml',
        # 'views/hr_add_holidays_view.xml',
        'wizard/hr_employee_forward_leave_wizard.xml',
        'wizard/leave_wizard_view.xml',
        'wizard/mail_template_preview.xml',
        # 'report/page_format_hr_holiday_report.xml',
        # 'report/leave_summary_report_template.xml',

    ],
    # only loaded in demonstration mode
    'demo': [

    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
