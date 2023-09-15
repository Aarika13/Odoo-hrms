# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime

class HrQuestionsWiz(models.TransientModel):
    _name = 'hr.questions.wiz'
    _description = 'HR Questions Popup'

    questions_ids = fields.One2many('hr.questions.line.wiz', 'hr_que_id', string="HR Questions")

    def update_que_ans(self):
        hr_applicant = self.env['hr.applicant'].browse(self._context.get('active_id'))
        question_lines = []
        for rec in self.questions_ids:
            question_lines.append((0, 0,
                                   {'name': rec.name,
                                    'ans': rec.ans
                                    }))
        return hr_applicant.write({'questions_ids': question_lines})


class HrQuestionsLineWiz(models.TransientModel):
    _name = 'hr.questions.line.wiz'
    _description = 'HR Questions Lines'

    hr_que_id = fields.Many2one('hr.questions.wiz', string="HR Question")
    name = fields.Char('Question')
    ans = fields.Char('Answer')
    active = fields.Boolean('Active', default=True)


class ApplicantGetRefuseReason(models.TransientModel):
    _inherit = 'applicant.get.refuse.reason'

    def action_refuse_reason_apply(self):
        res = super(ApplicantGetRefuseReason, self).action_refuse_reason_apply()
        app_id = self.env.context.get('active_id')
        candidate = self.env['hr.applicant'].search([('id', '=', app_id)])
        candidate.write({'refused_date':datetime.now()})
        candidate_skills = [] 
        for skills in candidate.applicant_skill_ids:
            if skills.level_progress != 0:
                print("skills.level_progress",skills.level_progress)
                candidate.candidate_id.write({'candidate_skill_ids': False})
                skills_dict = {'skill_type_id': skills.skill_type_id.id,
                            'skill_id': skills.skill_id.id,
                            'skill_level_id': skills.skill_level_id.id,
                            'level_progress': skills.level_progress,
                            }
                candidate_skills.append([0, 0, skills_dict])
        candidate.candidate_id.write({
            'candidate_skill_ids': candidate_skills,
        })
        return res
