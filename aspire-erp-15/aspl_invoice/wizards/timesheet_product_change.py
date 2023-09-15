from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import timedelta, date
import logging

_logger = logging.getLogger(__name__)

class InvoiceMenu(models.Model):
    _name = "timesheet.product.change"
    _description = "Timesheet Product Change"

    def _get_project_product(self):  
        if 'product_id' in self.env.context:
            domain =[('id', 'in', self.env.context['product_id'])]
            return domain

    product_id = fields.Many2one('product.product',string='Product', required=True,domain=_get_project_product)

    def change_timesheet_product(self):
        if 'account_analytic_ids' in self.env.context:
            for analytic_line in self.env.context['account_analytic_ids']:
                analytic_line_id = self.env['account.analytic.line'].browse(analytic_line)
                analytic_line_id.write({'product_type':self.product_id.id})
