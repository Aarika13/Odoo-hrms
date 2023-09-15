from odoo import models, fields, api, _


class HrEmployeeButton(models.Model):
    _inherit = 'hr.employee'

    def action_hr_test_wizard(self):
        # print("Wizard Button")
        # print("-----------------------------------------")
        return self.env['ir.actions.act_window']._for_xml_id('aspl_hr_employee.action_hr_test_wizard')
