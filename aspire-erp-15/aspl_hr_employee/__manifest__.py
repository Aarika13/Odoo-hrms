# -*- coding: utf-8 -*-

{
    'name': "Aspire Employee",
    'version': '15.0.0.0.16',
    'description': "",
    'author': 'Aspire Softserv Private Limited',
    'website': "https://aspiresoftware.in",
    'summary': '',
    'category': 'Employee',
    'depends': ['hr', 'hr_recruitment', 'contacts',
                'hr_skills',
                'website',
                'base'
                ],
    'data': [
        'security/ir.model.access.csv',
        'data/notifier_mail_template.xml',
        'data/notifier_schedular.xml',
        'sequence/auto_id.xml',
        'wizards/employee_letter.xml',

        'views/hr_employee_view.xml',
        'views/employee_education_view.xml',
        'views/passport_visa_view.xml',
        'views/nomination_view.xml',
        'views/identity_view.xml',
        'views/hr_bank_detail_view.xml',
        'views/hr_own_employee_view.xml',
        'views/hr_all_employee_view.xml',
        'views/hr_resume_line_view.xml',
        'views/notifier_view.xml',
        'views/birth_day_view.xml',
        'views/employee_configuration.xml',
        'views/hr_employee_button.xml',
        'wizards/hr_test_wizard_view.xml',
    ],
    'installable': True,
    'sequence': 12,
    'license': 'LGPL-3',
    'auto_install': False
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
