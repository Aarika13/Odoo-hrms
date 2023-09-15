# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class BlockedEmails(models.Model):
    _name = "blocked.emails"
    _description = "Blocked Emails list for Candidate"

    name = fields.Char("Email", required=True)


