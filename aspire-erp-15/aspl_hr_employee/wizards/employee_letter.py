from odoo import models, api,fields,_
import math
from datetime import timedelta 
from docxtpl import DocxTemplate,InlineImage
from htmldocx import HtmlToDocx
from datetime import datetime, date
import jinja2
import os
import io
import base64
from docxcompose.composer import Composer
from num2words import num2words
from docx import Document

DOCUMENT_TYPE = [
    ('appointment_letter','Appointment letter'),
    ('bond_trainee_letter_head','Bond trainee letter head'),
    ('bond_exp_candidate_letter_head','Bond exp. candidate letter head'),
    ('confirmation_letter','Confirmation letter'),
    ('consultant_contract','Consultant contract'),
    ('nda_experience','NDA - experience'),
    ('offer_letter_experience','Offer letter - experience'),
    ('offer_letter_trainee','Offer letter - trainee')
    ]

class EmployeeLetterWizards(models.TransientModel):
    _name = 'employee.letter.wizard'
    _description = "Employee Letter Wizard"

    emp_letter_type = fields.Selection(DOCUMENT_TYPE,'Letter Name')
    test_emp = fields.Char('Test Data')


    def date_converter(self,date):
        total_days =int(date.strftime("%d"))
        org_date = date.strftime("%d"+ self.suffix(total_days) + " %b %Y")
        return org_date

    def suffix(self,day):
        suffix = ""
        if 4 <= day <= 20 or 24 <= day <= 30:
            suffix = "ᵗʰ"
        else:
            suffix = ["ˢᵗ", "ⁿᵈ", "ʳᵈ"][day % 10 - 1]
        return suffix

    def _get_pan_detail(self,employee_obj):
        for data in employee_obj.employee_identity_id:
            if data.employee_identity == 'account_number':
                return data.pan_no

    def _get_aadhar_detail(self,employee_obj):
        for data in employee_obj.employee_identity_id:
            if data.employee_identity == 'aadhaar':
                return data.aadhaar_no

    def _get_job_designation(self,employee_obj):
        if employee_obj.position_designation:
            job_des_obj = max(employee_obj.position_designation.ids)
            job_record_data = self.env['designation.history'].search([('id', '=', job_des_obj)])
            return job_record_data.job_id.name
            
    def _get_doct_type_and_data(self,document_type,employee_obj):

        birthday_date = datetime.strftime(employee_obj.birthday, '%Y:%m:%d')
        diff_now_birthday = int((datetime.now().date() - datetime.strptime(birthday_date, '%Y:%m:%d').date()).days)
        year = diff_now_birthday // 365
        age_in_year = str(year) + ' years'
        self.date_converter(datetime.today().date())

        if document_type == "appointment_letter":
            html_path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'static/appointment_letter.html'))
            doc_name = 'Appointment Letter'
            doc_store_name = 'appointment_letter'
            salary_date = employee_obj.join_date.strftime("%d/%m")
            dict_data = {
                "name": employee_obj.name,
                "company": employee_obj.company_id.name,
                "address":employee_obj.pre_street +', '+ employee_obj.pre_landmark,
                "date":self.date_converter(datetime.today().date()),
                "city":employee_obj.pre_city +', '+ employee_obj.pre_pcode,
                "designation":self._get_job_designation(employee_obj),
                "date_of_joining":self.date_converter(employee_obj.join_date),
                "date_salary":salary_date
            }

        elif document_type == "bond_trainee_letter_head":
            html_path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'static/bond_trainee_letter_head.html'))
            doc_name = 'Bond Trainee Letter Head'
            doc_store_name = 'bond_trainee_letter_head'
            training_period_words = num2words(employee_obj.training_period)
            training_period =str(employee_obj.training_period) +' ( ' + training_period_words.capitalize() + ' )'
            dict_data = {
                "name": employee_obj.name,
                "training_period":training_period,
                "pan_detail":self._get_pan_detail(employee_obj),
                "aadhar_detail":self._get_aadhar_detail(employee_obj),
                "date":self.date_converter(datetime.today().date()),
                "date_of_training_start":self.date_converter(employee_obj.join_training_date),
                "company": employee_obj.company_id.name,
                "age":age_in_year,
                "address":employee_obj.pre_street +', '+ employee_obj.pre_landmark + ', '+employee_obj.pre_city +', '+ employee_obj.pre_pcode + '.'
            }

        elif document_type == "bond_exp_candidate_letter_head":
            html_path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'static/bond_exp_candidate_letter_head.html'))
            doc_name = 'Bond Exp Candidate Letter'
            doc_store_name = 'bond_exp_candidate_letter_head'
            dict_data = {
                "name": employee_obj.name,
                "pan_detail":self._get_pan_detail(employee_obj),
                "aadhar_detail":self._get_aadhar_detail(employee_obj),
                "date":self.date_converter(datetime.today().date()),
                "date_of_joining":self.date_converter(employee_obj.join_date),
                "company": employee_obj.company_id.name,
                "age":age_in_year,
                "address":employee_obj.pre_street +', '+ employee_obj.pre_landmark + ', '+employee_obj.pre_city +', '+ employee_obj.pre_pcode + '.'
            }

        elif document_type == "confirmation_letter":
            html_path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'static/confirmation_letter.html'))
            doc_name = 'Confirmation Letter'
            doc_store_name = 'confirmation_letter'
            dict_data = {
                "name": employee_obj.name,
                "date":self.date_converter(datetime.today().date()),
                "prob_start_date": self.date_converter(employee_obj.join_date),
                "prob_end_date": self.date_converter(employee_obj.probation_end_date),
                "designation":self._get_job_designation(employee_obj),
                "confirm_date":self.date_converter(employee_obj.confirm_date),
                "company": employee_obj.company_id.name,
            }

        elif document_type == "consultant_contract":
            html_path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'static/consultant_contract.html'))
            doc_name = 'Consultant Contract'
            doc_store_name = 'consultant_contract'
            dict_data = {
                "name": employee_obj.name,
                "company": employee_obj.company_id.name,
            }

        elif document_type == "nda_experience":
            html_path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'static/nda_experience.html'))
            doc_name = 'NDA Experience'
            doc_store_name = 'nda_experience'
            dict_data = {
                "name": employee_obj.name,
                "company": employee_obj.company_id.name,
                "pan_detail":self._get_pan_detail(employee_obj),
                "aadhar_detail":self._get_aadhar_detail(employee_obj),
                "date_of_joining":employee_obj.join_date,
                "date":self.date_converter(datetime.today().date()),
                "age":age_in_year,
                "address":employee_obj.pre_street +', '+ employee_obj.pre_landmark + ', '+employee_obj.pre_city +', '+ employee_obj.pre_pcode + '.'
            }

        elif document_type == "offer_letter_experience": 
            html_path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'static/offer_letter_experience.html'))
            doc_name = 'Offer Letter Experience'
            doc_store_name = 'offer_letter_experience'
            dict_data = {
                "name": employee_obj.name,
                "company": employee_obj.company_id.name,
                "address":employee_obj.pre_street +', '+ employee_obj.pre_landmark,
                "date":self.date_converter(datetime.today().date()),
                "city":employee_obj.pre_city +', '+ employee_obj.pre_pcode,
                "designation":self._get_job_designation(employee_obj),
                "date_of_joining":self.date_converter(employee_obj.join_date),
            }

        elif document_type == "offer_letter_trainee":
            html_path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'static/offer_letter_trainee.html'))
            training_period_words = num2words(employee_obj.training_period)
            training_period =str(employee_obj.training_period) +' ( ' + training_period_words.capitalize() + ' )'
            doc_name = 'Offer Letter Trainee'
            doc_store_name = 'offer_letter_trainee'
            dict_data = {
                "name": employee_obj.name,
                "position":self._get_job_designation(employee_obj),
                "training_period":training_period,
                "address":employee_obj.pre_street +', '+ employee_obj.pre_landmark,
                "date":self.date_converter(datetime.today().date()),
                "city":employee_obj.pre_city +', '+ employee_obj.pre_pcode,
                "comapny":employee_obj.company_id.name
            }   

        return {
            'html_path':html_path,
            'dict_data':dict_data,
            'document_name':doc_name,
            'document_store_name':doc_store_name
        }

    
    def generate_employee_letter(self):
        emp_id = self.env.context.get('employee_id')
        employee_obj = self.env['hr.employee'].browse(emp_id)
        document_type = self.emp_letter_type
        path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'static'))

        emp_letter_data = self._get_doct_type_and_data(document_type,employee_obj)
        html_path = emp_letter_data['html_path']
        dict_letter_data = emp_letter_data['dict_data']
        document_name = emp_letter_data['document_name']
        document_store_name = emp_letter_data['document_store_name']
        html_to_doc = HtmlToDocx()

        if document_store_name != 'nda_experience' and document_store_name != 'bond_exp_candidate_letter_head' and document_store_name != 'bond_trainee_letter_head':
            html_to_doc.table_style ='TableGrid'
        
        # html_to_doc.H1_style = 'Heading 1'
        html_to_doc.parse_html_file(html_path,path + '/demo')
        org_path = path + '/demo.docx'

        doc = DocxTemplate(org_path)
        doc.render(dict_letter_data)
        doc.save(org_path)
        
        master_doc = path + '/master.docx'

        master = Document(master_doc) #master_doc
        composer = Composer(master)
        doc_demo = Document(org_path) #org_path
        composer.append(doc_demo)
        composer.save(org_path)

        file = open(org_path,"rb")
        binary_out = file.read()
        file.close()
        employee_obj.write({'offer_letter_file': base64.b64encode(binary_out)})

        attachment_obj = self.env['ir.attachment']
        attachment_id = attachment_obj.create({'name': document_name,
                                               'store_fname': document_store_name,
                                               'datas': base64.b64encode(binary_out),
                                               'res_id':self.id,
                                               'res_model':'hr.employee'
                                               })
        download_url = '/web/content/' + \
                       str(attachment_id.id) + '?download=True'
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        return {
            "type": "ir.actions.act_url",
            "url": str(base_url) + str(download_url),
            "target": "new"
        }      
