{
    'name': "Aspire Payroll and Contract Extension",
    'version': '15.0.0.0.23',
    'description': "Using this module user will be able to modify payrolls and contracts.",
    'author': 'Aspire Softserv Private Limited',
    'website': "https://aspiresoftware.in",
    'summary': '',
    'category': 'Payroll',
    'depends': [
                'base',
                'hr_contract',
                'hr',
                'hr_holidays',
                'hr_contract_types',
                'hr_payroll_community',
                'automatic_payroll',
                'hr_payslip_monthly_report',
                'mail',
                'payroll_reports',
                ],

    'data': [
        'security/ir.model.access.csv',
        'security/custom_payslip_security.xml',
        'data/payslip_mail_data.xml',
        'data/salary_rule_data.xml',
        'views/contract_config_view.xml',
        'views/payroll_config_view.xml',
        'views/tax_calculations_view.xml',
        'views/it_declaration_schedule.xml',
        'views/it_statement_views.xml',
        'views/hr_payslip_batch_view.xml',
        'views/employee_full_final_view.xml',
        'wizards/payslip_wizard_view.xml',
        'wizards/generate_payslip_wizard_view.xml',
        'wizards/attendance_shortfall_wizard_view.xml',
        'views/payslip_modification.xml',
        'views/res_company_payroll_configuration.xml',
    ],
    'assets': {
        'web.assets_backend': [
        'aspl_payroll_and_contract_extension/static/src/css/it_statement.css',
        'aspl_payroll_and_contract_extension/static/src/js/it_statement.js',
        ],
        'web.assets_qweb': [

        'aspl_payroll_and_contract_extension/static/src/xml/it_statement.xml',
        ],
    },
    'external_dependencies': {'python': ['bs4', 'xlsxwriter']},
    'installable': True,
    'sequence': -99,
    'application': True,
    'license': 'LGPL-3',
    'auto_install': False
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
