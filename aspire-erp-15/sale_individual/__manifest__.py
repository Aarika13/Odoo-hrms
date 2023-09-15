# -*- coding: utf-8 -*-
{
    'name': "Sales Individual",
    'version': '15.0.0.0.',
    'author': 'Aspire Softserv Private Limited',
    'category': 'Sales Individual',
    'sequence': 12,
    'summary': 'Sales Individual',
    'website': 'https://aspiresoftware.in',
    'description': """""",

    'depends': ['sale','base'],  # 'hr_holidays', 'calendar', 'resource', 'hr', 'aspl_hr_employee',
    # always loaded
    'data': [
        'views/sale_contact_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
