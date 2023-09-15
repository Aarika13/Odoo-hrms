from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class salary_components(models.Model):
    _name = 'salary.components'

    amount = fields.Integer(string="Fixed Amount")
    rule_id = fields.Many2one('hr.salary.rule', string="Applicable Salary Rule")

class new_contract_config(models.Model):
    _inherit = 'hr.contract'

    gratuity = fields.Boolean(string="Gratuity")
    pf = fields.Boolean(string="Provident Fund")
    pf_ceiling = fields.Boolean(string="PF Ceiling")
    esic = fields.Boolean(string="Esic")
    applicable_salary_rule_ids = fields.Many2many('salary.components', string="Applicable Salary Rule")

    # @api.model
    # def create(self,vals):   
    #     contract = super(new_contract_config, self).create(vals)
    #     # self._update_record(contract)
    #     return contract

    # @api.model
    # def write(self,vals):
    #     contract = super(new_contract_config, self).create(vals)
    #     self.load_salary_components_record()
    #     return contract

    def load_salary_components(self):
        _logger.info("Update record called...")

        payslip =self.env['hr.payslip']
        slip_id = payslip.create({
                    'employee_id':self.employee_id.id,
                    'struct_id':self.struct_id.id,
                    'contract_id':self.id,
                    'worked_days_line_ids': [(0, 0,
                                {'name':'worked days',
                                'code':'WORK100',
                                'number_of_days':20,
                                'number_of_hours':160,
                                'contract_id' : self.id
                                })]
                    })
        print("slip_id",slip_id)
        slip_id.write({
                    'worked_days_line_ids': [(0, 0,
                                {'name':'worked days',
                                'code':'LOP',
                                'number_of_days':0,
                                'number_of_hours':0,
                                'contract_id' : self.id
                                })]
                    })
        _logger.info("Payslip id is: %s",slip_id)
        self.applicable_salary_rule_ids.unlink()
        salary_components = slip_id.get_projected_taxable_income_all()
        slip_id.unlink()
        _logger.info("Calculated components are: %s", salary_components)

        updated_details_dict = []
        for rule in self.struct_id.rule_ids:
            _logger.info("Rule: %s",rule)
            if rule.code in salary_components and rule.appear_on_contract == True:
                updated_details_dict.append([0,0,{
                            'amount':salary_components.get(rule.code),
                            'rule_id': rule.id
                        }])
        self.write({'applicable_salary_rule_ids':updated_details_dict})
