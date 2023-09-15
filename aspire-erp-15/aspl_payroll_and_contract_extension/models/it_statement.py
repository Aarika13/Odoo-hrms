from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta
import calendar
from odoo import models, fields, api, _
from odoo.http import request
import fiscalyear
import logging

_logger = logging.getLogger(__name__)
class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
        
    @api.model
    def get_user_employee_details_payslip(self):
        uid = request.session.uid
        employee = self.env['hr.employee'].sudo().search([('user_id', '=', uid)], limit=1)

        # ********************* YTD SUMMARY IT STATEMENT TABLE ********************* #
        ytd_summary_it_statement_data = {}
        fiscalyear.START_MONTH = 4
        currentfiscalstart = fiscalyear.FiscalYear(datetime.now().year).start.date() if datetime.now().month < 4 else fiscalyear.FiscalYear(datetime.now().year+1).start.date()
        currentfiscalend = fiscalyear.FiscalYear(datetime.now().year).end.date()  if datetime.now().month < 4 else fiscalyear.FiscalYear(datetime.now().year+1).end.date()
        fetch_details = self.env['hr.payslip'].search([('employee_id', '=', employee.id),('date_from','>=',currentfiscalstart),('date_to', '<=', currentfiscalend)])
        for details in fetch_details:
            for line in details.line_ids:
                if "Newid" in str(line.id):
                    pass
                else:
                    if line.salary_rule_id.taxable or line.salary_rule_id.is_deduction:
                        a = 'Income' if line.salary_rule_id.taxable else 'Deduction'
                        if ytd_summary_it_statement_data.get(a):
                            if ytd_summary_it_statement_data.get(a).get(line.salary_rule_id.name):
                                if ytd_summary_it_statement_data.get(a).get(line.salary_rule_id.name).get(details.date_from.month):
                                    pass
                                else:
                                    ytd_summary_it_statement_data.get(a).get(line.salary_rule_id.name)[details.date_from.month] = line.amount
                            else:
                                ytd_summary_it_statement_data.get(a)[line.salary_rule_id.name] = {details.date_from.month : line.amount}
                        else:
                            ytd_summary_it_statement_data[a] = {line.salary_rule_id.name : {details.date_from.month : line.amount}}

        last_day = calendar.monthrange(date.today().year, date.today().month)[1]
        last_full_date = date(date.today().year, date.today().month, last_day)
        current_date = last_full_date 
        enddate = date(currentfiscalend.year,currentfiscalend.month,currentfiscalend.day)
        if enddate > current_date:
            remaining_months = relativedelta(enddate, current_date).months
        else:
            remaining_months = 0
        _logger.info("Remaining Months: %s", remaining_months)

        fetch_details_projected = self.env['hr.contract'].search([('employee_id', '=', employee.id),('state','=','open')])
        counter_month = datetime.now().month
        counter_year = datetime.now().year
        if( datetime.strptime(f'{counter_year}-{counter_month}', "%Y-%m") > datetime.strptime(f'{fetch_details_projected.date_end.year}-{fetch_details_projected.date_end.month}', "%Y-%m")):
            if self.env['hr.contract'].search([('employee_id', '=', employee.id),('state','=','draft')]):
                fetch_details_projected = self.env['hr.contract'].search([('employee_id', '=', employee.id),('state','=','draft')])
        for i in range(0,remaining_months+1):
            for projected_details in fetch_details_projected:
                for line in projected_details.applicable_salary_rule_ids:
                    if line.rule_id.taxable or line.rule_id.is_deduction:
                        a = 'Income' if line.rule_id.taxable else 'Deduction'
                        if ytd_summary_it_statement_data.get(a):
                            if ytd_summary_it_statement_data.get(a).get(line.rule_id.name):
                                if ytd_summary_it_statement_data.get(a).get(line.rule_id.name).get(counter_month):
                                    pass
                                else:
                                    ytd_summary_it_statement_data.get(a).get(line.rule_id.name)[counter_month] = line.amount
                            else:
                                ytd_summary_it_statement_data.get(a)[line.rule_id.name] = {counter_month : line.amount}
                        else:
                            ytd_summary_it_statement_data[a] = {line.rule_id.name : {counter_month : line.amount}}
            if(datetime.now().month == 12 or counter_month == 12):
                counter_month = 1
                counter_year += 1
            else:
                counter_month += 1

        month_counter = [4,5,6,7,8,9,10,11,12,1,2,3]
        for i in ytd_summary_it_statement_data:
            for j,k in ytd_summary_it_statement_data[i].items():
                for mc in month_counter:
                    if mc not in k: 
                        k[mc] = 0
                sorted_items = []
                for key in range(4, 13):
                    if key in k:
                        sorted_items.append((key, k[key]))
                for key in range(1, 4):
                    if key in k:
                        sorted_items.append((key, k[key]))
                sorted_dict = dict(sorted_items)
                ytd_summary_it_statement_data[i][j] = sorted_dict

        total_of_months = 0
        for i in ytd_summary_it_statement_data:
            for j in ytd_summary_it_statement_data[i]:
                items = list(ytd_summary_it_statement_data[i][j].items())
                for key,value in ytd_summary_it_statement_data[i][j].items():
                    total_of_months += value
                items.insert(0, ('Total', total_of_months))
                total_of_months = 0
                ytd_summary_it_statement_data[i][j] = dict(items)

        # temp_dict2 = {}
        # counter2 = True
        for i in ytd_summary_it_statement_data:
            temp_dict = {}
            for j in ytd_summary_it_statement_data[i]:
                for key, value in ytd_summary_it_statement_data[i][j].items():
                    if temp_dict.get('Total'):
                        if temp_dict.get('Total').get(key):
                            temp_dict['Total'][key] += value
                        else:
                            temp_dict.get('Total')[key] = value
                    else:
                        temp_dict['Total'] = {key:value}
            ytd_summary_it_statement_data.get(i).update(temp_dict)
        #     if counter2==True:
        #         for p in temp_dict:
        #             for q,r in temp_dict[p].items():
        #                 if temp_dict2.get(p):
        #                     if temp_dict2.get(p).get(q):
        #                         pass
        #                     else:
        #                         temp_dict2[p][q] = r
        #                 else:
        #                     temp_dict2[p] = {q:r}
        #     else :
        #         for k in temp_dict:
        #             for key,value in temp_dict[k].items():
        #                 temp_dict2[k][key] -= value
        #     counter2=False
        # ytd_summary_it_statement_data['Grand Total'] = temp_dict2
        # counter2=True
        _logger.info("Yearly It Statement: %s", ytd_summary_it_statement_data)

        taxable_amount = ytd_summary_it_statement_data['Income']['Total']['Total']
        it_declaration_info = employee.get_it_statement_info(current_date)
        ytd_summary_it_deduction_components = it_declaration_info[0]
        del ytd_summary_it_deduction_components['regime']

        ytd_summary_it_deduction_component_last_employer = {}
        ytd_summary_it_deduction_component_last_employer['Total Income After Exemptions'] = it_declaration_info[1].income_after_exemptions
        ytd_summary_it_deduction_component_last_employer['Professional Tax'] = it_declaration_info[1].professional_tax
        ytd_summary_it_deduction_component_last_employer['Provident Fund'] = it_declaration_info[1].provident_fund
        ytd_summary_it_deduction_component_last_employer['Total Tax'] = it_declaration_info[1].total_tax_previous_employer

        totalbasic = ytd_summary_it_statement_data['Income']['Basic Salary']['Total']
        totalhra = ytd_summary_it_statement_data['Income']['House Rent Allowance']['Total']
        rent_paid =  ytd_summary_it_deduction_components['house_rent']
        hra_exempted_amount = 0
        formula=[]
        formula_1 = totalhra
        formula_2 = totalbasic * 0.5
        formula_3 = rent_paid - (0.1 * totalbasic) 
        formula_3 = 0 if formula_3 < 0 else formula_3
        formula.append(formula_1) 
        formula.append(formula_2)
        formula.append(formula_3) 
        hra_exempted_amount = min(formula)
        ytd_summary_it_deduction_components['HRA Exempted Amount'] = hra_exempted_amount
        del ytd_summary_it_deduction_components['house_rent']

        ytd_summary_it_deduction_components['Professional Tax'] = 2400
        standard_deduction = 50000
        ytd_summary_it_deduction_components['Standard Deduction'] = standard_deduction

        ytd_summary_it_income_components = {'Other Income':ytd_summary_it_deduction_components['other_income'] , 'Income Lose House Property':ytd_summary_it_deduction_components['income_lose_house_property']}
        del ytd_summary_it_deduction_components['other_income']
        del ytd_summary_it_deduction_components['income_lose_house_property']

# ===================================== OLD REGIME =====================================
        taxo=0
        tottaxo=0
        surchargeo=0
        for key,values in ytd_summary_it_deduction_components.items():
            taxable_amount -= values
        for key,values in ytd_summary_it_income_components.items():
            taxable_amount += values
        taxable_amount += ytd_summary_it_deduction_component_last_employer['Total Income After Exemptions']

        if taxable_amount > 0 and taxable_amount <= 250000:
            taxo = 0
        elif taxable_amount > 250000 and taxable_amount <= 500000:
            taxo = ((taxable_amount - 250000) * .05)
        elif taxable_amount > 500000 and taxable_amount <= 1000000:
            taxo = ((taxable_amount - 500000) * .20)+12500
        elif taxable_amount > 1000000:
            taxo = ((taxable_amount - 1000000) * .30)+112500
        else:
            taxo= 0

        if taxable_amount <= 500000:
            taxo = 0
        surchargeo = 0
        if taxable_amount > 5000000 and taxable_amount <= 10000000:
            surchargeo = taxo * .10
            # /* check Marginal Relif*/
            if taxable_amount > 5000000 and taxable_amount <= 5195896:
                surchargeo = (taxable_amount - 5000000) * .70
                surchargeo = surchargeo + 0
        elif taxable_amount > 10000000 and taxable_amount <= 20000000:
            surchargeo = taxo * .15
            # /* check Marginal Relif*/
            if taxable_amount > 10000000 and taxable_amount <= 10214695:
                surchargeo = (taxable_amount - 10000000) * .70
                surchargeo = surchargeo + 281250
        elif taxable_amount > 20000000 and taxable_amount <= 50000000:
            surchargeo = taxo * .25
            # /* check Marginal Relif*/
            if taxable_amount > 20000000 and taxable_amount <= 20930000:
                surchargeo = (taxable_amount - 20000000) * .70
                surchargeo = surchargeo + 871875
        elif taxable_amount > 50000000:
            surchargeo = taxo * .37
            # /* check Marginal Relif*/
            if taxable_amount > 50000000 and taxable_amount <= 53017827:
                surchargeo = (taxable_amount - 50000000) * .70
                surchargeo = surchargeo + 3703125
        cesso = 0
        if taxo > 0:
            cesso =  (taxo + surchargeo) * .04
        tottaxo = taxo + cesso + surchargeo

# ===================================== NEW REGIME =====================================
        taxo_new_regime=0
        tottaxo_new_regime=0
        surchargen_new_regime=0
        taxable_amount_new_regime = ytd_summary_it_statement_data['Income']['Total']['Total']

        for key,values in ytd_summary_it_income_components.items():
            taxable_amount_new_regime += values
        taxable_amount_new_regime += ytd_summary_it_deduction_component_last_employer['Total Income After Exemptions']
        taxable_amount_new_regime -= standard_deduction

        if taxable_amount_new_regime > 0 and taxable_amount_new_regime <= 300000:
            taxo_new_regime = 0
        elif taxable_amount_new_regime > 300000 and taxable_amount_new_regime <= 600000:
            taxo_new_regime = ((taxable_amount_new_regime - 300000) * .05)
        elif taxable_amount_new_regime > 600000 and taxable_amount_new_regime <= 900000:
            taxo_new_regime = ((taxable_amount_new_regime - 600000) * .10) + 15000
        elif taxable_amount_new_regime > 900000 and taxable_amount_new_regime <= 1200000:
            taxo_new_regime = ((taxable_amount_new_regime - 900000) * .15) + 15000 + 30000
        elif taxable_amount_new_regime > 1200000 and taxable_amount_new_regime <= 1500000:
            taxo_new_regime = ((taxable_amount_new_regime - 1200000) * .20) + 15000 + 30000 + 45000
        elif taxable_amount_new_regime > 1500000:
            taxo_new_regime = ((taxable_amount_new_regime - 1500000) * .30) + 15000 + 30000 + 45000 + 60000
        else:
            taxo_new_regime=0

        if taxable_amount_new_regime <= 700000:
            taxo_new_regime=0
        surchargen_new_regime = 0
        if taxable_amount_new_regime > 5000000 and taxable_amount_new_regime <= 10000000:
            surchargen_new_regime = taxo_new_regime * .10
            # /* check Marginal Relif*/
            if taxable_amount_new_regime > 5000000 and taxable_amount_new_regime <= 5195896:
                surchargen_new_regime = (taxable_amount_new_regime - 5000000) * .70
                surchargen_new_regime = surchargen_new_regime + 0
        elif taxable_amount_new_regime > 10000000 and taxable_amount_new_regime <= 20000000:
            surchargen_new_regime = taxo_new_regime * .15
            # /* check Marginal Relif*/
            if taxable_amount_new_regime > 10000000 and taxable_amount_new_regime <= 10214695:
                surchargen_new_regime = (taxable_amount_new_regime - 10000000) * .70
                surchargen_new_regime = surchargen_new_regime + 273750
        elif taxable_amount_new_regime > 20000000 and taxable_amount_new_regime <= 50000000:
            surchargen_new_regime = taxo_new_regime * .25
            # /* check Marginal Relif*/
            if taxable_amount_new_regime > 20000000 and taxable_amount_new_regime <= 20930000:
                surchargen_new_regime = (taxable_amount_new_regime - 20000000) * .70
                surchargen_new_regime = surchargen_new_regime + 860625
        elif taxable_amount_new_regime > 50000000:
            surchargen_new_regime = taxo_new_regime * .25
            # /* check Marginal Relif*/
            if taxable_amount_new_regime > 50000000 and taxable_amount_new_regime <= 53017827:
                surchargen_new_regime = (taxable_amount_new_regime - 50000000) * .70
                surchargen_new_regime = surchargen_new_regime + 3684375
        cessn_new_regime = 0
        if taxo_new_regime > 0:
            cessn_new_regime =  (taxo_new_regime + surchargen_new_regime) * .04
            tottaxo_new_regime = taxo_new_regime + cessn_new_regime + surchargen_new_regime

        # if taxable_amount < 0:
        #     taxable_amount = 0
        # if tottaxo_new_regime < 0:
        #     tottaxo_new_regime = 0
        tax_amount_old_regime_dict = {'Raw Tax':"{:.2f}".format(taxo),'Surcharge':"{:.2f}".format(surchargeo),'Health & Edu.Cess':"{:.2f}".format(cesso),'Total Tax Amount' : "{:.2f}".format(tottaxo)}
        tax_amount_new_regime_dict = {'Raw Tax':"{:.2f}".format(taxo_new_regime),'Surcharge':"{:.2f}".format(surchargen_new_regime),'Health & Edu.Cess':"{:.2f}".format(cessn_new_regime),'Total Tax Amount' : "{:.2f}".format(tottaxo_new_regime)}

        _logger.info("Current Financial Year: %s", it_declaration_info[1].financial_year.name)
        _logger.info("Ytd Summary It Income Component Last Employer: %s", ytd_summary_it_deduction_component_last_employer)
        _logger.info("Ytd Summary It Income Components: %s", ytd_summary_it_income_components)
        _logger.info("Ytd Summary It Deduction Components: %s", ytd_summary_it_deduction_components)
        _logger.info("Total Taxable Amount Old Regime: %s", taxable_amount)
        _logger.info("Total Tax Amount Old Regime: %s", tax_amount_old_regime_dict)
        _logger.info("Total Taxable Amount New Regime: %s", taxable_amount_new_regime)
        _logger.info("Total Tax Amount New Regime: %s", tax_amount_new_regime_dict)

        if employee :
            data = {
                'current_financial_year' : it_declaration_info[1].financial_year.name,
                'ytd_summary_it_statement_data' : ytd_summary_it_statement_data,
                'ytd_summary_it_income_components' : ytd_summary_it_income_components,
                'ytd_summary_it_deduction_component_last_employer' : ytd_summary_it_deduction_component_last_employer,
                'ytd_summary_it_deduction_components' : ytd_summary_it_deduction_components,
                'tax_amount_old_regime_dict' : tax_amount_old_regime_dict,
                'tax_amount_new_regime_dict' : tax_amount_new_regime_dict,
            }
            return data
        else:
            return False
