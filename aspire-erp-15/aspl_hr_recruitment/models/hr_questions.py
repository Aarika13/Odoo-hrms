# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class HrQuestions(models.Model):
    _name = 'hr.questions'
    _description = 'HR Questions'

    name = fields.Char('Question')
    active = fields.Boolean('Active', default=True)
