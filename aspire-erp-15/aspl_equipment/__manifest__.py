# -*- coding: utf-8 -*-

{
    'name': "Aspire Equipment Extension",

    'summary': """Equipments, Assets, Internal Hardware, Allocation Tracking""",

    'description': """
        Track employees' equipment and manage maintenance requests.
    """,

    'author': "Aspire Softserv Private Limited",
    'website': "http://www.aspiresoftware.in",
    'category': 'Manufacturing',
    'version': '15.0.0.0.8',

    'depends': ['base',
                'hr_maintenance'],

    # always loaded
    'data': [
        'security/groups_rules.xml',
        'security/ir.model.access.csv',
        # 'views/hr_equipment_report_view.xml',
        'views/hr_equipment_out_ward_stock_view.xml',
        'views/hr_equipment_available_stock_view.xml',
        'views/hr_equipment_view.xml',
        'data/in_warranty.xml',
        'data/auto_id.xml',
        'data/hr_equipment_data_view.xml',
        'wizard/replace_wiz.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'sequence': 12,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
