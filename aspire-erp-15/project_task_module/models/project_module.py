from odoo import api, fields, models

class ProjectModule(models.Model):
    _name = 'project.module'
    _description = "Project Module"
    _order = 'name'

    def _get_default_project_id(self):
        return self.env.context.get('default_project_id') or self.env.context.get('active_id')

    name = fields.Char(required=True)
    project_id = fields.Many2one('project.project', required=True, default=_get_default_project_id)
    description = fields.Char('Description')

    module_task_ids = fields.One2many(
        "project.task", "module_id", string="Project Tasks"
    )

   


    
    

