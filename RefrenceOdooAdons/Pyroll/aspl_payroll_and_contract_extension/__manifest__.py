# -*- coding: utf-8 -*-

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
                ],

    'data': [
        'security/ir.model.access.csv',
        'views/contract_config_view.xml',
        'views/payroll_config_view.xml',
        'views/tax_calculations_view.xml',
    ],
    'external_dependencies': {'python': ['bs4', 'xlsxwriter']},
    'installable': True,
    'sequence': -99,
    'application': True,
    'license': 'LGPL-3',
    'auto_install': False
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
