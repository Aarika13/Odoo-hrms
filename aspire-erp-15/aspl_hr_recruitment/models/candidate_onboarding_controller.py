from odoo import http
from odoo import models, fields, api, _
from odoo.http import request
from datetime import datetime
import base64
import re
import mimetypes
from urllib.parse import urlencode
import json


class EmployeeSkill(models.Model):
    _inherit = 'hr.employee.skill'

    onboarding_candidate_id = fields.Many2one('candidate.onboarding', 'Onbording Candidate',required=True, ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', required=False, ondelete='cascade')

class EmployeeIdentity(models.Model):
    _inherit = "employee.identity"

    onboarding_candidate_id = fields.Many2one('candidate.onboarding', 'Onbording Candidate')

CURRENT_DOCUMENTS = [
    ('appointment', 'Appointment'),
    ('appraisal', 'Appraisal'),
    ('confirmation', 'Confirmation'),
    ('nomination','Nomination'),
    ('exitForm', 'Exit Form'),
    ('experience', 'Experience'),
    ('offer', 'Offer'),
    ('paySlip', 'Pay Slip'),
    ('relieving', 'Relieving'),
    ('other', 'Other'),
]   

class EmployeeDocument(models.Model):
    _name = "onboarding.document"
    _description = "Onboarding Document"

    onboarding_candidate_id = fields.Many2one('candidate.onboarding', 'Onbording Candidate')
    onboarding_connector = fields.Char("Onboarding_connector")
    document_name = fields.Char('Attachment Name', required=True)
    document_type = fields.Selection([
        ('pdf', 'PDF'),
        ('word', 'Word'),
        ('other', 'Other'),
    ], 'Document Type', required=True)
    document_description = fields.Text('Description')
    document = fields.Binary('Document', required=True)
    attached_date = fields.Date('Attached Date', default=fields.Date.context_today)
    type = fields.Selection(string='Type',
                            selection=[('past', 'Previous employment'),
                                       ('current', 'Current employment'),
                                       ('education', 'Education'),
                                       ],
                            required=True)
    doc = fields.Selection(CURRENT_DOCUMENTS, 'Document', required=True)
class HrResumeLine(models.Model):
    _inherit = 'hr.resume.line'

    onboarding_candidate_id = fields.Many2one('candidate.onboarding','Onbording Candidate')
    employee_id = fields.Many2one('hr.employee', required=False, ondelete='cascade')
    onboarding_connector = fields.Char("Onboarding_connector")

class Employee(models.Model):
    _inherit = 'hr.employee'

    onboarding_candidate_id = fields.Many2one('candidate.onboarding','Onbording Candidate')
    
 


class CandidateOnboard(http.Controller):
    
    def preFilledDataEduIdentity(self,onboarding_emp_id):

        line_type_id = request.env['hr.resume.line.type'].sudo().search([('name','=','Education')])
        candidate_eductaion_resume_id = request.env['hr.resume.line'].sudo().search([('onboarding_candidate_id','=',onboarding_emp_id.id),('line_type_id','=',line_type_id.id)])
        response = {}
        eduFlag = 1
        for candidate_eductaion_resume in candidate_eductaion_resume_id:
            response['eduction_degree' + str(eduFlag)] = candidate_eductaion_resume.name
            response['education_start_date' + str(eduFlag)] = str(candidate_eductaion_resume.date_start)
            response['education_end_date' + str(eduFlag)] = str(candidate_eductaion_resume.date_end)
            response['eduction_degree_id' + str(eduFlag)] = candidate_eductaion_resume.id

            edcuation_resume_document = request.env['onboarding.document'].sudo().search([('document_name','=',candidate_eductaion_resume.name),('onboarding_candidate_id','=',onboarding_emp_id.id)])
            eduFlag += 1
            # response['education_attchment' + str(eduFlag)] = edcuation_resume_document.document
        
        
        identityFlag = 1
        candidate_identity_id = request.env['employee.identity'].sudo().search([('onboarding_candidate_id','=',onboarding_emp_id.id)])
        for candidate_identity in candidate_identity_id:
            if candidate_identity.employee_identity == 'aadhaar':
                response['identity_doc_no' + str(identityFlag)] =candidate_identity.aadhaar_no
                response['identity_doc_name' + str(identityFlag)] =candidate_identity.aadhaar_name

            elif candidate_identity.employee_identity == 'election_card':
                response['identity_doc_no' + str(identityFlag)] =candidate_identity.ec_no
                response['identity_doc_name' + str(identityFlag)] =candidate_identity.ec_name

            elif candidate_identity.employee_identity == 'account_number':
                response['identity_doc_no' + str(identityFlag)] =candidate_identity.pan_no
                response['identity_doc_name' + str(identityFlag)] =candidate_identity.pan_name
    
            response['identity_type'+str(identityFlag)] = candidate_identity.employee_identity
            response['identity_type_id' + str(identityFlag)] = candidate_identity.id

            # response['identity_attchment' + str(identityFlag)] = candidate_identity.document
            identityFlag += 1
        return response
    
    def preFilledDataPreviousExperience(self,onboarding_emp_id):
        #Data For Prefilled Document
        response = {}
        # preEmpFlag = 1
        # previous_employment_doc_id = request.env['onboarding.document'].sudo().search([('type','=','past'),('onboarding_candidate_id','=',onboarding_emp_id.id),('doc','!=','experience')])
        # for previous_employment_doc in previous_employment_doc_id:
        #     response['previous_emp_doc_type' + str(preEmpFlag)] = previous_employment_doc.doc
        #     response['previous_emp_doc_type_id' + str(preEmpFlag)] = previous_employment_doc.id
        #     preEmpFlag += 1
        
        expFlag = 1

        line_type_id = request.env['hr.resume.line.type'].sudo().search([('name','=','Experience')])
        candidate_experience_id = request.env['hr.resume.line'].sudo().search([('onboarding_candidate_id','=',onboarding_emp_id.id),('line_type_id','=',line_type_id.id)])
        for candidate_experience in candidate_experience_id:
            response['exp_company' + str(expFlag)] = candidate_experience.name
            response['exp_start_date' + str(expFlag)] = str(candidate_experience.date_start)
            response['exp_end_date' + str(expFlag)] = str(candidate_experience.date_end)
            response['exp_company_id' + str(expFlag)] = candidate_experience.id

            preEmpFlag = 1
            connection = candidate_experience.onboarding_connector
            previous_employment_doc_id = request.env['onboarding.document'].sudo().search([('onboarding_connector','like',connection)])
            for previous_employment_doc in previous_employment_doc_id:
                response['experience'+ str(expFlag) + '_previous_emp_doc_type' + str(preEmpFlag)] = previous_employment_doc.doc
                response['experience'+ str(expFlag) + '_previous_emp_doc_type_id' + str(preEmpFlag)] = previous_employment_doc.id
                preEmpFlag += 1
    
            expFlag += 1
        return response
    
    @http.route('/onboarding',type='http',auth='public',website = True,csrf = False)
    def index(self,**kwargs):
        onboarding_emp_id = request.env['candidate.onboarding'].sudo().search([('uid','=',kwargs['uid'])])
        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])

        if onboarding_emp_id.onboarding_status != 'submitted' and  'country' in kwargs and not 'section_id' in kwargs :#onboarding_emp_id.onboarding_status != 'submitted' and  
            states = request.env['res.country.state'].sudo().search([('country_id','=',int(kwargs['country']))])
            response = {
                'states': [{'id': s.id, 'name': s.name} for s in states],
                }
            return json.dumps(response)
        
        if onboarding_emp_id.onboarding_status != 'submitted' and  'precountry' in kwargs and not 'section_id' in kwargs :#onboarding_emp_id.onboarding_status != 'submitted' and  
            states = request.env['res.country.state'].sudo().search([('country_id','=',int(kwargs['precountry']))])
            response = {
                'states': [{'id': s.id, 'name': s.name} for s in states],
                }
            if 'prestate' in kwargs and kwargs['prestate']:
                prestate = request.env['res.country.state'].sudo().search([('id','=',int(kwargs['prestate']))])
                response['prestate'] = [{'id': s.id, 'name': s.name} for s in prestate]
            return json.dumps(response)
        
        # Record Store while click next On Personal Information Section
        if onboarding_emp_id.onboarding_status != 'submitted' and 'section_id' in kwargs and kwargs['section_id'] == 'presonalInfoOnboarding':#onboarding_emp_id.onboarding_status != 'submitted' and 
            county_id = request.env['res.country'].sudo().search([('id','=',kwargs['country'])])
            state_id = request.env['res.country.state'].sudo().search([('id','=',kwargs['state'])])

            data = {}

            if onboarding_emp_id.name and not onboarding_emp_id.name == (kwargs['first_name'] + ' ' + kwargs['last_name']):
                data['name'] = kwargs['first_name'] + ' ' + kwargs['last_name']

            if not onboarding_emp_id.per_street or (onboarding_emp_id.per_street and not onboarding_emp_id.per_street == kwargs['street1']):
                data['per_street'] = kwargs['street1']

            if not onboarding_emp_id.per_landmark or (onboarding_emp_id.per_landmark and not onboarding_emp_id.per_landmark == kwargs['landmark']):
                data['per_landmark'] = kwargs['landmark']

            if not onboarding_emp_id.per_pcode or (onboarding_emp_id.per_pcode and not onboarding_emp_id.per_pcode == kwargs['postal']):
                data['per_pcode'] = kwargs['postal']    

            if not onboarding_emp_id.per_city or (onboarding_emp_id.per_city and not onboarding_emp_id.per_city == kwargs['city']):
                data['per_city'] = kwargs['city']

            if not onboarding_emp_id.per_phone1 or (onboarding_emp_id.per_phone1 and not onboarding_emp_id.per_phone1 == kwargs['mobile_no']):
                data['per_phone1'] = kwargs['mobile_no']

            if not onboarding_emp_id.emergency_phone or (onboarding_emp_id.emergency_phone and not onboarding_emp_id.emergency_phone == kwargs['emergency_no']):
                data['emergency_phone'] = kwargs['emergency_no']
            if not onboarding_emp_id.emergency_contact  or (onboarding_emp_id.emergency_contact and not onboarding_emp_id.emergency_contact == kwargs['emergency_no_name']):
                data['emergency_contact'] = kwargs['emergency_no_name']

            if not onboarding_emp_id.personal_email or (onboarding_emp_id.personal_email and not onboarding_emp_id.personal_email == kwargs['email']):
                data['personal_email'] = kwargs['email']
                
            if not onboarding_emp_id.birthday or (onboarding_emp_id.birthday and not str(onboarding_emp_id.birthday) == kwargs['birthday']):
                data['birthday'] = kwargs['birthday']

            if not onboarding_emp_id.gender or (onboarding_emp_id.gender and not onboarding_emp_id.gender == kwargs['gender']):
                data['gender'] = kwargs['gender']

            if not onboarding_emp_id.blood_group or (onboarding_emp_id.blood_group and not onboarding_emp_id.blood_group == kwargs['blood_group']):
                data['blood_group'] = kwargs['blood_group']

            if not onboarding_emp_id.per_state or (onboarding_emp_id.per_state and not onboarding_emp_id.per_state.id == int(kwargs['state'])):
                data['per_state'] = int(kwargs['state'])

            if not onboarding_emp_id.per_county or (onboarding_emp_id.per_county and not onboarding_emp_id.per_county.id == int(kwargs['country'])):
                data['per_county'] = int(kwargs['country'])


            if not onboarding_emp_id.pre_street or (onboarding_emp_id.pre_street and not onboarding_emp_id.pre_street == kwargs['prestreet1']):
                data['pre_street'] = kwargs['prestreet1']

            if not onboarding_emp_id.pre_landmark or (onboarding_emp_id.pre_landmark and not onboarding_emp_id.pre_landmark == kwargs['prelandmark']):
                data['pre_landmark'] = kwargs['prelandmark']

            if not onboarding_emp_id.pre_pcode or (onboarding_emp_id.pre_pcode and not onboarding_emp_id.pre_pcode == kwargs['prepostal']):
                data['pre_pcode'] = kwargs['prepostal']    

            if not onboarding_emp_id.pre_city or (onboarding_emp_id.pre_city and not onboarding_emp_id.pre_city == kwargs['precity']):
                data['pre_city'] = kwargs['precity']

            if not onboarding_emp_id.pre_state or (onboarding_emp_id.pre_state and not onboarding_emp_id.pre_state.id == int(kwargs['prestate'])):
                data['pre_state'] = int(kwargs['prestate'])

            if not onboarding_emp_id.pre_county or (onboarding_emp_id.pre_county and not onboarding_emp_id.pre_county.id == int(kwargs['precountry'])):
                data['pre_county'] = int(kwargs['precountry'])

            if not onboarding_emp_id.isPresentAddSameAsPermanent or (onboarding_emp_id.isPresentAddSameAsPermanent and not str(onboarding_emp_id.isPresentAddSameAsPermanent) == (kwargs['isPresentSameAsPermanent']).capitalize()):
                if (kwargs['isPresentSameAsPermanent']).capitalize() == 'True':
                    data['isPresentAddSameAsPermanent'] = True
                else:
                    data['isPresentAddSameAsPermanent'] = False   
            if data:
                onboarding_emp_id.write(data)

            
            #Data For Prefilled Document
            response = self.preFilledDataEduIdentity(onboarding_emp_id)

            return json.dumps(response)

        elif onboarding_emp_id.onboarding_status != 'submitted' and 'section_id' in kwargs and kwargs['section_id'] == 'eduIdenPage':#onboarding_emp_id.onboarding_status != 'submitted' and
            line_type_id = request.env['hr.resume.line.type'].sudo().search([('name','=','Education')])
            storeEduDetailFlag = 1
            while 'eduction_degree' + str(storeEduDetailFlag) in kwargs:
                if kwargs['eduction_degree_id'+str(storeEduDetailFlag)]:

                    education_record_id = request.env['hr.resume.line'].sudo().search([('id','=',kwargs['eduction_degree_id'+str(storeEduDetailFlag)])])
                    if education_record_id:
                        education_record_document_id = request.env['onboarding.document'].sudo().search([('document_name','=',education_record_id.name),('type','=','education'),('onboarding_candidate_id','=',onboarding_emp_id.id)])
                    if education_record_id and (education_record_id.name != kwargs['eduction_degree' + str(storeEduDetailFlag)]):
                        education_record_id.write({'name':kwargs['eduction_degree' + str(storeEduDetailFlag)]})
                        education_record_document_id.write({'document_name':kwargs['eduction_degree' + str(storeEduDetailFlag)]})

                    if education_record_id and (str(education_record_id.date_start) != kwargs['education_start_date'+ str(storeEduDetailFlag)]):
                        education_record_id.write({'date_start':kwargs['education_start_date'+ str(storeEduDetailFlag)]})

                    if education_record_id and (str(education_record_id.date_end) != kwargs['education_end_date'+ str(storeEduDetailFlag)]):
                        education_record_id.write({'date_start':kwargs['education_start_date'+ str(storeEduDetailFlag)]})

                    if education_record_id and not kwargs['education_attchment'+str(storeEduDetailFlag)] == 'undefined':
                        attachment_file = kwargs['education_attchment' + str(storeEduDetailFlag)]
                        attachment_file_name = kwargs.get('education_attchment'+str(storeEduDetailFlag)).filename
                        attachment_read = attachment_file.read()
                        mimetype = mimetypes.guess_type(attachment_file_name)[0] if attachment_file_name else ''

                        document_dict = {
                            'document_type':'pdf' if 'pdf' in (mimetype).lower() else 'word' if 'word' in (mimetype).lower() else 'other',
                            'document':base64.b64encode(attachment_read),
                            'attached_date':datetime.today(),
                        }
                        
                        education_record_document_id.write(document_dict)
                else: 
                    attachment_file = kwargs['education_attchment' + str(storeEduDetailFlag)]
                    attachment_file_name = kwargs.get('education_attchment'+str(storeEduDetailFlag)).filename
                    attachment_read = attachment_file.read()
                    mimetype = mimetypes.guess_type(attachment_file_name)[0] if attachment_file_name else ''
                    
                    #Document 
                    document_dict = {
                        'doc' : 'other',
                        'document_type':'pdf' if 'pdf' in (mimetype).lower() else 'word' if 'word' in (mimetype).lower() else 'other',
                        'document':base64.b64encode(attachment_read),
                        'attached_date':datetime.today(),
                        'document_name':kwargs['eduction_degree' + str(storeEduDetailFlag)],
                        'type':'education',
                    }
                    
                    #Resume
                    resume_dict = {
                        'name':kwargs['eduction_degree' + str(storeEduDetailFlag)],
                        'date_start':kwargs['education_start_date'+ str(storeEduDetailFlag)],
                        'date_end':kwargs['education_end_date' + str(storeEduDetailFlag)],
                        'display_type':'classic',
                        'line_type_id':line_type_id.id,
                        'onboarding_candidate_id':onboarding_emp_id.id,
                    }
                    onboarding_emp_id.write({
                        'employee_document_id':[(0,0,document_dict)],
                        'resume_line_ids':[(0,0,resume_dict)]
                    })
                storeEduDetailFlag +=1

            storeIdeDetailFlag = 1
            while 'identity_type' + str(storeIdeDetailFlag) in kwargs:

                if kwargs['identity_type_id'+str(storeIdeDetailFlag)]:
                    identity_type_id = request.env['employee.identity'].sudo().search([('id','=',kwargs['identity_type_id'+str(storeIdeDetailFlag)])])
                    # if identity_type_id and identity_type_id.
                    if identity_type_id.employee_identity == 'aadhaar':
                        if identity_type_id.aadhaar_name != kwargs['identity_doc_name' + str(storeIdeDetailFlag)]:
                            identity_type_id.write({'aadhaar_name':kwargs['identity_doc_name' + str(storeIdeDetailFlag)]})  
                        if identity_type_id.aadhaar_no != kwargs['identity_doc_no' + str(storeIdeDetailFlag)]:
                            identity_type_id.write({'aadhaar_no':kwargs['identity_doc_no' + str(storeIdeDetailFlag)],
                                                    'complete_name':'Aadhaar Card [' + kwargs['identity_doc_no' + str(storeIdeDetailFlag)] + ' ] '})
                    if identity_type_id.employee_identity == 'election_card':
                        if identity_type_id.ec_name != kwargs['identity_doc_name' + str(storeIdeDetailFlag)]:
                            identity_type_id.write({'ec_name':kwargs['identity_doc_name' + str(storeIdeDetailFlag)]})
                        if identity_type_id.ec_no != kwargs['identity_doc_no' + str(storeIdeDetailFlag)]:
                            identity_type_id.write({'ec_no':kwargs['identity_doc_no' + str(storeIdeDetailFlag)]})
                            identity_type_id.write({'complete_name':'Election Card [' + kwargs['identity_doc_no' + str(storeIdeDetailFlag)] + ' ] '})
                    if identity_type_id.employee_identity == 'account_number':
                        if identity_type_id.pan_name != kwargs['identity_doc_name' + str(storeIdeDetailFlag)]:
                            identity_type_id.write({'pan_name':kwargs['identity_doc_name' + str(storeIdeDetailFlag)]})
                        if identity_type_id.pan_no != kwargs['identity_doc_no' + str(storeIdeDetailFlag)]:
                            identity_type_id.write({'pan_no':kwargs['identity_doc_no' + str(storeIdeDetailFlag)]})
                            identity_type_id.write({'complete_name':'Pan Number[' + kwargs['identity_doc_no' + str(storeIdeDetailFlag)] + ' ] '})
                    if identity_type_id and not kwargs['identity_attachment'+str(storeIdeDetailFlag)] == 'undefined':
                        attachment_file = kwargs['identity_attachment' + str(storeIdeDetailFlag)]
                        attachment_file_name = kwargs.get('identity_attachment'+str(storeIdeDetailFlag)).filename
                        attachment_read = attachment_file.read()
                        mimetype = mimetypes.guess_type(attachment_file_name)[0] if attachment_file_name else ''

                        document_dict = {
                            'document':base64.b64encode(attachment_read),
                        }
                        education_record_document_id.write(document_dict)  
             

                else:
                    attachment_file = kwargs['identity_attachment' + str(storeIdeDetailFlag)]
                    attachment_file_name = kwargs.get('identity_attachment'+str(storeIdeDetailFlag)).filename
                    attachment_read = attachment_file.read()
                    mimetype = mimetypes.guess_type(attachment_file_name)[0] if attachment_file_name else ''

                    if kwargs['identity_type' + str(storeIdeDetailFlag)] == 'aadhaar':
                        document_dict = {
                            'complete_name' : 'Aadhaar Card [' + kwargs['identity_doc_no' + str(storeIdeDetailFlag)] + ' ] ',
                            'document_name':attachment_file_name,
                            'document':base64.b64encode(attachment_read),
                            'employee_identity':'aadhaar',
                            'aadhaar_no':int(kwargs['identity_doc_no' + str(storeIdeDetailFlag)]),
                            'aadhaar_name':kwargs['identity_doc_name' + str(storeIdeDetailFlag)],
                        }

                    elif kwargs['identity_type' + str(storeIdeDetailFlag)] == 'election_card':
                        document_dict = {
                            'complete_name' : 'Election Card [' + kwargs['identity_doc_no' + str(storeIdeDetailFlag)] + ' ] ',
                            'document_name':attachment_file_name,
                            'document':base64.b64encode(attachment_read),
                            'employee_identity':'election_card',
                            'ec_no':kwargs['identity_doc_no' + str(storeIdeDetailFlag)],
                            'ec_name':kwargs['identity_doc_name' + str(storeIdeDetailFlag)],
                        }

                    elif kwargs['identity_type' + str(storeIdeDetailFlag)] == 'account_number':
                        document_dict = {
                            'complete_name' : 'Pan Number[' + kwargs['identity_doc_no' + str(storeIdeDetailFlag)] + ' ] ',
                            'document_name':attachment_file_name,
                            'document':base64.b64encode(attachment_read),
                            'employee_identity':'account_number',
                            'pan_no':kwargs['identity_doc_no' + str(storeIdeDetailFlag)],
                            'pan_name':kwargs['identity_doc_name' + str(storeIdeDetailFlag)],
                        }

                    onboarding_emp_id.write({
                        'employee_identity_id':[(0,0,document_dict)],
                    })
                storeIdeDetailFlag += 1             
                       

            response = self.preFilledDataPreviousExperience(onboarding_emp_id)

            return json.dumps(response)
        
        elif onboarding_emp_id and onboarding_emp_id.onboarding_status != 'submitted' and  not 'section_id' in kwargs and not 'recordId' in kwargs:#onboarding_emp_id.onboarding_status != 'submitted' and  
            data= {
                'uid':kwargs['uid'],
                'countries':countries,
            }

            if onboarding_emp_id.name:
                data['first_name'] = (onboarding_emp_id.name).split(" ")[0]
                data['last_name'] = (onboarding_emp_id.name).split(" ")[1]

            if onboarding_emp_id.per_street:
                data['street1'] = onboarding_emp_id.per_street

            if onboarding_emp_id.per_landmark:
                data['landmark'] = onboarding_emp_id.per_landmark

            if onboarding_emp_id.per_pcode:
                data['postal'] = onboarding_emp_id.per_pcode    

            if onboarding_emp_id.per_city:
                data['city'] = onboarding_emp_id.per_city

            if onboarding_emp_id.per_phone1:
                data['mobile_no'] = onboarding_emp_id.per_phone1

            if onboarding_emp_id.emergency_phone:
                data['emergency_no'] = onboarding_emp_id.emergency_phone
            if onboarding_emp_id.emergency_contact:
                data['emergency_no_name'] = onboarding_emp_id.emergency_contact

            if onboarding_emp_id.personal_email:
                data['email'] = onboarding_emp_id.personal_email
                
            if onboarding_emp_id.birthday:
                data['birthday'] = onboarding_emp_id.birthday

            if onboarding_emp_id.gender:
                data['gender'] = onboarding_emp_id.gender

            if onboarding_emp_id.per_county:
                data['country'] = onboarding_emp_id.per_county

                if onboarding_emp_id.per_state:
                    data['state'] = onboarding_emp_id.per_state
                    data['states'] = states = request.env['res.country.state'].sudo().search([('country_id','=',onboarding_emp_id.per_county.id)])
            else:
                data['states'] = ''  


            if onboarding_emp_id.pre_street:
                data['prestreet1'] = onboarding_emp_id.pre_street

            if onboarding_emp_id.pre_landmark:
                data['prelandmark'] = onboarding_emp_id.pre_landmark

            if onboarding_emp_id.pre_pcode:
                data['prepostal'] = onboarding_emp_id.pre_pcode 

            if onboarding_emp_id.pre_city:
                data['precity'] = onboarding_emp_id.pre_city

            if onboarding_emp_id.blood_group:
                data['blood_group'] = onboarding_emp_id.blood_group   

            if onboarding_emp_id.pre_county:
                data['precountry'] = onboarding_emp_id.pre_county

                if onboarding_emp_id.pre_state:
                    data['prestate'] = onboarding_emp_id.pre_state
                    data['states2'] = states = request.env['res.country.state'].sudo().search([('country_id','=',onboarding_emp_id.pre_county.id)])
            else:
                data['states2'] = ''     

            if onboarding_emp_id.isPresentAddSameAsPermanent:
                data['samePresentPermanent'] = onboarding_emp_id.isPresentAddSameAsPermanent 

            return request.render('aspl_hr_recruitment.candidate_onboarding_template',data)
        
        elif onboarding_emp_id and onboarding_emp_id.onboarding_status != 'submitted' and  'recordId' in kwargs:#onboarding_emp_id.onboarding_status != 'submitted' and 
            if kwargs['model'] in ('education','experience'):
                resume_record_id = request.env['hr.resume.line'].sudo().search([('id','=',kwargs['recordId'])])
                if resume_record_id and kwargs['model'] == 'education':
                    education_record_document_id = request.env['onboarding.document'].sudo().search([('document_name','=',resume_record_id.name),('type','=','education'),('onboarding_candidate_id','=',onboarding_emp_id.id)])
                    education_record_document_id.unlink()
                    resume_record_id.unlink()
                elif resume_record_id and kwargs['model'] == 'experience':
                    
                    education_record_document_id = request.env['onboarding.document'].sudo().search([('onboarding_connector','like',resume_record_id.onboarding_connector)])
                    if education_record_document_id:
                        education_record_document_id.unlink()
                    resume_record_id.unlink()    
            elif kwargs['model'] == 'identity':
                candidate_identity_id = request.env['employee.identity'].sudo().search([('id','=',kwargs['recordId'])])
                candidate_identity_id.unlink()
            elif kwargs['model'] == 'previous':
                previous_employment_doc_id = request.env['onboarding.document'].sudo().search([('id','=',kwargs['recordId'])])
                previous_employment_doc_id.unlink()
        else: 
            return request.render('aspl_hr_recruitment.candidate_onboarding_after_apply_page')
        

class CandidateOnboardReceive(http.Controller):        

    def add_education_profile(self,onboarding_emp_id,kwargs):
        education_flag = 'eduction_degree' + str(1)
        flag = 1
        line_type_id = request.env['hr.resume.line.type'].sudo().search([('name','=','Education')])
    
        while education_flag in kwargs:

            attachment_file = kwargs['education_attchment' + str(flag)]
            attachment_file_name = kwargs.get('education_attchment'+str(flag)).filename
            attachment_read = attachment_file.read()
            mimetype = mimetypes.guess_type(attachment_file_name)[0] if attachment_file_name else ''
            
            #Document 
            document_dict = {
                'doc' : 'other',
                'document_type':'pdf' if 'pdf' in (mimetype).lower() else 'word' if 'word' in (mimetype).lower() else 'other',
                'document':base64.b64encode(attachment_read),
                'attached_date':datetime.today(),
                'document_name':kwargs[education_flag],
                'type':'education',
            }
            
            #Resume
            resume_dict = {
                'name':kwargs[education_flag],
                'date_start':kwargs['education_start_date'+ str(flag)],
                'date_end':kwargs['education_end_date' + str(flag)],
                'display_type':'classic',
                'line_type_id':line_type_id.id,
                'onboarding_candidate_id':onboarding_emp_id.id,
            }
            onboarding_emp_id.write({
                'employee_document_id':[(0,0,document_dict)],
                'resume_line_ids':[(0,0,resume_dict)]
            })
            flag += 1
            education_flag = 'eduction_degree' + str(flag)


    def add_identity_document(self,onboarding_emp_id,kwargs):
        flag = 1


        while 'identity_type' + str(flag) in kwargs:

            attachment_file = kwargs['identity_attachment' + str(flag)]
            attachment_file_name = kwargs.get('identity_attachment'+str(flag)).filename
            attachment_read = attachment_file.read()
            mimetype = mimetypes.guess_type(attachment_file_name)[0] if attachment_file_name else ''

            if kwargs['identity_type' + str(flag)] == 'aadhaar':
                document_dict = {
                    'complete_name' : 'Aadhaar Card [' + kwargs['identity_doc_no' + str(flag)] + ' ] ',
                    'document_name':attachment_file_name,
                    'document':base64.b64encode(attachment_read),
                    'employee_identity':'aadhaar',
                    'aadhaar_no':kwargs['identity_doc_no' + str(flag)],
                    'aadhaar_name':kwargs['identity_doc_name' + str(flag)],
                }

            elif kwargs['identity_type' + str(flag)] == 'election_card':
                document_dict = {
                    'complete_name' : 'Election Card [' + kwargs['identity_doc_no' + str(flag)] + ' ] ',
                    'document_name':attachment_file_name,
                    'document':base64.b64encode(attachment_read),
                    'employee_identity':'election_card',
                    'ec_no':kwargs['identity_doc_no' + str(flag)],
                    'ec_name':kwargs['identity_doc_name' + str(flag)],
                }

            elif kwargs['identity_type' + str(flag)] == 'account_number':
                document_dict = {
                    'complete_name' : 'Pan Number[' + kwargs['identity_doc_no' + str(flag)] + ' ] ',
                    'document_name':attachment_file_name,
                    'document':base64.b64encode(attachment_read),
                    'employee_identity':'account_number',
                    'pan_no':kwargs['identity_doc_no' + str(flag)],
                    'pan_name':kwargs['identity_doc_name' + str(flag)],
                }

            onboarding_emp_id.write({
                'employee_identity_id':[(0,0,document_dict)],
            })
            flag += 1


    def add_previous_company_document(self,onboarding_emp_id,kwargs,experience_number,company):
        flag = 1
        line_type_id = request.env['hr.resume.line.type'].sudo().search([('name','=','Experience')])
        
        
        experience_company = request.env['hr.resume.line'].search([('name','=',company),('line_type_id','=',line_type_id.id),('onboarding_candidate_id','=',onboarding_emp_id.id)])
        while experience_number + '_previous_emp_doc_type' + str(flag) in kwargs:
            if kwargs[experience_number + '_previous_emp_doc_type_id'+str(flag)] and not kwargs[experience_number + '_previous_emp_doc_type_id'+str(flag)] == 'undefined':
                id_doc = int(kwargs[experience_number + '_previous_emp_doc_type_id'+str(flag)])
                previous_employment_doc_id = request.env['onboarding.document'].sudo().search([('id','=',id_doc)])
                if kwargs.get(experience_number +'_pervious_emp_doc_attachment'+str(flag)).filename:
                        attachment_file = kwargs[experience_number +'_pervious_emp_doc_attachment' + str(flag)]
                        attachment_file_name = kwargs.get(experience_number +'_pervious_emp_doc_attachment'+str(flag)).filename
                        attachment_read = attachment_file.read()
                        mimetype = mimetypes.guess_type(attachment_file_name)[0] if attachment_file_name else ''

                        document_dict = {
                            'document':base64.b64encode(attachment_read),
                            'doc' : kwargs[experience_number +'_previous_emp_doc_type' + str(flag)],
                            'document_type':'pdf' if 'pdf' in (mimetype).lower() else 'word' if 'word' in (mimetype).lower() else 'other',
                            'document':base64.b64encode(attachment_read),
                            'attached_date':datetime.today(),
                            'document_name':kwargs[experience_number +'_previous_emp_doc_type' + str(flag)] + '_' + company,
                            'type':'past',
                            'onboarding_connector':experience_company.onboarding_connector + '_previous_emp_doc' + str(flag)
                        }
                        previous_employment_doc_id.write(document_dict)
            else:
                attachment_file = kwargs[experience_number +'_pervious_emp_doc_attachment' + str(flag)]
                attachment_file_name = kwargs.get(experience_number +'_pervious_emp_doc_attachment'+str(flag)).filename
                attachment_read = attachment_file.read()
                mimetype = mimetypes.guess_type(attachment_file_name)[0] if attachment_file_name else ''
 
                document_dict = {
                    'doc' : kwargs[experience_number +'_previous_emp_doc_type' + str(flag)],
                    'document_type':'pdf' if 'pdf' in (mimetype).lower() else 'word' if 'word' in (mimetype).lower() else 'other',
                    'document':base64.b64encode(attachment_read),
                    'attached_date':datetime.today(),
                    'document_name':kwargs[experience_number +'_previous_emp_doc_type' + str(flag)] + '_' + company,
                    'type':'past',
                    'onboarding_connector':experience_company.onboarding_connector + '_previous_emp_doc' + str(flag)
                }

                onboarding_emp_id.write({
                    'employee_document_id':[(0,0,document_dict)],
                })
            flag += 1 


    def add_experience(self,onboarding_emp_id,kwargs):
        flag = 1
        line_type_id = request.env['hr.resume.line.type'].sudo().search([('name','=','Experience')])
        while 'exp_company' + str(flag) in kwargs:
            experience_number = 'experience'+ str(flag)
            company = kwargs['exp_company' + str(flag)]
            if kwargs['exp_company_id' + str(flag)]:
                experience_record_id = request.env['hr.resume.line'].sudo().search([('id','=',kwargs['exp_company_id'+str(flag)])])
                if experience_record_id:
                    experience_record_document_id = request.env['onboarding.document'].sudo().search([('document_name','=',experience_record_id.name),('onboarding_candidate_id','=',onboarding_emp_id.id),('doc','=','experience')])
                
                if experience_record_id and (experience_record_id.name != kwargs['exp_company' + str(flag)]):
                    experience_record_id.write({'name':kwargs['exp_company' + str(flag)]})
                    # experience_record_document_id.write({'document_name':kwargs['exp_company' + str(flag)]})

                if experience_record_id and (str(experience_record_id.date_start) != kwargs['exp_start_date'+ str(flag)]):
                    experience_record_id.write({'date_start':kwargs['exp_start_date'+ str(flag)]})

                if experience_record_id and (str(experience_record_id.date_end) != kwargs['exp_end_date'+ str(flag)]):
                    experience_record_id.write({'date_end':kwargs['exp_end_date'+ str(flag)]})

                self.add_previous_company_document(onboarding_emp_id,kwargs,experience_number,company)
            else:    
                # attachment_file = kwargs['experience_attchment' + str(flag)]
                # attachment_file_name = kwargs.get('experience_attchment'+str(flag)).filename
                # attachment_read = attachment_file.read()
                # mimetype = mimetypes.guess_type(attachment_file_name)[0] if attachment_file_name else ''
                
                # #Document 
                # document_dict = {
                #     'doc' : 'experience',
                #     'document_type':'pdf' if 'pdf' in (mimetype).lower() else 'word' if 'word' in (mimetype).lower() else 'other',
                #     'document':base64.b64encode(attachment_read),
                #     'attached_date':datetime.today(),
                #     'document_name':kwargs['exp_company' + str(flag)],#+ ' Experience Letter'
                #     'type':'past',
                # }
                
                #Resume
                resume_dict = {
                    'name':kwargs['exp_company' + str(flag)],
                    'date_start':kwargs['exp_start_date'+ str(flag)],
                    'date_end':kwargs['exp_end_date' + str(flag)],
                    'display_type':'classic',
                    'line_type_id':line_type_id.id,
                    'onboarding_candidate_id':onboarding_emp_id.id,
                    'onboarding_connector':experience_number
                }

                onboarding_emp_id.write({
                    # 'employee_document_id':[(0,0,document_dict)],
                    'resume_line_ids':[(0,0,resume_dict)]
                })

                experience_record_id = request.env['hr.resume.line'].sudo().search([('onboarding_candidate_id','=',onboarding_emp_id.id)],order="create_date desc",limit=1)
                experience_record_id.write({
                    'onboarding_connector':experience_number + str(experience_record_id.id)
                })

                #previous Document Dictionary
                self.add_previous_company_document(onboarding_emp_id,kwargs,experience_number,company)

            flag += 1




            
  

    @http.route('/onboarding/record/',auth='public',website = True,csrf = False)
    def generate_onboarding_record(self,**kwargs):
        if 'uid' in kwargs:
            onboarding_emp_id = request.env['candidate.onboarding'].sudo().search([('uid','=',kwargs['uid'])])
            
            if onboarding_emp_id:
                # self.add_previous_company_document(onboarding_emp_id,kwargs)
                self.add_experience(onboarding_emp_id,kwargs)
                onboarding_emp_id.write({
                    'onboarding_status':'submitted',
                })

                url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
                menuId = request.env.ref('hr_recruitment.menu_hr_recruitment_root').sudo().id
                actionId = request.env.ref('aspl_hr_recruitment.candidate_onboarding_detail_view').sudo().id

                onboardingCandidateURL = url + '/web#id='+str(onboarding_emp_id.id)+'&menu_id='+str(menuId)+'&action='+str(actionId)+'&model=candidate.onboarding&view_type=form'
                
                mail_to_list = []
                attendance_manager_group_users = request.env['res.users'].search([('groups_id','=',request.env.ref('hr.group_hr_manager').sudo().id)])
                hr_employee = request.env['hr.employee'].search([('user_id','in',attendance_manager_group_users.ids),('department_id.name','=','Human Resource'),('user_id.company_ids','in',onboarding_emp_id.candidate_applicant_id.company_id.id)])
                for mail in hr_employee : mail_to_list.append(mail.work_email)
                mail_to = ','.join(mail_to_list)

                context = {
                    'onboardingCandidateURL':onboardingCandidateURL,
                    'mail_to':mail_to,
                }
                template_id = request.env['mail.template'].sudo().search([('name','=','Candidate Onboarding Process Submit Form')])
                mail_id = template_id.with_context(context).send_mail(onboarding_emp_id.id,force_send = True)

            else:
                return request.render('aspl_hr_recruitment.candidate_onboarding_after_apply_page')

            return request.render('aspl_hr_recruitment.candidate_onboarding_submission',{})
        else:
            return request.render('aspl_hr_recruitment.candidate_onboarding_after_apply_page')
