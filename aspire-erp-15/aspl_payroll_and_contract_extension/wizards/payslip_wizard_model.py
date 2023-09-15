from odoo import fields, models
from datetime import date
from openpyxl import Workbook
import logging
import base64

_logger = logging.getLogger(__name__)

class PayslipWizards(models.TransientModel):
    _name = 'payslip.file.wizard'
    _description = "Generate Payslip Excel File"

    bank_selection = fields.Many2one('res.partner.bank' , string='Select Bank' ,required=True)
    payment_date = fields.Date(string='Payment Date' ,required=True,default= date.today())


    def _get_template(self):
        self.banksheet_template = base64.b64encode(open("/opt/odoo/.local/bank_sheet.xlsx", "rb").read())

    banksheet_template = fields.Binary('Template', compute="_get_template",default = date.today())



    def get_contract_template(self):
        payslip_batch_details = self.env['hr.payslip.run'].search([])
        _logger.info("payslip_batch_details: %s", payslip_batch_details)
        return {
            'type': 'ir.actions.act_url',
            'name': 'contract',
            'url': '/web/content/payslip.file.wizard/%s/banksheet_template/bank_sheet.xlsx?download=true' %(self.id),
        }
    
    #@http.route('/aspl_payroll_and_contract_extension/generate_excel', type='http', auth='user')
    def generate_excel(self, **post):
        wb = Workbook()
        ws = wb.active
        ws.append(["PYMT_PROD_TYPE_CODE","PYMT_MODE","DEBIT_ACC_NO","BNF_NAME","BENE_ACC_NO","BENE_IFSC","AMOUNT","DEBIT_NARR","CREDIT_NARR","MOBILE_NUM","EMAIL_ID","REMARK","PYMT_DATE","REF_NO","ADDL_INFO1","ADDL_INFO2","ADDL_INFO3","ADDL_INFO4","ADDL_INFO5","LEI_NUMBER"])
        name = "/opt/odoo/.local/bank_sheet.xlsx"
        wb.save(name)
        batch_id = self.env.context['batch_id']
        payslip_batch_details = self.env['hr.payslip.run'].search([('id', '=', batch_id)])
        net_amount = 0
        _logger.info("payslip_batch_details: %s", payslip_batch_details)
        for data in payslip_batch_details.slip_ids:
            if data.is_blocked:
                continue
            for info in data.line_ids:
                _logger.info("payslip_info_code: %s", info.code)
                if info.code =='NET':
                    _logger.info("payslip_salary_code: %s", info.amount)
                    net_amount = info.amount
                if info.code == 'NCC':
                    net_amount = info.amount

            list=['PAB_VENDOR','NEFT',self.bank_selection.bank_id.name,data.employee_id.name,data.employee_id.bank_account_no,data.employee_id.bank_id.bic,net_amount,'','','','','',self.payment_date]

            _logger.info("payslip_batch_list: %s",list)
            ws.append(list)
            wb.save(name)

        return self.get_contract_template()
