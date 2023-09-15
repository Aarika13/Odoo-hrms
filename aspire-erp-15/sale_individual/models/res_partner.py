from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'


    # def action_send_email(self):
    #     print("Button for email")