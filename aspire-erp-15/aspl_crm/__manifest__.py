# -*- coding: utf-8 -*-

{
    'name': "Aspire CRM Extension",

    'summary': """CRM Tools""",

    'description': """
    """,

    'author': "Aspire Softserv Private Limited",
    'website': "http://www.aspiresoftware.in",
    'category': 'Sales',
    'version': '15.0.0.0.8',

    'depends': ['base',
                'crm', 'mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/followup_schedular.xml',
        'views/crm_views.xml',
        'views/blocked_emails.xml',
        'views/crm_lead.xml',
        'views/crm_followup_view.xml'
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'sequence': 12,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
