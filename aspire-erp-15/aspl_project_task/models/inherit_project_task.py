from odoo import api, fields, models, _


class Project_Task(models.Model):
    _inherit = 'project.task'

    type_of_task = fields.Many2one('project.task.selection')
    type_of_task_color = fields.Char(string="Type of Task color", related="type_of_task.color", tracking=True)
    task_priority = fields.Selection([('lowest', 'Lowest'), ('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('highest', 'Highest')], string='Priority', tracking=True)
    story_points = fields.Selection([('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('5', '5'), ('8', '8'), ('13', '13'), ('21', '21')], string='Story Points', tracking=True)


class ProjectMilestone(models.Model):
    _inherit = "project.milestone"

    active = fields.Boolean('Active', default=True)
