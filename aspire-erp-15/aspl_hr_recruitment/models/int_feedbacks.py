# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import datetime
import json
from odoo.http import request


class IntFeedbacks(models.Model):
    _name = 'int.feedbacks'
    _description = 'Interviewers Feedbacks for the applicant'
    _rec_name = 'interviewer_id'

    def _domain_get_interviewers(self):
        interviewers = self.env.ref('aspl_hr_recruitment.group_recruiter_user').users.ids
        return [('active', '=', True), ('id', 'in', interviewers)]
    job_opening_id = fields.Many2one('job.opening', "Job Opening")
    interviewer_id = fields.Many2one('res.users', "Interviewer",
                              domain=_domain_get_interviewers, default=lambda self: self.env.user)
    applicant_id = fields.Many2one('hr.applicant', ondelete='cascade', string='Applicant')
    date = fields.Date('Date', default=fields.Date.today())
    interview_date = fields.Datetime('Interview Date', default=fields.Datetime.now)
    interview_time = fields.Integer('Interview Time (Min)', required=True)
    status = fields.Selection([('selected', 'Selected'),
                               ('rejected', 'Rejected'),
                               ('onhold', 'On Hold'),
                               ('n/a', 'N/A')], 'Result') #, default='rejected
    comment = fields.Text('Comments')
    feedbacks_skill_ids = fields.One2many('int.feedbacks.skill', 'int_feed_id', string="Skills",default =lambda self: self._get_feedback_skill())
    refuse_reason = fields.Many2one('hr.applicant.refuse.reason','Refuse Reasons')
    interview = fields.Selection([
        ('na', "Applicant Not Available"),
        ('reschedule', "Re-Schedule"),
        ('done', "Done"),
    ], string='Interview Status')
    activity_type_id = fields.Many2one(
        'mail.activity.type', 'Next Activity Type')

    def _get_feedback_skill(self):
        # data = json.loads(request.httprequest.data)
        data_applicant = request.jsonrequest

        if 'applicant_id' in data_applicant['params']['args'][1]:
            applicant_id = data_applicant['params']['args'][1]['applicant_id']['id']

            hr_applicant_obj = self.env['hr.applicant'].search([('id','=',applicant_id)])
            print("hr_applicant_obj == ",hr_applicant_obj)
            
            applicant_skill_id = hr_applicant_obj.applicant_skill_ids
            skill_lines = []
            for skill in applicant_skill_id:
                skill_lines.append([0, 0, {
                    'skill_id': skill.skill_id.id,
                    'skill_level_id': skill.skill_level_id.id,
                    'skill_type_id': skill.skill_type_id.id,
                    'level_progress': skill.level_progress,
                }])  
            return skill_lines
        

    # _sql_constraints = [
    #     ('unique_interviewer_id', 'unique (interviewer_id)', 'This Interviewer already exists')
    # ]


    @api.model
    def create(self,vals):
        activity_model = self.env['mail.activity'].search([('user_id','=',vals.get('interviewer_id')),('res_model','=','int.feedbacks'),('res_id','=',self.id)])
        activity_model.action_done()
        current_id= self.env['hr.applicant'].search([('id','=',vals.get('applicant_id'))])
        result = super(IntFeedbacks,self).create(vals)
        result.write({'job_opening_id':current_id.job_opening_id})
    
        # ====================== AUTO MARK DONE INTERVIEW ACTIVITY =============================== #

        current_id_no = vals.get('applicant_id')
        current_id_interviewers_ids = self.env['hr.applicant'].browse(current_id_no).interviewers_ids
        activity_model_interview = self.env['mail.activity'].search([
                                                           ('res_model', '=', 'hr.applicant'), 
                                                           ('res_id','=',vals.get('applicant_id')),
                                                           ('user_id','in',current_id_interviewers_ids.ids),
                                                           ('activity_type_id','like','Interview'),
                                                           ('date_deadline','>=',datetime.datetime.now())
                                                           ])
        activity_model_interview.action_done()
        
        return result


# class MailActivityInherit(models.Model):
#     _inherit = 'mail.activity'

#     activity_model = self.env['mail.activity']
#     activities = activity_model.search([('state', '=', 'to_do')])
#     activities.write({'state': 'done'})

class IntFeedbacksSkill(models.Model):
    _name = 'int.feedbacks.skill'
    _description = "Skills feedbacks from Interviewers"
    _rec_name = 'skill_id'
    _order = "skill_level_id"

    int_feed_id = fields.Many2one('int.feedbacks', required=True, ondelete='cascade')
    skill_id = fields.Many2one('hr.skill', required=True)
    skill_level_id = fields.Many2one('hr.skill.level', required=True)
    skill_type_id = fields.Many2one('hr.skill.type', required=True)
    level_progress = fields.Integer(related='skill_level_id.level_progress')

    _sql_constraints = [
        ('_unique_skill', 'unique (int_feed_id, skill_id)', "Two levels for the same skill is not allowed"),
    ]

    @api.constrains('skill_id', 'skill_type_id')
    def _check_skill_type(self):
        for record in self:
            if record.skill_id not in record.skill_type_id.skill_ids:
                raise ValidationError(
                    _("The skill %(name)s and skill type %(type)s doesn't match", name=record.skill_id.name,
                      type=record.skill_type_id.name))

    @api.constrains('skill_type_id', 'skill_level_id')
    def _check_skill_level(self):
        for record in self:
            if record.skill_level_id not in record.skill_type_id.skill_level_ids:
                raise ValidationError(_("The skill level %(level)s is not valid for skill type: %(type)s",
                                        level=record.skill_level_id.name, type=record.skill_type_id.name))


class HrSkillTypeInherit(models.Model):
    _inherit = 'hr.skill.type'

    def merge_skills(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'merge.skills',
            'view_type':'form',
            'view_mode':'form',
            'name':_('Merge Skills'),
            'target':'new',
        }
