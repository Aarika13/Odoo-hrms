from odoo import models, fields, api, _
from datetime import date
import logging

_logger = logging.getLogger(__name__)

class mailing__list_contact_modification(models.Model):
    _inherit = 'mailing.contact'
    
    website_url = fields.Char(string="Company Website")
    linkedin_id = fields.Char(string="LinkedIn Profile")
    contact_number = fields.Char(string="Contact Number")

    def generate_lead(self):
        lead_generation = self.env['crm.lead'].search([('email_from','=',self.email)])
        _logger.info("lead_generationXyy: %s", self.id)

        if not lead_generation:
            vals= ({
                    'name':self.name,
                    'email_from':self.email,
                    'partner_name':self.company_name,
                    'website':self.website_url,
                    'mobile':self.contact_number,
                    #'mail_id' : self.id,
                    'linked_in_profile' :self.linkedin_id
                    })
            lead_generation.create(vals)
    

    def lead(self):
        lead_generation = self.env['crm.lead'].search([('email_from','=',self.email)])
        url = self.env['ir.config_parameter'].get_param('web.base.url') 
        menuId = self.env.ref('crm.crm_menu_root').id 
        print("menuId1",menuId)
        actionId = self.env.ref('crm.crm_lead_all_leads').id
        crm_url = url + '/web#id='+str(lead_generation.id)+'&menu_id='+str(menuId)+'&action='+str(actionId)+'&model=hr.employee&view_type=form' 
        return {'res_model': 'crm.lead', 'type': 'ir.actions.act_window','name': _("Leads"),'domain': [('email_from', '=', self.email)],'view_mode': 'tree,form',}
        #return { 'type':'ir.actions.act_url', 
        #        'target':'self', 
        #        'url':crm_url, }
        #return { 'type': 'ir.actions.act_window','res_model': 'crm.lead', 
        #         'view_type':'tree', 'view_mode':'tree', 'id':_('crm.crm_lead_all_leads'), 
        #         'context': {'email_from': [self.email]}, }
        #view = 'crm.crm_lead_all_leads' if self.use_leads else 'crm.crm_lead_opportunities'
        #action = self.env.ref(view).sudo().read()[0]
        #action['view_mode'] = 'tree,kanban,graph,pivot,form,calendar'
        #action['domain'] = [('source_id', 'in', self.source_id.ids)]
        #action['context'] = {'active_test': False, 'create': False}
        #return action
