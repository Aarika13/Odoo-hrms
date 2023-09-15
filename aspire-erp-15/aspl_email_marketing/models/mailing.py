from odoo import models, fields, api, _


class MailingModel(models.Model):
    _inherit = 'mailing.mailing'

    def action_view_clicked_list(self):
        action = self.env["ir.actions.actions"]._for_xml_id("mass_mailing.action_view_mass_mailing_contacts")

        for rec in self:
            link_tracker_ids = self.env['link.tracker.click'].search([('mass_mailing_id', '=', rec.id)])
            mail_trace_ids = self.env['mailing.trace'].search([('id', 'in', link_tracker_ids.mailing_trace_id.ids), ('model', '=', 'mailing.contact')])
        mail_trace = mail_trace_ids.mapped('res_id')
        action['domain'] = [('id', 'in', mail_trace)]
        return action
