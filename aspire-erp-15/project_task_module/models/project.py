
from odoo import api, fields, models

class Project(models.Model):
    _inherit = 'project.project'

    module_ids = fields.One2many('project.module', 'project_id')
    module_count = fields.Integer(compute='_compute_module_count')


    @api.depends('module_ids')
    def _compute_module_count(self):
        read_group = self.env['project.module'].read_group([('project_id', 'in', self.ids)], ['project_id'], ['project_id'])
        mapped_count = {group['project_id'][0]: group['project_id_count'] for group in read_group}
        for project in self:
            project.module_count = mapped_count.get(project.id, 0)