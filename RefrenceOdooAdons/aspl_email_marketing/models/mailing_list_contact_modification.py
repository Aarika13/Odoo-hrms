from odoo import models, fields, api, _
from datetime import date
import logging

_logger = logging.getLogger(__name__)

class mailing__list_contact_modification(models.Model):
    _inherit = 'mailing.contact'
    
    website_url = fields.Char(string="Company Website")
    linkedin_id = fields.Char(string="LinkedIn Profile")
    contact_number = fields.Float(string="Contact Number")

    def generate_lead(self):
        lead_generation = self.env['crm.lead'].search([('mail_id','=',self.id)])
        _logger.info("lead_generationXyy: %s", self.id)

        if not lead_generation:
            vals= ({
                    'name':self.name,
                    'email_from':self.email,
                    'partner_name':self.company_name,
                    'website':self.website_url,
                    'mobile':self.contact_number,
                    'mail_id' : self.id,
                    'linked_in_profile' :self.linkedin_id
                    })
            lead_generation.create(vals)
    

    def lead(self):
        lead_generation = self.env['crm.lead'].search([('mail_id','=',self.id)])
        url = self.env['ir.config_parameter'].get_param('web.base.url') 
        menuId = self.env.ref('crm.crm_menu_root').id 
        print("menuId1",menuId)
        actionId = self.env.ref('crm.crm_lead_all_leads').id
        crm_url = url + '/web#id='+str(lead_generation.id)+'&menu_id='+str(menuId)+'&action='+str(actionId)+'&model=hr.employee&view_type=form' 
        return { 'type':'ir.actions.act_url', 
                'target':'self', 
                'url':crm_url, }