import requests
from odoo import models, fields, api, _


class Currency_Settings(models.TransientModel):
    _inherit = "res.config.settings"
    _name = "res.config.settings"

     
    api_key = fields.Char("API Key", related='company_id.api_key' , readonly= False)

    interval_number = fields.Integer(
        string="Scheduled update interval", related='company_id.interval_number', readonly= False)

    interval_type = fields.Selection(
        string="Units of scheduled update interval",
        related='company_id.interval_type',
        selection=[("minutes", "Minute(s)"),("hours", "Hour(s)"),("days", "Day(s)"), ("weeks", "Week(s)"), ("months", "Month(s)")],
        readonly= False
    )

    @api.model
    def create(self,vals):
        scheduler_settings = self.env['ir.cron'].search([('name','=','Currency Rates Update Everyday')])
        scheduler_settings.write({'interval_number':vals.get('interval_number')})
        scheduler_settings.write({'interval_type': vals.get('interval_type')})
       
        return super(Currency_Settings, self).create(vals)

class Currency_Update(models.Model):
    _inherit = "res.currency.rate"
    
    current_company_currency =  fields.Many2one('res.currency',  string="Base Currency")







