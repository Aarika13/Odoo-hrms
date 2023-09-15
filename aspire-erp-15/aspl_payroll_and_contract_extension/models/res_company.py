from odoo import _, exceptions, models, api, fields
from odoo.exceptions import ValidationError

import logging

_logger = logging.getLogger(__name__)

class payslip_calculations(models.Model):
    _inherit = 'res.company'

    basicpercentage = fields.Float(string='Basic Percentage',tracking = True,help='Add percentage value like 25%')
    min_basic = fields.Float(string='Minimum Basic ',tracking = True)
    max_basic = fields.Float(string='Maximum Basic ',tracking = True)
    gratuity_percentage = fields.Float(string='Gratuity Percentage',tracking = True,help='Add percentage value like 4.81%',default = 4.81)
    gratuity_multiplier = fields.Float(string='Gratuity Multiplier',tracking = True)
    esic_ee_percentage = fields.Float(string='ESIC EE Percentage ',tracking = True,help='Add percentage value like 0.75%')
    esic_er_percentage = fields.Float(string='ESIC ER Percentage ',tracking = True,help='Add percentage value like 3.25%')
    pfpercentage = fields.Float(string='PF Percentage ',tracking = True,help='Add percentage value like 12.00%')
    pfceilingamt = fields.Float(string='PF Ceiling Limit ',tracking = True)
    esicwagelimit = fields.Float(string='ESIC wage Limit ',tracking = True)
    esicwagelimit_physical_chanllanged = fields.Float(string='ESIC wage Limit for Physically chanlanged person ',tracking = True)
    professional_tax = fields.Integer(string='Professional Tax',tracking = True)
    tax_deducted_at_source = fields.Float(string='TDS',tracking = True)
    cess = fields.Float(string='Assess (cess) ',tracking = True,help='Add percentage value like 4.00%')