from odoo import api, fields, models
from odoo.exceptions import ValidationError


class HrTestWizard(models.TransientModel):
    _name = "hr.test.wizard"
    _description = "Hr Test Wizard"

    approval_id = fields.Many2one('res.users',string="Approve")


    def action_set_leave_manager_id(self):
        # print(".................",self.approval_id)
        # print("++++++++++++++++++++++++", self.approval_id.id)

        coach_id = self.env[self._context['active_model']].browse(self._context['active_id'])
        print(coach_id)
        coach_id.write({'leave_manager_id': self.approval_id.id})
        # if self.approval_id in self.env['res.users']:
        #     coach_id = self.env[self._context['active_model']].browse(self._context['active_id'])
        #     print(coach_id)
        #     coach_id.write({'leave_manager_id': self.approval_id.id})
        # else:
        #     raise ValidationError("Select from the given.It is not applicable.")



