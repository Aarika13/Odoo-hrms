# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ApplicantFeedbackQue(models.Model):
    _name = 'applicant.feedback.que'
    _description = 'Applicant Feedback Questions'

    name = fields.Char('Question')
    active = fields.Boolean('Active', default=True)
