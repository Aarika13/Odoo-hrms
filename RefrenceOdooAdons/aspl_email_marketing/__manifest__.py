# -*- coding: utf-8 -*-

{
    'name': "Aspire Email Marketing",
    'version': '15.0.0.0.23',
    'description': "Using this module user will be able to modify email marketing.",
    'author': 'Aspire Softserv Private Limited',
    'website': "https://aspiresoftware.in",
    'summary': '',
    'category': 'Payroll',
    'depends': [
                'base',
                'mail',
                'mass_mailing',
                ],

    'data': [
            'views/mailing_modification_view.xml'
    ],
    'external_dependencies': {'python': ['bs4', 'xlsxwriter']},
    'installable': True,
    'sequence': -99,
    'application': True,
    'license': 'LGPL-3',
    'auto_install': False
}
