from datetime import date
import calendar
from odoo import models, fields, api, _
from odoo.http import request


class HrContract(models.Model):
    _inherit = 'hr.contract'

    @api.model
    def salary_range(self):
        data = []

        cookies = request.httprequest.cookies.get('cids').split(',')
        active_companies = []
        for i in cookies:
            active_companies.append(self.env['res.company'].browse(int(i)).name)

        domain = [('state', '=', 'open'), ('company_id.name', 'in', active_companies)]

        salary_ranges = [
            {'label': 'Below 25k', 'domain': [('wage', '<', 25000)]},
            {'label': '25k to 50k', 'domain': [('wage', '>=', 25000), ('wage', '<', 50000)]},
            {'label': '50k to 75k', 'domain': [('wage', '>=', 50000), ('wage', '<', 75000)]},
            {'label': '75k to 1 lakh', 'domain': [('wage', '>=', 75000), ('wage', '<', 100000)]},
            {'label': 'above 1 lakh', 'domain': [('wage', '>=', 100000)]}
        ]

        search_id = self.env.ref('hr_contract.hr_contract_history_view_search').sudo().id
        for salary_range in salary_ranges:
            count = self.env['hr.contract'].search_count(domain + salary_range['domain'])
            data.append({'label': salary_range['label'], 'value': count, 'search_id': search_id})

        return data


class AccountInvoice(models.Model):
    _inherit = "account.move"

    @api.model
    def invoices(self):
        vendor = []
        amount = []

        cookies = request.httprequest.cookies.get('cids').split(',')
        active_companies = []
        for i in cookies:
            active_companies.append(self.env['res.company'].browse(int(i)).name)

        for rec in self.env['account.move'].search(
                [('move_type', '=', 'out_invoice'), ('amount_residual_signed', '!=', '0'),
                 ('payment_state', '!=', 'paid'), ('company_id.name', 'in', active_companies)]):
            vendor.append(rec.partner_id.name)
            amount.append(abs(int(rec.amount_residual_signed)))

        name_sum_dict = {}

        for name, amount in zip(vendor, amount):
            if name not in name_sum_dict:
                name_sum_dict[name] = {'value': amount, 'text': 1}
            else:
                name_sum_dict[name]['value'] += amount
                name_sum_dict[name]['text'] += 1

        search_id = self.env.ref('account.view_account_invoice_filter').sudo().id
        data = [{'label': name, 'value': info['value'], 'txt': info['text'], 'search_id': search_id} for name, info in
                name_sum_dict.items()]

        return data

    @api.model
    def bills(self):
        vendor = []
        amount = []

        cookies = request.httprequest.cookies.get('cids').split(',')
        active_companies = []
        for i in cookies:
            active_companies.append(self.env['res.company'].browse(int(i)).name)

        for rec in self.env['account.move'].search(
                [('move_type', '=', 'in_invoice'), ('amount_residual_signed', '!=', '0'),
                 ('payment_state', '!=', 'paid'), ('company_id.name', 'in', active_companies)]):
            vendor.append(rec.partner_id.name)
            amount.append(abs(int(rec.amount_residual_signed)))

        name_sum_dict = {}

        for name, amount in zip(vendor, amount):
            if name not in name_sum_dict:
                name_sum_dict[name] = {'value': amount, 'text': 1}
            else:
                name_sum_dict[name]['value'] += amount
                name_sum_dict[name]['text'] += 1

        search_id = self.env.ref('account.view_account_invoice_filter').sudo().id
        data = [{'label': name, 'value': info['value'], 'txt': info['text'], 'search_id': search_id} for name, info in
                name_sum_dict.items()]

        return data


class Employee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def check_user_group_manager(self):
        uid = request.session.uid
        user = self.env['res.users'].sudo().search([('id', '=', uid)], limit=1)
        if user.has_group('account.group_account_manager'):
            return True
        else:
            return False

    @api.model
    def experience_salary_graph(self):
        data = []

        cookies = request.httprequest.cookies.get('cids').split(',')
        active_companies = []
        for i in cookies:
            active_companies.append(self.env['res.company'].browse(int(i)).name)

        exp_less_2 = []
        exp_2_4 = []
        exp_4_6 = []
        exp_6_8 = []
        exp_more_8 = []

        for rec in self.env['hr.employee'].search([('company_id.name', 'in', active_companies)]):
            wage = rec.contract_id.wage
            experience = rec.actual_experience

            if experience == '0' or experience is None or 'Years' not in experience:
                exp_less_2.append(wage)

            elif 'Years' in experience:
                exp_parts = experience.split()
                if int(exp_parts[0]) < 4:
                    exp_2_4.append(wage)
                elif int(exp_parts[0]) < 6:
                    exp_4_6.append(wage)
                elif int(exp_parts[0]) < 8:
                    exp_6_8.append(wage)
                elif int(exp_parts[0]) >= 8:
                    exp_more_8.append(wage)

        search_id = self.env.ref('hr.view_employee_filter').sudo().id

        data.append({'label': 'Below 2 years', 'value': len(exp_less_2), 'search_id': search_id})
        data.append({'label': '2-4 years', 'value': len(exp_2_4), 'search_id': search_id})
        data.append({'label': '4-6 years', 'value': len(exp_4_6), 'search_id': search_id})
        data.append({'label': '6-8 years', 'value': len(exp_6_8), 'search_id': search_id})
        data.append({'label': 'Above 8 years', 'value': len(exp_more_8), 'search_id': search_id})

        return data

    @api.model
    def earning_expense_graph(self):
        year = date.today().year - 1
        # year = date.today().year

        cookies = request.httprequest.cookies.get('cids').split(',')
        active_companies = []
        for i in cookies:
            active_companies.append(self.env['res.company'].browse(int(i)).name)

        earning_data = {i: 0 for i in range(1, 13)}
        expense_data = {i: 0 for i in range(1, 13)}

        for rec in self.env['account.move'].search([('move_type', '=', 'out_invoice'), ('company_id.name', 'in', active_companies)]):
            if rec.invoice_date.year == year:
                earning_data[rec.invoice_date.month] += rec.amount_total_signed

        for rec in self.env['hr.contract'].search([]):
            if rec.date_start.year == year:
                for month in range(rec.date_start.month, 13):
                    expense_data[month] += rec.wage
            elif rec.date_start.year == (year - 1):
                for month in range(1, rec.date_start.month + 1):
                    expense_data[month + 1] += rec.wage

        month_names = [calendar.month_abbr[i] for i in range(1, 13)]

        earning_data = [{'label': month_names[month - 1], 'value': value} for month, value in earning_data.items()]
        expense_data = [{'label': month_names[month - 1], 'value': value} for month, value in expense_data.items()]

        data = [{'label': 'Earning', 'value': earning_data}, {'label': 'Expense', 'value': expense_data}]

        return data
