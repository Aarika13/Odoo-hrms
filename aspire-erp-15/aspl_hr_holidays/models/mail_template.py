from odoo import models, fields, api, _


class MailTemplate(models.Model):
    _inherit = 'mail.template'

    email_bcc = fields.Char("Bcc")

    def generate_email(self, res_ids, fields):
        fields.append('email_bcc')
        return super(MailTemplate ,self).generate_email(res_ids, fields)
    
class MailMail(models.Model):
    _inherit = 'mail.mail'

    email_bcc = fields.Char("Bcc")

    @api.model
    def create(self, vals):
        if self.env.context.get('with_bcc') and self.env.context.get('with_email_bcc'):
            vals['email_bcc'] = self.env.context.get('with_email_bcc')
        return super(MailMail, self).create(vals)

class IrMailServer(models.Model):
    _inherit = "ir.mail_server"

    def build_email(self, email_from, email_to, subject, body, email_cc=None, email_bcc=None, reply_to=False,
                attachments=None, message_id=None, references=None, object_id=False, subtype='plain', headers=None,
                body_alternative=None, subtype_alternative='plain'):
        email_bcc = email_bcc and (email_bcc + ',' + self.env.context.get('with_email_bcc')) or self.env.context.get('with_email_bcc')

        return super().build_email(email_from, email_to, subject, body, email_cc, email_bcc, reply_to,
                attachments, message_id, references, object_id, subtype, headers,
                body_alternative, subtype_alternative)
