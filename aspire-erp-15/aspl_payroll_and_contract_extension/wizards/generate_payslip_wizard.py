from odoo import api, fields, models, _
from datetime import date
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class PayslipWizards(models.TransientModel):
    _name = 'payslip.generate.wizard'
    _description = "Generate Payslip Wizard"

    employee_ids = fields.Many2many('employee.full.final', string='Employee Ids')
    is_hold_salary = fields.Boolean(string='Is Hold Salary')
    payslip_run_id = fields.Many2one('hr.payslip.run')

    select_all = fields.Boolean("Select All")
    lock_previous_payroll = fields.Boolean("Lock Previous Payroll")
    employee_addition = fields.Boolean("Employee Additions")
    employee_separtion = fields.Boolean("Employee Separations")
    employee_confirmation = fields.Boolean("Employee Confirmations")
    employee_data_update = fields.Boolean("Employee Data Updates")
    update_payment_details = fields.Boolean("Update Payment Details")
    salary_revisions = fields.Boolean("Salary Revisions")
    update_one_time_payment = fields.Boolean("Update One Time Payment")
    update_one_time_deductions = fields.Boolean("Update One Time Deductions")
    update_any_other_salary_changes = fields.Boolean("Update Any Other Salary Changes")
    loans_update = fields.Boolean("Loans Update")
    stop_payment = fields.Boolean("Stop Payment")
    update_lop_lwp = fields.Boolean("Update LOP/LWP")
    update_arrears = fields.Boolean("Update Arrears")
    full_final_settlements = fields.Boolean("Full & Final Settlements")
    reimbursement_claims = fields.Boolean("Reimbursement Claims")
    lock_it_declaration = fields.Boolean("Lock IT Declaration")
    download_it_declaration = fields.Boolean("Download IT Declaration")

    @api.onchange('select_all')
    def select_all_checkbox(self):
        if self.select_all:
            self.lock_previous_payroll = True
            self.employee_addition = True
            self.employee_separtion = True
            self.employee_confirmation = True
            self.employee_data_update = True
            self.update_payment_details = True
            self.salary_revisions = True
            self.update_one_time_payment = True
            self.update_one_time_deductions = True
            self.update_any_other_salary_changes = True
            self.loans_update = True
            self.stop_payment = True
            self.update_lop_lwp = True
            self.update_arrears = True
            self.full_final_settlements = True
            self.reimbursement_claims = True
            self.lock_it_declaration = True
            self.download_it_declaration = True
        else:
            self.lock_previous_payroll = False
            self.employee_addition = False
            self.employee_separtion = False
            self.employee_confirmation = False
            self.employee_data_update = False
            self.update_payment_details = False
            self.salary_revisions = False
            self.update_one_time_payment = False
            self.update_one_time_deductions = False
            self.update_any_other_salary_changes = False
            self.loans_update = False
            self.stop_payment = False
            self.update_lop_lwp = False
            self.update_arrears = False
            self.full_final_settlements = False
            self.reimbursement_claims = False
            self.lock_it_declaration = False
            self.download_it_declaration = False

    def check_condition_step(self):
        check_list = ['lock_previous_payroll', 'employee_addition',
                        'employee_separtion', 'employee_confirmation',
                        'employee_data_update', 'update_payment_details',
                        'salary_revisions', 'update_one_time_payment',
                        'update_one_time_deductions', 'update_any_other_salary_changes',
                        'loans_update', 'stop_payment', 'update_lop_lwp', 'update_arrears',
                        'full_final_settlements', 'reimbursement_claims',
                        'lock_it_declaration', 'download_it_declaration']
        check_dict = self.env['payslip.generate.wizard'].search_read([('id', '=', self.id)])
        count = 0
        bool_list = []
        for i in check_dict[0]:
            if i in check_list:
                count = count+1
                if check_dict[0][i]:
                    bool_list.append(True)
                else:
                    bool_list.append(False)
        if False in bool_list:
            raise ValidationError("Please Tick Check Box")
        else:
            result_id = self.env['check.attendance.shortfall'].create({})
            return {
                'name': _('Check Attendance'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'check.attendance.shortfall',
                'res_id': result_id.id,
                'target': 'new'
            }



    def auto_genarate_payslip(self):

        employee = self.env['hr.contract'].search(
            [('date_end', '>=', self.payslip_run_id.date_start), ('date_start', '<=', self.payslip_run_id.date_start)]).employee_id
        current_company_employee = employee.filtered(
            lambda emp: emp.company_id.id in self.env.context.get('allowed_company_ids'))

        if current_company_employee:
            current_date = date.today()
            employee_list = []
            it_declaration_year = str(current_date.strftime('%Y')) + '-' + str(
                (current_date + relativedelta(years=1)).strftime('%y')) if current_date > date(current_date.year, 3,
                                                                                               31) else str(
                (current_date - relativedelta(years=1)).strftime('%Y')) + '-' + str(current_date.strftime('%y'))
            financial_year = self.env['financial.year'].search([('name', '=', it_declaration_year)])
            if financial_year:
                for employee_id in current_company_employee:
                    it_declaration_year_record = self.env['it.declaration.payslip'].search(
                        [('employee_id', '=', employee_id.id), ('financial_year', '=', financial_year.id)], limit=1,
                        order='create_date desc')
                    if it_declaration_year_record and it_declaration_year_record.status == 'unlocked':
                        employee_list.append(employee_id.name)
            else:
                raise ValidationError(
                    "It declaration are not created for current Year. Please create for all employee.")

            if len(employee_list) > 1:
                raise ValidationError(
                    "IT Declaration for following employees are not locked. Please lock before you generate payslips.\n" + "\n".join(
                        "- " + employee for employee in employee_list))
            elif len(employee_list) == 1:
                raise ValidationError(
                    "IT Declaration for following employee is not locked. Please lock before you generate payslip.\n- " + str(
                        employee_list[0]))

            payslips = self.env['hr.payslip']

            for employee in current_company_employee:
                slip_data = self.env['hr.payslip'].onchange_employee_id(self.payslip_run_id.date_start, self.payslip_run_id.date_end, employee.id,
                                                                        contract_id=False)
                blocked = False
                if employee in self.employee_ids.employee_id:
                    blocked = True
                res = {
                    'employee_id': employee.id,
                    'name': slip_data['value'].get('name'),
                    'struct_id': slip_data['value'].get('struct_id'),
                    'contract_id': slip_data['value'].get('contract_id'),
                    'payslip_run_id': self.payslip_run_id.id,
                    'input_line_ids': [(0, 0, x) for x in slip_data['value'].get('input_line_ids')],
                    'worked_days_line_ids': [(0, 0, x) for x in slip_data['value'].get('worked_days_line_ids')],
                    'date_from': self.payslip_run_id.date_start,
                    'date_to': self.payslip_run_id.date_end,
                    'credit_note': self.payslip_run_id.credit_note,
                    'company_id': employee.company_id.id,
                    'is_blocked': blocked,
                }
                payslips += self.env['hr.payslip'].create(res)
            payslips.compute_sheet()
