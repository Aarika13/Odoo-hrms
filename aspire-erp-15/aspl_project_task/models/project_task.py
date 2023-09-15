from odoo import api, fields, models, _

class Project_Task(models.Model):
    _name = 'project.task.selection'
    _description = 'Project_Task_Selection'


    name = fields.Char(string="Task Type")
    parent_id = fields.Many2one('project.task', string='Parent Task', index=True)
    display_project_id = fields.Many2one('project.project', index=True)
    project_id = fields.Many2one('project.project', string='Project',

        compute='_compute_project_id', recursive=True, store=True, readonly=False,

        index=True, tracking=True, change_default=True)

    color = fields.Char(string='Color')

    @api.depends('parent_id.project_id', 'display_project_id')
    def _compute_project_id(self):
        for task in self:
            if task.parent_id:
                task.project_id = task.display_project_id or task.parent_id.project_id

    

