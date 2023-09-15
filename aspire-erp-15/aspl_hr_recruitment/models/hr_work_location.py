from odoo import models, fields, api, _


class WorkLocation(models.Model):
    _inherit = 'hr.work.location'

    gmap_url = fields.Char('Google Map URL', tracking=True)