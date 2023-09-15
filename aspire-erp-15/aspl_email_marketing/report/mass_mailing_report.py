from odoo import api, fields, models, tools, _


class MassMailingReport(models.Model):
    _name = "mass.mailing.report"
    _description = "Mail Tracking Report"
    _auto = False

    contact_name = fields.Char(string='Contact Name')
    contact_email = fields.Char(string='Contact Email')
    contact_number = fields.Char(string='Contact Number')
    mass_mail_id = fields.Many2one('mailing.mailing', "Mailing")
    campaign_id = fields.Many2one('utm.campaign', "Campaigns")
    url = fields.Char(string="URL")
    id = fields.Integer()

    def init(self):
        tools.drop_view_if_exists(self._cr, 'mass_mailing_report')
        self._cr.execute(""" CREATE OR REPLACE VIEW mass_mailing_report AS (
            select ltc.id as id, lt.url as url,
            mc.name as contact_name, 
            mc.email as contact_email, 
            mc.contact_number as contact_number, 
            mt.mass_mailing_id as mass_mail_id, 
            mt.campaign_id as campaign_id 
            from  link_tracker as lt  
            INNER JOIN link_tracker_click as ltc on lt.id = ltc.link_id 
			INNER JOIN mailing_trace as mt on mt.id = ltc.mailing_trace_id 
            INNER JOIN mailing_contact as mc on mc.id = mt.res_id 
            where mt.model = 'mailing.contact')
            """)