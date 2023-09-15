# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models, _


class TransferToApplication(models.TransientModel):
    _name = 'transfer.to.application'
    _description = 'Transfer candidate to application'

    job_opening_id = fields.Many2one('job.opening', string="Job Opening")

    def transfer_to_application(self):
        for record in self:
            hr_application = self.env['hr.applicant']
            res_partner = self.env['res.partner'].browse(self.env.context.get('active_ids'))
            job_opening_obj = self.env['job.opening'].browse(record.job_opening_id.id)
            skill_lines = []
            # applicant_activity_list = []
            for skill in job_opening_obj.opening_skill_ids:
                skill_lines.append([0, 0, {
                    'skill_id': skill.skill_id.id,
                    'skill_level_id': skill.skill_level_id.id,
                    'skill_type_id': skill.skill_type_id.id,
                    'level_progress': skill.level_progress,
                }])
            # applicant_activity_list.append([0, 0, {
            #     'new_stage_id': self.env.ref('aspl_hr_recruitment.initial').id,
            #     'track_date': datetime.now(),
            # }])
            for rec in res_partner:
                if hr_application.search([('active', 'in', [True])]).filtered(lambda p: p.candidate_id.id == rec.id):
                    pass
                else:
                    applicant = hr_application.create({
                        'name': rec.name,
                        'candidate': rec.id,
                        'partner_name': rec.name,
                        'email_from': rec.email,
                        'partner_phone': rec.phone,
                        'partner_mobile': rec.mobile,
                        'type_id': rec.type_id.id,
                        'source_id': rec.source_id.id,
                        'categ_ids': rec.categ_ids.ids,
                        'job_id': job_opening_obj.job_id.id,
                        'department_id': job_opening_obj.department_id.id,
                        'stage_id': self.env.ref('aspl_hr_recruitment.initial').id,
                        'user_id': job_opening_obj.user_id.id,
                        'job_opening_id': record.job_opening_id.id,
                        'private_note': rec.private_note,
                        'date_received': rec.date_received,
                        'total_exp_years': rec.total_exp_years,
                        'is_partner': True,
                        # 'message_main_attachment_id': rec.message_main_attachment_id.id,
                    })
                    applicant.update({'applicant_skill_ids': skill_lines})
                    rec.in_application = True
                    rec.is_applicant = True
                    rec.is_candidate = True
                    rec.is_employee = False
                    rec.active_employee = False
                    # applicant.update({'applicant_activity_ids': applicant_activity_list})

                    context = self._context
                    current_uid = context.get('uid')
                    user = self.env['res.users'].browse(current_uid)
                    activity_status = self.env['mail.activity.type'].search([('name', '=',applicant.stage_id.name),('res_model','ilike','hr.applicant')])
                    applicant.write({
                        'applicant_activity_ids':[(0,0,{
                            'activity':activity_status.id,
                            'track_date':datetime.now(),
                            'user_id':user.id,
                            'job_opening':job_opening_obj.id
                        })],
                    })


class AspireTransferToApplication(models.TransientModel):
    _name = 'aspire.transfer.to.application'
    _description = 'Transfer candidate to application'

    job_opening_id = fields.Many2one('job.opening', string="Job Opening")

    def aspire_transfer_to_application(self):
        for record in self:
            hr_application = self.env['hr.applicant']
            res_partner = self.env['candidate'].browse(self.env.context.get('active_ids'))
            job_opening_obj = self.env['job.opening'].browse(record.job_opening_id.id)
            skill_lines = []
            # applicant_activity_list = []
            for skill in job_opening_obj.opening_skill_ids:
                skill_lines.append([0, 0, {
                    'skill_id': skill.skill_id.id,
                    'skill_level_id': skill.skill_level_id.id,
                    'skill_type_id': skill.skill_type_id.id,
                    'level_progress': skill.level_progress,
                }])
            # applicant_activity_list.append([0, 0, {
            #     'new_stage_id': self.env.ref('aspl_hr_recruitment.initial').id,
            #     'track_date': datetime.now(),
            # }])
            for rec in res_partner:
                if hr_application.search([('active', 'in', [True])]).filtered(lambda p: p.candidate_id.id == rec.id):
                    pass
                else:
                    applicant = hr_application.create({
                        'name': rec.name,
                        'candidate_id': rec.id,
                        'partner_name': rec.name,
                        'email_from': rec.email,
                        'partner_mobile': rec.mobile,
                        'type_id': rec.type_id.id,
                        'source_id': rec.source_id.id,
                        'categ_ids': rec.categ_ids.ids,
                        'job_id': job_opening_obj.job_id.id,
                        'department_id': job_opening_obj.department_id.id,
                        'stage_id': self.env.ref('aspl_hr_recruitment.initial').id,
                        'user_id': job_opening_obj.user_id.id,
                        'job_opening_id': record.job_opening_id.id,
                        'private_note': rec.private_note,
                        'date_received': rec.date_received,
                        'total_exp_years': rec.total_exp_years,
                        'is_candidate': True,
                        'current_ctc':rec.salary_current,
                        'total_exp':rec.total_exp,
                        'salary_expected':rec.salary_expected,
                        'current_location_city':rec.current_location_city.id,
                        'year_of_passing':rec.year_of_passing,
                        'referred_id':rec.partner_id.id,
                        'current_company_id':rec.current_company_id.id,
                        'description':rec.description,
                        # 'message_main_attachment_id': rec.message_main_attachment_id.id,
                    })
                    applicant.update({'applicant_skill_ids': skill_lines})
                    rec.in_application = True
                    rec.is_applicant = True
                    rec.is_candidate = True
                    rec.is_employee = False
                    rec.active_employee = False
                    # applicant.update({'applicant_activity_ids': applicant_activity_list})
                    # initial_activity_banned = self.env['hr.applicant'].search([('job_id')])
                    # if applicant.source_id != self.env['utm.source'].search([('name', '=', 'Email')]):
                    context = self._context
                    current_uid = context.get('uid')
                    user = self.env['res.users'].browse(current_uid)
                    activity_status = self.env['mail.activity.type'].search([('name', '=',applicant.stage_id.name),('res_model','ilike','hr.applicant')])
                    application_count = self.env['hr.applicant'].search_count([('candidate_id', '=', rec.id), ('active', 'in', [True, False])])
                    if not applicant.source_id.id == self.env['utm.source'].search([('name', '=', 'Email')]).id and not application_count > 1:
                        applicant.write({
                            'applicant_activity_ids':[(0,0,{
                                'activity':activity_status.id,
                                'track_date':datetime.now(),
                                'user_id':user.id,
                                'job_opening':job_opening_obj.id,
                                'activity_source_count':False,
                                })],
                            })
                    else:
                         applicant.write({
                            'applicant_activity_ids':[(0,0,{
                                'activity':activity_status.id,
                                'track_date':datetime.now(),
                                'user_id':user.id,
                                'job_opening':job_opening_obj.id,
                                'activity_source_count':True,
                                })],
                            })
                    
  

