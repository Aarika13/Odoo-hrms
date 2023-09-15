from odoo import api, fields, models, _


class Project(models.Model):
    # _name = 'project.project'
    _inherit = 'project.project'

    # color = fields.Char(string='Color')
    task_type  = fields.One2many('project.task.selection','project_id','Task Type')


    @api.model
    def create(self,vals):
        result = super(Project,self).create(vals)

        self.env['project.task.selection'].create({
                    'name': 'Task',
                    'color': 'green',
                    'project_id': result.id,
                })

        self.env['project.task.selection'].create({
                    'name': 'Bug',
                    'color': 'red',
                    'project_id': result.id,
                })

        self.env['project.task.selection'].create({
                    'name': 'Support',
                    'color': '#5A5A5A',
                    'project_id': result.id,
                })
       
        return result

    
