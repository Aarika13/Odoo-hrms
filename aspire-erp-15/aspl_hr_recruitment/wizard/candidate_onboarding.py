
from odoo import api, fields, models, _
from odoo.http import request
import werkzeug.urls
import json
import requests
import string
import random
import logging

_logger = logging.getLogger(__name__)

class CandidareOnboardingWizard(models.TransientModel):
    _name = 'candidate.onboarding.wizard'
    _description = 'Candidate Onboarding Wizard'

    def _set_default_url(self):
        if 'applicant_id' in self.env.context:
            url = request.env['ir.config_parameter'].get_param('web.base.url')
            applicant_id = self.env['hr.applicant'].browse(self.env.context['applicant_id'])
            
            candidate = request.env['candidate'].sudo().search([('id','=',applicant_id.candidate_id.id)])
            onboarding_emp_id = request.env['candidate.onboarding'].search([('candidate_id','=',candidate.id)])
            _logger.info('onboarding_emp_id == == == %s %s',onboarding_emp_id, onboarding_emp_id.name) 

            if onboarding_emp_id:
                query_string = werkzeug.urls.url_encode({'uid':onboarding_emp_id.uid})
                return url + "/onboarding?" + query_string
            else:
                
                res = ''.join(random.choices(string.ascii_uppercase +
                             string.digits, k=50))
                params = {
                    'uid':res
                }   
                query_string = werkzeug.urls.url_encode(params)
                
                emp_dict = {
                    'name':candidate.name,
                    'personal_email':candidate.email,
                    'per_phone1':(candidate.mobile).strip()[-10::1],
                    'candidate_id':candidate.id,
                    'candidate_applicant_id':applicant_id.id,
                    'uid':res,
                    'onboarding_status':'onprocess',
                }

                _logger.info("Emp Dictionary == == == %s",emp_dict)
                try:
                    self.env['candidate.onboarding'].create(emp_dict)
                except Exception as e:
                    _logger.info("Reason of onboarding candidate creation failure == == == %s",e)


                return url + "/onboarding?" + query_string


    url = fields.Char('url',default =lambda self: self._set_default_url())


    def send_mail_onboarding(self):
        if 'applicant_id' in self.env.context:
            applicant_id = self.env['hr.applicant'].search([('id','=',self.env.context['applicant_id'])])
            template_id = self.env['mail.template'].search([('name','=','Candidate Onboarding Process')])

            context = self._context
            current_uid = context.get('uid')
            user = self.env['res.users'].browse(current_uid)

            mail_from_list = []
            attendance_manager_group_users = self.env['res.users'].search([('groups_id','=',self.env.ref('hr.group_hr_manager').sudo().id)])
            hr_employee = self.env['hr.employee'].search([('user_id','in',attendance_manager_group_users.ids),('department_id.name','=','Human Resource'),('user_id.company_ids','in',applicant_id.company_id.id)])
            for mail in hr_employee : mail_from_list.append(mail.work_email)
            mail_from = ','.join(mail_from_list)
            
            context = {
                'user':user.name,
                'url':self.url,
                'applicant_id':applicant_id,
                'mail_from':mail_from
            }
    
            mail_id = template_id.with_context(context).send_mail(applicant_id.id,force_send = True)



class CandidareOnboardingReprocessWizard(models.TransientModel):
    _name = 'candidate.onboarding.reprocess.wizard'
    _description = 'candidate Onboarding Reprocess Wizard'

    onboarding_changes = fields.Html('Description')


    def send_mail_onboarding(self):
        
        if 'onboarding_candidate_id' in self.env.context:
            onboarding_candidate_id = self.env['candidate.onboarding'].search([('id','=',self.env.context['onboarding_candidate_id'])])
            template_id = self.env['mail.template'].search([('name','=','Candidate On-boarding Reprocess')])
            
            url = request.env['ir.config_parameter'].get_param('web.base.url')

            
            if onboarding_candidate_id.old_uid:
                query_string = werkzeug.urls.url_encode({'uid':onboarding_candidate_id.uid})
            else:
                onboarding_candidate_id.write({'old_uid':onboarding_candidate_id.uid})
                res = ''.join(random.choices(string.ascii_uppercase + string.digits, k=50))
                query_string = werkzeug.urls.url_encode({'uid':res})
                onboarding_candidate_id.write({'uid':res})
            
            onboarding_url = url + "/onboarding?" + query_string
            context = self._context
            current_uid = context.get('uid')
            user = self.env['res.users'].browse(current_uid)

            mail_from_list = []
            attendance_manager_group_users = self.env['res.users'].search([('groups_id','=',self.env.ref('hr.group_hr_manager').sudo().id)])
            hr_employee = self.env['hr.employee'].search([('user_id','in',attendance_manager_group_users.ids),('department_id.name','=','Human Resource'),('user_id.company_ids','in',onboarding_candidate_id.candidate_applicant_id.company_id.id)])
            for mail in hr_employee : mail_from_list.append(mail.work_email)
            mail_from = ','.join(mail_from_list)

            
            context = {
                'user':user.name,
                'url':onboarding_url,
                'description':self.onboarding_changes,
                'mail_from':mail_from,
            }
            
            mail_id = template_id.with_context(context).send_mail(onboarding_candidate_id.id,force_send = True)
            onboarding_candidate_id.write({'onboarding_status':'reprocess'})          
            