from odoo import models, fields, api

class ProjectTask(models.Model):
    _inherit = 'project.task'

    type_of_task = fields.Many2many('projectt.tags', string = "Tags Name")
    print("***************",type_of_task)