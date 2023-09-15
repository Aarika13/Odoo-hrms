# -*- coding: utf-8 -*-
{
    'name': "Aspire E-Learning Management",
    'version': '15.0.0.0.',
    'author': 'Aspire Softserv Private Limited',
    'category': 'Employee Development Resources',
    'sequence': 27,
    'summary': 'E-learning module',
    'website': 'https://aspiresoftware.in',
    'depends': ['website_slides','mass_mailing_slides'],  # report

    # always loaded
    'data': [
        
        'security/ir.model.access.csv',
        # 'data/odoo_training.xml',
        'wizard/add_content_playlist.xml',
        'views/inherit_course_view.xml',
        # 'views/hr_leave_menu.xml',

    ],
    # only loaded in demonstration mode
    'demo': [

    ],
    'license': 'LGPL-3',
    # 'installable': True,
    'application': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
