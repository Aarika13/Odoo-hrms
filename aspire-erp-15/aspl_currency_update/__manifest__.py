# -*- coding: utf-8 -*-

{
    'name': "Currency Rate Update",

    'summary': "Update exchange rates from Exchangereates(APILayer)",

    'description': """
    """,

    'author': "Aspire Softserv Private Limited",
    'website': "http://www.aspiresoftware.in",
    'category': 'Accounting',
    'version': '0.0.9',

    'depends': ['base', 'account'],

    # always loaded
    'data': [ 
        'views/conversion_update.xml',
        'views/currency_settings.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'sequence': 12,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
