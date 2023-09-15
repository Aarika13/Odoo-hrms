# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class TransferToApplication(models.TransientModel):
    _name = 'refer.to.job.opening.wiz'
    _description = 'Transfer/Refer applicant to another job opening'

    job_opening_id = fields.Many2one('job.opening', string="Job Opening")
    
    def move_to_job_opening(self):
        applicant_obj = self.env['hr.applicant'].browse(self.env.context.get('active_id'))
        current_applicant_obj = applicant_obj.write({'active': False})

        hr_application = self.env['hr.applicant']
        skill_lines = []
        hr_questions = []
        for skill in self.job_opening_id.opening_skill_ids:
            skill_lines.append([0, 0, {
                'skill_id': skill.skill_id.id,
                'skill_level_id': skill.skill_level_id.id,
                'skill_type_id': skill.skill_type_id.id,
                'level_progress': skill.level_progress,
            }])

        if applicant_obj.questions_ids:
            for questions in applicant_obj.questions_ids:
                hr_questions.append([0, 0, {
                    'name': questions.name,
                    'ans': questions.ans
                }])
        if hr_application.search([('active', 'in', [True])]).filtered(lambda p: p.candidate_id.id == applicant_obj.candidate_id.id):
            pass
        else:
            applicant = hr_application.create({
                    'name': applicant_obj.candidate_id.name,
                    'candidate_id': applicant_obj.candidate_id.id,
                    'partner_name': applicant_obj.candidate_id.name,
                    'email_from': applicant_obj.candidate_id.email,
                    'partner_mobile': applicant_obj.candidate_id.mobile,
                    'total_exp_years': applicant_obj.candidate_id.total_exp_years,
                    'current_company_id': applicant_obj.candidate_id.current_company_id.id,
                    'current_ctc': applicant_obj.candidate_id.salary_current,
                    'salary_expected': applicant_obj.candidate_id.salary_expected,
                    'type_id': applicant_obj.type_id.id,
                    'source_id': applicant_obj.source_id.id,
                    'categ_ids': applicant_obj.categ_ids.ids,
                    'job_id': self.job_opening_id.job_id.id,
                    'department_id': self.job_opening_id.department_id.id,
                    'stage_id': self.env.ref('aspl_hr_recruitment.initial').id,
                    'user_id': self.job_opening_id.user_id.id,
                    'interviewers_ids': self.job_opening_id.user_id.ids,
                    'reviewer_user_ids': self.job_opening_id.user_id.ids,
                    'referred_id': applicant_obj.user_id.partner_id.id,
                    'job_opening_id': self.job_opening_id.id,
                    'private_note': applicant_obj.private_note,
                    'date_received': applicant_obj.date_received
                })
            applicant.update({'applicant_skill_ids': skill_lines})
            if hr_questions:
                applicant.update({'questions_ids': hr_questions})
            applicant_obj.candidate_id.in_application = True

