# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
import pytz
import logging
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class OpeningWizard(models.TransientModel):
    _name = 'recruitment.send.interview.wizard'
    _description = 'Recruitment Send Interview Wizard'

    date_time = fields.Datetime('Starting at')
    description = fields.Text('Description')
    agenda = fields.Text('Agenda')
    telephonic = fields.Boolean("Telephonic")
    interview_type = fields.Selection([
        ('microsoft_team', 'Microsoft Team'),
        ('google meet', 'Google Meet'),
        ('skype', 'Skype'),
        ('aptitude', 'Aptitude Test'),
    ])
    interview_round = fields.Many2one('mail.activity.type', 'Interview',domain=[('suggested_next_type_ids.name','=','Interview Scheduled')])
    user_id = fields.Many2one('res.users', 'Interviewer' , default=lambda self: self.env.user.id)
    user_ids = fields.Many2many('res.users', string='Interviewer')
    work_location_id = fields.Many2one('hr.work.location', 'Work Location', store=True, readonly=False)
    

    @api.onchange('telephonic')
    def onchange_telephonic(self):
        if not self.telephonic:
            self.description = False
            self.interview_type = False

    def action_schedule_interview(self):
        applicant = self.env['hr.applicant'].search([('id', '=', self.env.context.get('active_id'))])
        context = self._context

        current_uid = self.env.context.get('uid') if self.env.context.get('uid') else context.get('uid')

        user = self.env['res.users'].browse(current_uid)
        status = self.env['hr.recruitment.stage'].search([('name', '=', 'Interview')])
        activity_status = self.env['mail.activity.type'].search([('name', '=', 'Interview Scheduled'),('res_model','ilike','hr.applicant')])
        _logger.info('Current User == %s %s',user.name,activity_status.name)
        tz = pytz.timezone(self.user_id.partner_id.tz) or pytz.utc

        self.date_time = self.date_time.replace(tzinfo=tz)
        
        applicant.write({
            'telephonic': self.telephonic,
            'interview_type': self.interview_type,
            'interview_type_message': self.description,
            'meeting_description': self.agenda,
            'interviewers_ids': self.user_ids,
            'interview_date': self.date_time.date(),
            'interview_day': self.date_time.date().strftime("%A"),
            'interview_time': self.date_time.time(),
            'applicant_activity_ids':[(0,0,{
                'activity':activity_status.id,
                'track_date':datetime.now(),
                'user_id':self.user_id.id,
                'job_opening':applicant.job_opening_id.id
            })],
            'stage_id':status,
            'work_location_id':self.work_location_id.id,
        })

        interview_event = self.env['calendar.event']
        vals = {
            'name': applicant.partner_name + " - Interview",
            'res_id':applicant.id,
            'res_model':'hr.applicant',
            'start' : self.date_time,
            'stop': self.date_time,
            'applicant_id':applicant.id,
            'additional_activity':self.interview_round.id,
            'user_id':self.user_id.id,
            'partner_ids': self.user_ids.partner_id,
            }
        calender = interview_event.create(vals)
        context = {
            'interview_round':self.interview_round.name
        }

        template_id = self.env['mail.template'].search([('name', '=', 'Interview Schedule')])
        template_id.with_context(context).send_mail(applicant.id, force_send=True)

        if not self.user_ids:
            raise UserError(_("There are no attendees on these events"))

        email_act = calender.action_open_composer()
        email_ctx = email_act.get('context', {})
        calender.with_context(**email_ctx).message_post_with_template(email_ctx.get('default_template_id'))
