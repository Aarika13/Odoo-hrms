from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class clm_lead_enhancement(models.Model):
    _inherit = "crm.lead"
    _order="write_date desc"

    linked_in_profile = fields.Char(string="LinkedIn Profile")
    followup_id = fields.Many2one('crm.followup',string="Followup")
    followup_start_date = fields.Date(string="Followup Start Date")
    last_followup_send_date = fields.Date(string="Last Followup Send Date")
    followup_replay_date = fields.Date(string="Followup Replay Date")
    source_by = fields.Many2one('res.users',string="Source By")
    direction = fields.Selection([
        ('inbound', 'Inbound'),
        ('outbound', 'Outbound'),
    ], string="Direction", default='inbound')
