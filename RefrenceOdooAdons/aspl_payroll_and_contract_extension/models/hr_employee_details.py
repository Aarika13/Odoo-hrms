from odoo import models, fields, api, _
from datetime import date
from dateutil.relativedelta import relativedelta
import logging
import fiscalyear

_logger = logging.getLogger(__name__)

class cummulative_details_employee(models.Model):
    _inherit = 'hr.employee'
    def cummulative_details(self):
        employee_details = self.env['hr.employee'].browse(self.ids)
        fiscalyear.START_MONTH = 4
        currentfiscalstart = fiscalyear.FiscalYear.current().start
        currentfiscalend = fiscalyear.FiscalYear.current().end
        fetch_details = self.env['hr.payslip'].search([('employee_id', '=', employee_details.id),('date_from','>=',currentfiscalstart),('date_to', '<=', currentfiscalend)])
        total_amount = 0
        payslip_components = {}
        for details in fetch_details:
            for line in details.line_ids:
                _logger.info("Payslip Line: %s %s %s",line.id,line.code,line.amount)
                if "Newid" in str(line.id):
                    pass
                else:
                    if line.salary_rule_id.taxable:
                       total_amount += line.amount
                       _logger.info("payslip_components  %s",payslip_components)
            _logger.info("find_payslip_id  %s",details)
        
        fetch_details_projected = self.env['hr.contract'].search([('id', '=', self.contract_id.id)])
        _logger.info("Total from past month payslips: %s", total_amount)
        _logger.info("fetch_details_projected  %s",fetch_details_projected)
        projected_total = 0
        
        payslip_components_projected = {}
        for projected_details in fetch_details_projected:
            for line in projected_details.applicable_salary_rule_ids:
                _logger.info("payslip_components_projected  %s -----%s",line,type(line))
                salary_component = self.env['salary.components'].search([('id', '=', line.id)])
                _logger.info("Rule: %s",salary_component.rule_id)
                if salary_component.rule_id.taxable:
                        projected_total += salary_component.amount
        _logger.info("Projected Total: %s",projected_total)
        current_date = date.today() 
        _logger.info("Dates: %s -- %s",current_date,currentfiscalend)
        enddate = date(currentfiscalend.year,currentfiscalend.month,currentfiscalend.day)
        if enddate > current_date:
            remaining_months = relativedelta(enddate, current_date).months
        else:
            remaining_months = 0

        _logger.info("remaining_months  %s",remaining_months)

        total_amount += projected_total*remaining_months
        _logger.info("total_amount  %s",total_amount)

        return total_amount
