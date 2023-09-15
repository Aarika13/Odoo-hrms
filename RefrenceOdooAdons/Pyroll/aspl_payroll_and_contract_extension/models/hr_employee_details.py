from odoo import models, fields, api, _
from datetime import date
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)

class cummulative_details_employee(models.Model):
    _inherit = 'hr.employee'
    def cummulative_details(self,payslip):
        _logger.info("PAYSLIP  %s",payslip)
        employee_details = self.env['hr.employee'].browse(self.ids)

        fetch_details = self.env['hr.payslip'].search([('employee_id', '=', employee_details.id)])
        payslip_components = {}
        for details in fetch_details:
            for line in details.line_ids:
                if line.salary_rule_id.taxable:
                    if line.code in payslip_components :
                        payslip_components[line.code] = payslip_components[line.code] + line.amount
                    else :
                        payslip_components[line.code] = line.amount
                _logger.info("payslip_components  %s",payslip_components)
            _logger.info("find_payslip_id  %s",details)

        fetch_details_projected = self.env['hr.contract'].search([('id', '=', self.contract_id)])
        _logger.info("fetch_details_projected  %s",fetch_details_projected)

        payslip_components_projected = {}
        for projected_details in fetch_details_projected:
            for line in projected_details.applicable_salary_rule_ids:
                if line.salary_rule_id.taxable:
                    if line.code in payslip_components_projected :
                        payslip_components_projected[line.code] = payslip_components_projected[line.code] + line.amount
                    else :
                        payslip_components_projected[line.code] = line.amount
                _logger.info("payslip_components_projected  %s",payslip_components_projected)


        today = fetch_details.date_from
        contract_end_date = fetch_details_projected.date_end 
        if contract_end_date > today:
            remaining_months = relativedelta(contract_end_date, today).months
        else:
            remaining_months = 0

        _logger.info("remaining_months  %s",remaining_months)

        def myMapFunc(n):
            return n*remaining_months
        remaining_amount = map(myMapFunc, payslip_components_projected)
        _logger.info("remaining_amount  %s",remaining_amount)

        total_amount = {}
        for line.code, line.amount in payslip_components.items():
            if line.code in payslip_components_projected:
                total_amount[line.code] = line.amount + payslip_components_projected[line.code]
            else:
                total_amount[line.code] = line.amount
        return total_amount