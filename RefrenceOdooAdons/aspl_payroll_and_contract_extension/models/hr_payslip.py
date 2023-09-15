from odoo import _, exceptions, models, api, fields
from datetime import date
import logging

_logger = logging.getLogger(__name__)

class payslip_calculations(models.Model):
    _inherit = 'hr.payslip'

    tax_regime = fields.Selection([('old_regime','Old'),('new_regime','New')],string='Regime')
    grand_total = fields.Float(string="Total",default=0)

    def get_projected_taxable_income_all(self):
        payslip_components = {}
        for payslip in self:
            lines = self._get_payslip_lines(payslip.contract_id.ids, payslip.id)
            for line in lines:
                code = line.get('code')
                amount = line.get('amount')
                if code in payslip_components :
                    payslip_components[code] = payslip_components[code] + amount
                else :
                    payslip_components[code] = amount
        return payslip_components