
from odoo import models, fields, api, _

class MailComposer(models.TransientModel):
    _inherit = 'mail.template.preview'

    email_bcc = fields.Char('Bcc',compute='_compute_mail_template_fields')
