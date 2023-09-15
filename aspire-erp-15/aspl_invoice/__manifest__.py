# -*- coding: utf-8 -*-

{
    'name': "Aspire Invoicing Extension",
    'version': '15.0.0.0.23',
    'author': 'Aspire Softserv Private Limited',
    'website': "https://aspiresoftware.in",
    'summary': '',
    'category': 'Invoicing',
    'depends': ['base','account','payment','hr_timesheet_sheet','aspl_hr_timesheet','l10n_in'],
    'data': [
        'security/ir.model.access.csv',
        'views/inherit_account_invoice_line_view.xml',
        'views/account_analytic_line_inherit.xml',
        'wizards/hr_timesheet_wiz_project.xml',
        'wizards/product_change_timesheet.xml',
        'views/res_partner_inherit.xml',
        'views/inherit_product_views.xml',
        'views/payment_swift_details_view.xml',
        'views/inherit_res_company.xml',
        'views/inherit_account_invoice_view.xml',
        'views/inherit_account_payment_term_view.xml',
        'views/inherit_account_payment_view.xml',
        'report/time_and_material_invoice_report.xml',
        'report/bank_details.xml'
    ],
    # "assets": {
    #     "web.assets_common": [
    #         "aspl_invoice/static/src/css/custom_report.css",
    #         "https://fonts.googleapis.com/css?family=Droid+Sans",
    #         "aspl_invoice/static/src/css/invoice_time_and_material_report.css"
    #     ],
    # },
    'installable': True,
    'sequence': -99,
    'application': True,
    'license': 'LGPL-3',
    'auto_install': False
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
