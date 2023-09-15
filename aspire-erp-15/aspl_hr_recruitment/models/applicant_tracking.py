# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime
from dateutil.relativedelta import relativedelta


def date_diff_in_seconds(dt2, dt1):
    # difference = dt2 - dt1
    diff = relativedelta(dt2, dt1)
    # return difference.days * 24 * 3600 + difference.seconds
    temp = "{}:{}:{} {}:{}:{}".format(diff.years, diff.months, diff.days, diff.hours, diff.minutes, diff.seconds)
    # res_list = res.split()[0].split(':') + res.split()[-1].split(':')
    # fin_res = ['0'+i if len(i) == 1 else i for i in res_list]
    res = ['0'+i if len(i) == 1 else i for i in temp.split()[0].split(':') + temp.split()[-1].split(':')]
    return "{}:{}:{} {}:{}:{}".format(res[0], res[1], res[2], res[3], res[4], res[5])

# def total_diff(seconds):
#     minutes, seconds = divmod(seconds, 60)
#     hours, minutes = divmod(minutes, 60)
#     days, hours = divmod(hours, 24)
#     months, seconds = divmod(seconds, 2628288)
#     years, seconds = divmod(seconds, 31536000)
#     print("YY MM DD HH MM SS", years, months, days, hours, minutes, seconds)
#     # if not days and not hours:
#     #     return "{} minutes".format(minutes)
#     # if not days:
#     #     return "{} hours {} minutes".format(hours, minutes)
#     return "{}:{}:{}:{}".format(days, hours, minutes, seconds)


class ApplicantActivity(models.Model):
    _name = 'applicant.activity'
    _description = 'Applicant Activity Logs'
    _order = "create_date desc"
    _rec_name = "user_id"

    user_id = fields.Many2one('res.users', string="User")
    old_stage_id = fields.Many2one('hr.recruitment.stage', string="Previous Stage")
    new_stage_id = fields.Many2one('hr.recruitment.stage', string="Current Stage")
    activity = fields.Many2one('mail.activity.type',string="Activity")
    job_opening = fields.Many2one('job.opening',string="Job Opening")
    track_date = fields.Datetime('Date')
    applicant_id = fields.Many2one('hr.applicant', string="Applicant")
    time_taken = fields.Char()  # compute='_compute_time_taken'
    # years = fields.Integer()
    # months = fields.Integer()
    # days = fields.Integer()
    # hours = fields.Integer()
    # minutes = fields.Integer()
    # seconds = fields.Integer()
    # update_id = fields.Integer()
    activity_source_count = fields.Boolean()
    screened_date = fields.Datetime('Screened Date')
    shortlisted_date = fields.Datetime('shortlisted Date')
    interview_date = fields.Datetime('Interview Date')
    joined_date = fields.Datetime('Joined Date')



class MailTrackingValue(models.Model):
    _inherit = 'mail.tracking.value'

    @api.model
    def create_applicant_activity(self):
        for rec in self:
            app_id = rec.mail_message_id.res_id
            uid = self.env.user.id
            activity = self.env['applicant.activity']
            result = {'user_id': uid,
                      'old_stage_id': rec.old_value_integer,
                      'new_stage_id': rec.new_value_integer,
                      'track_date': datetime.now(),
                      'applicant_id': rec.mail_message_id.res_id,
                      }
            applicant_obj = self.env['hr.applicant'].search([('id', '=', app_id)])
            stage_name_obj = self.env['hr.recruitment.stage'].search([('id', '=', result.get('old_stage_id'))])
            if stage_name_obj.name == 'Initial':
                # difference = total_diff(date_diff_in_seconds(result.get('track_date'), applicant_obj.create_date))
                difference = date_diff_in_seconds(result.get('track_date'), applicant_obj.create_date)
                temp_list = difference.split()[0].split(":") + difference.split()[-1].split(":")
                result['years'] = temp_list[0]
                result['months'] = temp_list[1]
                result['days'] = temp_list[2]
                result['hours'] = temp_list[3]
                result['minutes'] = temp_list[4]
                result['seconds'] = temp_list[5]
                result['time_taken'] = difference
            for data in self.env['applicant.activity'].search([('applicant_id', '=', app_id)]):
                if result.get('old_stage_id') == data.new_stage_id.id:
                    # difference = total_diff(date_diff_in_seconds(result.get('track_date'), data.track_date))
                    difference = date_diff_in_seconds(result.get('track_date'), data.track_date)
                    temp_list = difference.split()[0].split(":") + difference.split()[-1].split(":")
                    result['years'] = temp_list[0]
                    result['months'] = temp_list[1]
                    result['days'] = temp_list[2]
                    result['hours'] = temp_list[3]
                    result['minutes'] = temp_list[4]
                    result['seconds'] = temp_list[5]
                    result['time_taken'] = difference
            activity.create(result)


