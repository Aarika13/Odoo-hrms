# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class MultipleCandidatesEmails(models.Model):
    _name = "multiple.candidates.emails"
    _description = "Multiple Emails for one Candidate"

    name = fields.Char('Email Id')
