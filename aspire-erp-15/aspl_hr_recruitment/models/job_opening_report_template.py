# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class JobOpeningReportTemplate(models.Model):
    _name = "job.opening.report.template"
    _description = "Job Opening Report Template"

    name = fields.Char('Name')
    recruiter_id = fields.Many2one('res.users', string="Recruiter")
    job_opening_ids = fields.Many2many('job.opening', string="Job Openings")
    period = fields.Selection([
        ('cm', 'Current Month'),
        ('lm', 'Last Month'),
        ('cq', 'Current Quarter'),
        ('cy', 'Current Year'),
    ], string='Period', default='cm')
    company_id = fields.Many2one('res.company', string="Company")
    state = fields.Selection([
        ('recruit', 'In Progress'),
        ('open', 'Done')
    ], string='Status', default='recruit',
        help="Set whether the recruitment process is open or closed for this job position.")
