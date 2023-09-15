# -*- coding: utf-8 -*-

from odoo import fields, models


class ResumeLine(models.Model):
    _inherit = 'hr.resume.line'

    percentage = fields.Float('Percentage')
    relevant = fields.Boolean("Relevant")
    leaving_reason = fields.Char("Reason For Leaving")
