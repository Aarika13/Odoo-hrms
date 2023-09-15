from odoo import models, fields, api, _, _lt


class Task(models.Model):
    _name = "project.task"
    _inherit = "project.task"

    effective_hours = fields.Float("Hours Spent", compute='_compute_effective_hours', compute_sudo=True, store=True, help="Time spent on this task, excluding its sub-tasks.")

    def interchange_time_entry_task(self):

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'timesheet.task.change',
            'view_type':'form',
            'view_mode':'form',
            'name':_('Timesheet Entry Task Change'),
            'target':'new',
            'context': {'task_id':self.id},
        }

   