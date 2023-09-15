# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    module_id = fields.Many2one(
        "project.module",
        string="Module",
        group_expand="_read_group_module_ids",
        domain="[('project_id', '=', project_id)]",
    )

    @api.model
    def _read_group_module_ids(self, module_ids, domain, order):
        if "default_project_id" in self.env.context:
            module_ids = self.env["project.module"].search(
                [("project_id", "=", self.env.context["default_project_id"])]
            )
        return module_ids
