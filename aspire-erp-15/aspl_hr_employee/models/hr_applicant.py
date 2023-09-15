# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class Applicant(models.Model):
    _inherit = 'hr.applicant'

    def create_employee_from_aspire_applicant(self):
        """ Create an hr.employee from the hr.applicants """
        skill_lines = []
        skill_lines_dict = []
        employee = False
        employee_data = {}
        for applicant in self:
            contact_name = False
            if applicant.partner_id:
                address_id = applicant.partner_id.address_get(['contact'])['contact']
                contact_name = applicant.partner_id.display_name
            else:
                if not applicant.partner_name:
                    raise UserError(_('You must define a Contact Name for this applicant.'))
                new_partner_id = self.env['res.partner'].create({
                    'is_company': False,
                    'is_employee': True,
                    'is_candidate': False,
                    'is_applicant': False,
                    'type': 'private',
                    'name': applicant.partner_name,
                    'email': applicant.email_from,
                    'phone': applicant.partner_phone,
                    'mobile': applicant.partner_mobile,
                    'active_employee': True
                })
                applicant.partner_id = new_partner_id
                address_id = new_partner_id.address_get(['contact'])['contact']
            for skill in applicant.applicant_skill_ids:
                skill_lines_dict.append({
                    'skill_id': skill.skill_id.id,
                    'skill_level_id': skill.skill_level_id.id,
                    'skill_type_id': skill.skill_type_id.id,
                    'level_progress': skill.level_progress,
                })
            for skill_data in skill_lines_dict:
                skill_lines.append([0, 0, skill_data])

            if applicant.partner_name or contact_name:
                employee_data = {
                    'default_name': applicant.partner_name or contact_name,
                    'default_job_id': applicant.job_id.id,
                    'default_job_title': applicant.job_id.name,
                    'address_home_id': address_id,
                    'default_department_id': applicant.department_id.id or False,
                    'default_address_id': applicant.company_id and applicant.company_id.partner_id
                                          and applicant.company_id.partner_id.id or False,
                    'default_work_email': applicant.email_from,
                    # applicant.department_id and applicant.department_id.company_id and applicant.department_id.company_id.email or False
                    'default_work_phone': applicant.partner_mobile,  # department_id.company_id.phone
                    'form_view_initial_mode': 'edit',
                    'default_applicant_id': applicant.ids,
                    'default_mobile_phone': applicant.partner_mobile,
                    'default_employee_skill_ids': skill_lines
                }
        dict_act_window = self.env['ir.actions.act_window']._for_xml_id('hr.open_view_employee_list')
        dict_act_window['context'] = employee_data
        return dict_act_window
