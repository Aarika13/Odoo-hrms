from odoo import models, fields, api, _
from datetime import datetime,timedelta
from odoo.exceptions import ValidationError



class account_payment(models.Model):
    _name='candidate.onboarding'
    _inherit = 'hr.employee'

    uid = fields.Char('Onboarding Unique Id')
    old_uid = fields.Char('Onboarding Unique Id')
    emp_onboarding = fields.Boolean('Employee on-boarding')
    candidate_id = fields.Many2one('candidate','Candidate')
    employee_id = fields.Many2one('hr.employee','Employee')
    candidate_applicant_id = fields.Many2one('hr.applicant','Applicant')
    release_candidate = fields.Boolean('Release Candidate',default=True)
    onboarding_status = fields.Selection(
        [('onprocess', 'On Process'), 
         ('reprocess', 'Re-process'),
         ('submitted', 'Submitted'), 
         ('completed', 'Approved'),
         ], 'Onboarding Status', readonly=True, default='onprocess',tracking=True)
    
    resume_line_ids = fields.One2many('hr.resume.line', 'onboarding_candidate_id', string="Resumé lines")
    employee_skill_ids = fields.One2many('hr.employee.skill', 'onboarding_candidate_id', string="Skills")
    
    employee_identity_id = fields.One2many('employee.identity', 'onboarding_candidate_id', 'Employee Identity', required=False)
    employee_document_id = fields.One2many('onboarding.document', 'onboarding_candidate_id', 'Document Detail')
    employee_document_previous_id = fields.One2many('onboarding.document', 'onboarding_candidate_id', 'Document Detail',domain=[('type','=','past')])
    employee_document_current_id = fields.One2many('onboarding.document', 'onboarding_candidate_id', 'Document Detail',domain=[('type','=','current')])
    employee_document_education_id = fields.One2many('onboarding.document', 'onboarding_candidate_id', 'Document Detail',domain=[('type','=','education')])

    per_street = fields.Char('Permanent Street',required=False)
    per_landmark = fields.Char('Permanent Landmark',tracking=True,required=False)
    per_city = fields.Char('Permanent City', size=30, help="City max size is 30",tracking=True,required=False)
    per_pcode = fields.Char('Permanent Pin code', size=6, help='Pincode max size is 6',tracking=True,required=False)
    per_state = fields.Many2one('res.country.state', 'Permanent State',tracking=True,required=False)
    per_county = fields.Many2one('res.country', 'Permanent Country',tracking=True,required=False)

    category_ids = fields.Many2many(
        'hr.employee.category', 'employee_category_rel_onboarding',
        'emp_id', 'category_id', groups="hr.group_hr_manager",
        string='Tags')

    def approve_candidate(self):
        if self.onboarding_status == 'submitted':
            self.write({'onboarding_status':'completed'})
            template_id = self.env['mail.template'].search([('name','=','Candidate On-boarding Process Complete')])

            mail_from_list = []
            attendance_manager_group_users = self.env['res.users'].search([('groups_id','=',self.env.ref('hr.group_hr_manager').sudo().id)])
            hr_employee = self.env['hr.employee'].search([('user_id','in',attendance_manager_group_users.ids),('department_id.name','=','Human Resource'),('user_id.company_ids','in',self.candidate_applicant_id.company_id.id)])
            for mail in hr_employee : mail_from_list.append(mail.work_email)
            mail_from = ','.join(mail_from_list)

            context = {
                    'mail_from':mail_from,
                }

            mail_id = template_id.with_context(context).send_mail(self.id,force_send = True)

        else:
            if self.onboarding_status == 'completed':
                raise ValidationError('Candidate already Approved.')
            else:
                raise ValidationError('Candidate must be submitted')    

        # return {
        #     'effect':{
            
        #     'fadeout':'fast',
        #     'message':'Approved successfully',
        #     'type':'rainbow_man',
        #     },
        # }

    def employee_redirect_url(self):
        if self.employee_id:
            url = self.env['ir.config_parameter'].get_param('web.base.url')
            menuId = self.env.ref('hr.menu_hr_root').id
            actionId = self.env.ref('hr.open_view_employee_list_my').id

            candidateEmployeeURL = url + '/web#id='+str(self.employee_id.id)+'&menu_id='+str(menuId)+'&action='+str(actionId)+'&model=hr.employee&view_type=form'
            return {
                'type':'ir.actions.act_url',
                'target':'self',
                'url':candidateEmployeeURL,
            }
        else:
            raise ValidationError('Employee must be created.')


    def create_employee_from_onboarding(self):
        applicant = self.candidate_applicant_id
        if self.onboarding_status == 'completed':
            if not self.employee_id:

                # Add Applicant Activity
                activity_status = self.env['mail.activity.type'].search([('name', 'ilike','joined'),('res_model','ilike','hr.applicant')])
                context = self._context
                current_uid = context.get('uid')
                user = self.env['res.users'].browse(current_uid)
                applicant.write({
                    'applicant_activity_ids':[(0,0,{
                        'activity':activity_status.id,
                        'track_date':datetime.now(),
                        'user_id':user.id,
                        'job_opening':applicant.job_opening_id.id
                    })],
                })

                """ Create an hr.employee from the hr.applicants """

                # Add Applicant Activity
                status_ = self.env['hr.recruitment.stage'].search([('name', 'ilike', 'Joined')])
                applicant.write({'stage_id':status_})
                applicant.write({'offer':'joined'})
                applicant.write({'stage_status':'joined'})

                #Employee Personal Detail
                onboarding_data = {
                    'name':self.name,
                    'gender':self.gender,
                    'birthday':str(self.birthday),
                    'emergency_phone':self.emergency_phone,
                    'emergency_contact':self.emergency_contact,
                    'per_street':self.per_street,
                    'per_landmark':self.per_landmark,
                    'per_pcode':self.per_pcode,
                    'per_city':self.per_city,
                    'per_phone1':self.per_phone1,
                    'personal_email':self.personal_email,
                    'per_state':self.per_state.id,
                    'per_county':self.per_county.id,
                    'country_id':self.country_id.id,
                    'marital':self.marital,
                    'spouse':self.spouse,
                    'marriage_date':self.marriage_date,
                    'children':self.children,
                    'blood_group':self.blood_group,
                    'religion':self.religion,
                    'international_employee':self.international_employee,
                    'physically_challenged':self.physically_challenged,
                    'pre_street':self.pre_street,
                    'pre_landmark':self.pre_landmark,
                    'pre_pcode':self.per_pcode,
                    'pre_city':self.per_city,
                    'isPresentAddSameAsPermanent':self.isPresentAddSameAsPermanent,
                    'work_email':self.work_email,
                }
                employee_id = self.env['hr.employee'].create(onboarding_data)
                self.write({'employee_id':employee_id.id})

                #create Skills dictionary
                skill_lines = []
                skill_lines_dict = []
                for skill in applicant.applicant_skill_ids:
                    skill_lines_dict.append({
                        'skill_id': skill.skill_id.id,
                        'skill_level_id': skill.skill_level_id.id,
                        'skill_type_id': skill.skill_type_id.id,
                        'level_progress': skill.level_progress,
                    })
                for skill_data in skill_lines_dict:
                    skill_lines.append([0, 0, skill_data])

                employee_data = {
                    'job_id': applicant.job_id.id,
                    'job_title': applicant.job_id.name,
                    'department_id': applicant.department_id.id or False,
                    'address_id': applicant.company_id and applicant.company_id.partner_id and applicant.company_id.partner_id.id or False,
                    # 'work_email': applicant.email_from,
                    'employee_skill_ids': skill_lines
                }
                employee_id.write(employee_data)


                #Resume Line Data
                resume_lines = []
                resume_lines_dict = []
                for resume_line in self.resume_line_ids:
                    resume_lines_dict.append({
                        'name':resume_line.name,
                        'date_start':str(resume_line.date_start),
                        'date_end':str(resume_line.date_end),
                        'display_type':resume_line.display_type,
                        'line_type_id':resume_line.line_type_id.id,
                        'relevant':resume_line.relevant,
                        'leaving_reason':resume_line.leaving_reason,
                        'percentage':resume_line.percentage,
                        'description':resume_line.description,
                        'employee_id':employee_id.id,
                    })
                for resume in resume_lines_dict:
                    resume_lines.append([0, 0, resume])
                employee_id.write({'resume_line_ids':resume_lines})


                #Empoyee Document Detail
                employee_document_dict = []
                for document in self.employee_document_id:
                    employee_document_dict.append([0,0,{
                        'document_name':document.document_name,
                        'document_type':document.document_type,
                        'document_description':document.document_description,
                        'document':document.document,
                        'attached_date':str(document.attached_date),
                        'type':document.type,
                        'doc':document.doc,
                        'employee_id':employee_id.id,
                    }])
                employee_id.write({'employee_document_id':employee_document_dict})


                #Employee Identity Detail
                identity_dict = []
                for document in self.employee_identity_id:
                    identity_dict.append([0,0,{
                        'employee_identity':document.employee_identity,
                        'complete_name':document.complete_name,
                        'aadhaar_no':document.aadhaar_no,
                        'aadhaar_name':document.aadhaar_name,
                        'aadhaar_enrolno':document.aadhaar_enrolno,
                        'ec_no':document.ec_no,
                        'ec_name':document.ec_name,
                        'passport_no':document.passport_no,
                        'passport_name':document.passport_name,
                        'expire_date':str(document.expire_date) if document.expire_date else False,
                        'pan_no':document.pan_no,
                        'pan_name':document.pan_name,
                        'bank_acc':document.bank_acc,
                        'bank_ifsc':document.bank_ifsc,
                        'bank_acc_name':document.bank_acc_name,
                        'document_verified':document.document_verified,
                        'license_name':document.license_name,
                        'license_number':document.license_number,
                        'document':document.document,
                        'document_name':document.document_name,
                        'employee_id':employee_id.id
                    }])
                employee_id.write({'employee_identity_id':identity_dict})
            if self.employee_id:
                url = self.env['ir.config_parameter'].get_param('web.base.url')
                menuId = self.env.ref('hr.menu_hr_root').id
                actionId = self.env.ref('hr.open_view_employee_list_my').id

                candidateEmployeeURL = url + '/web#id='+str(self.employee_id.id)+'&menu_id='+str(menuId)+'&action='+str(actionId)+'&model=hr.employee&view_type=form'
                return {
                    'type':'ir.actions.act_url',
                    'target':'self',
                    'url':candidateEmployeeURL,
                }
        else:
            raise ValidationError('Candidate Must be Approved.')
        

    def re_process_onboarding(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'candidate.onboarding.reprocess.wizard',
            'view_type':'form',
            'view_mode':'form',
            'name':_('Candidate On-boarding Reprocess'),
            'target':'new',
            'context': {'onboarding_candidate_id': self.id},
        }  

    


