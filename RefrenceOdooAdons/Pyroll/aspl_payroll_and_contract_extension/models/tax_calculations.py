from odoo import _, exceptions, models, api, fields
from datetime import date



class tax_calculations(models.Model):
    _inherit = 'hr.payslip'

    financial_year = fields.Char(string="Financial Year",tracking=True)
    status = fields.Selection( [
            ("locked", "Locked"),
            ("unlocked", "Unlocked"),
            ("submitted", "Submitted"),
        ],
        tracking=True,
        string="Status"

    )

    #Income From Other Sources
    # other_income = fields.Integer(string="Other Income",tracking=True)
    # income_from_house_properties = fields.Integer(string="Income From House Properties",tracking=True)

    #Tax Paid Till Date
    # deduction_through_payroll = fields.Integer(string="Deduction Through Payroll",tracking=True)
    # direct_tds = fields.Integer(string="Direct TDS",tracking=True)
    # previous_employment = fields.Integer(string="Previous Employment",tracking=True)

    #Sec 80C
    five_year_fixed_deposite = fields.Integer(string="80C Five Years of Fixed Deposite in Scheduled Bank",tracking=True)
    children_tution_fees = fields.Integer(string="80C Children Tuition Fees",tracking=True)
    contribution_to_pension_fund = fields.Integer(string="80CCC Contribution to Pension Fund",tracking=True)
    deposite_in_nsc = fields.Integer(string="80C Deposit in NSC",tracking=True)
    deposite_in_nss = fields.Integer(string="80C Deposit in NSS",tracking=True)
    deposite_in_post_office = fields.Integer(string="80C Deposit in Post Office Savings Schemes",tracking=True)
    equity_linked_saving_scheme = fields.Integer(string="80C Equity Linked Savings Scheme ( ELSS )",tracking=True)
    interest_on_nsc = fields.Integer(string="80C Interest on NSC Reinvested",tracking=True)
    kisan_vikas_patra = fields.Integer(string="80C Kisan Vikas Patra (KVP)",tracking=True)
    life_insurance_premium = fields.Integer(string="80C Life Insurance Premium",tracking=True)
    long_term_infrastructure_bond = fields.Integer(string="80C Long term Infrastructure Bonds",tracking=True)
    mutual_funds = fields.Integer(string="80C Mutual Funds",tracking=True)
    nabard_rural_funds = fields.Integer(string="80C NABARD Rural Bonds",tracking=True)
    national_pension_scheme = fields.Integer(string="80C National Pension Scheme",tracking=True)
    nhb_scheme = fields.Integer(string="80C NHB Scheme",tracking=True)
    post_office_time_deposite = fields.Integer(string="80C Post office time deposit for 5 years",tracking=True)
    pradhan_mantri_suraksha_bima = fields.Integer(string="80C Pradhan Mantri Suraksha Bima Yojana",tracking=True)
    public_provident_fund = fields.Integer(string="80C Public Provident Fund",tracking=True)
    repayment_of_housing_loan = fields.Integer(string="80C Repayment of Housing loan(Principal amount)",tracking=True)
    stamp_duty_registration_charges = fields.Integer(string="80C Stamp duty and Registration charges",tracking=True)
    sukanya_samriddhi_yojana = fields.Integer(string="80C Sukanya Samriddhi Yojana",tracking=True)
    unit_linked_insurance_premium = fields.Integer(string="80C Unit Linked Insurance Premium (ULIP)",tracking=True)
    total_declared_80c = fields.Integer(compute='onchange_function_80c',string="Total declared in ₹",tracking=True)

    @api.onchange('five_year_fixed_deposite','children_tution_fees','contribution_to_pension_fund','deposite_in_nsc','deposite_in_nss','deposite_in_post_office','equity_linked_saving_scheme','interest_on_nsc','kisan_vikas_patra','life_insurance_premium','long_term_infrastructure_bond','mutual_funds','nabard_rural_funds','national_pension_scheme','nhb_scheme','post_office_time_deposite','pradhan_mantri_suraksha_bima','public_provident_fund','repayment_of_housing_loan','stamp_duty_registration_charges','sukanya_samriddhi_yojana','unit_linked_insurance_premium')
    def onchange_function_80c(self):
        self.total_declared_80c = self.five_year_fixed_deposite+self.children_tution_fees+self.contribution_to_pension_fund+self.deposite_in_nsc+self.deposite_in_nss+self.deposite_in_post_office+self.equity_linked_saving_scheme+self.interest_on_nsc+self.kisan_vikas_patra+self.life_insurance_premium+self.long_term_infrastructure_bond+self.mutual_funds+self.nabard_rural_funds+self.national_pension_scheme+self.nhb_scheme+self.post_office_time_deposite+self.pradhan_mantri_suraksha_bima+self.public_provident_fund+self.repayment_of_housing_loan+self.stamp_duty_registration_charges+self.sukanya_samriddhi_yojana+self.unit_linked_insurance_premium


    #Other Chapter VI-A Deductions
    additional_interest_on_housing_2016 = fields.Integer(string="80EE Additional Interest on housing loan borrowed as on 1st Apr 2016",tracking=True)
    additional_interest_on_housing_2019 = fields.Integer(string="80EEA Additional Interest on Housing loan borrowed as on 1st Apr 2019",tracking=True)
    interest_on_electric_vehicle = fields.Integer(string="80EEB Interest on Electric Vehicle borrowed as on 1st Apr 2019",tracking=True)
    contribution_to_nps = fields.Integer(string="80CCD1(B) Contribution to NPS 2015",tracking=True)
    interest_on_savings_etc = fields.Integer(string="80TTB Interest on Deposits in Savings Account, FDs, Post Office And Cooperative Society for Senior Citizen",tracking=True)
    superannuation_exemption = fields.Integer(string="10(13) Superannuation Exemption",tracking=True)
    donation_100_exemption = fields.Integer(string="80G Donation - 100 Percent Exemption",tracking=True)
    donation_50_exemption = fields.Integer(string="80G Donation - 50 Percent Exemption",tracking=True)
    donation_children_education = fields.Integer(string="80G Donation - Children Education",tracking=True)
    donation_political_parties = fields.Integer(string="80G Donation - Political Parties",tracking=True)
    interests_on_deposites = fields.Integer(string="80TTA Interest on Deposits in Savings Account, FDs, Post Office And Cooperative Society",tracking=True)
    interests_on_loan_self_higher = fields.Integer(string="80E Interest on Loan of higher Self education",tracking=True)
    medical_insurance_for_handicapped = fields.Integer(string="80DD Medical Treatment / Insurance of handicapped Dependant",tracking=True)
    medical_insurance_for_handicapped_severe = fields.Integer(string="80DD Medical Treatment / Insurance of handicapped Dependant (Severe)",tracking=True)
    medical_insurance_specified_disease_only = fields.Integer(string="80DDB Medical Treatment ( Specified Disease only )",tracking=True)
    medical_insurance_specified_disease_only_senior_citizen = fields.Integer(string="80DDB Medical Treatment (Specified Disease only)- Senior Citizen",tracking=True)
    permanent_physical_disability_above_80 = fields.Integer(string="80U Permanent Physical Disability (Above 80 percent)",tracking=True)
    permanent_physical_disability_40_80= fields.Integer(string="80U Permanent Physical Disability (Between 40 - 80 Percent)",tracking=True)
    rajiv_gandhi_equity_scheme = fields.Integer(string="80CCG Rajiv Gandhi Equity Scheme",tracking=True)
    total_declared_vi_a_deductions = fields.Integer(compute="onchange_function_deduction",string="Total declared in ₹",tracking=True)

    @api.onchange('additional_interest_on_housing_2016','additional_interest_on_housing_2019','interest_on_electric_vehicle','contribution_to_nps','interest_on_savings_etc','superannuation_exemption','donation_100_exemption','donation_50_exemption','donation_children_education','donation_political_parties','interests_on_deposites','interests_on_loan_self_higher','medical_insurance_for_handicapped','medical_insurance_for_handicapped_severe','medical_insurance_specified_disease_only','medical_insurance_specified_disease_only_senior_citizen','permanent_physical_disability_above_80','permanent_physical_disability_40_80','rajiv_gandhi_equity_scheme')
    def onchange_function_deduction(self):
        self.total_declared_vi_a_deductions = self.additional_interest_on_housing_2016+self.additional_interest_on_housing_2019+self.interest_on_electric_vehicle+self.contribution_to_nps+self.interest_on_savings_etc+self.superannuation_exemption+self.donation_100_exemption+self.donation_50_exemption+self.donation_children_education+self.donation_political_parties+self.interests_on_deposites+self.interests_on_loan_self_higher+self.medical_insurance_for_handicapped+self.medical_insurance_for_handicapped_severe+self.medical_insurance_specified_disease_only+self.medical_insurance_specified_disease_only_senior_citizen+self.permanent_physical_disability_above_80+self.permanent_physical_disability_40_80+self.rajiv_gandhi_equity_scheme

    #House Rent Allowance
    house_allowance_ids = fields.One2many('homerent.allowance','house_allowance_id', string="House Rent Allowances")
    total_declared_hra = fields.Integer(compute="onchange_function_hra",string="Total declared in ₹",tracking=True)

    @api.onchange(house_allowance_ids)
    def onchange_function_hra(self):
        annual_rent = 0
        total = 0 
        for annual_rent in self.house_allowance_ids:
            total += annual_rent.annual_rent_amount 
        self.total_declared_hra=total


    #Medical (Sec 80D)
    declared_amount_1 = fields.Integer(string="80D Preventive Health Checkup - Dependant Parents",tracking=True)
    declared_amount_2 = fields.Integer(string="80D Medical Bills - Senior Citizen",tracking=True)
    declared_amount_3 = fields.Integer(string="80D Medical Insurance Premium",tracking=True)
    declared_amount_4 = fields.Integer(string="80D Medical Insurance Premium - Dependant Parents",tracking=True)
    declared_amount_5 = fields.Integer(string="80D Preventive Health Check-up",tracking=True)
    age = fields.Selection( [
            ("< 60", "< 60"),
            ("60 - 79", "60 - 79"),
            (">= 80", ">= 80"),
        ],
        tracking=True,
        string="Age"
    )
    age_dependant = fields.Selection( [
            ("< 60", "< 60"),
            ("60 - 79", "60 - 79"),
            (">= 80", ">= 80"),
        ],
        tracking=True,
        string="Age"
    )
    total_declared_medical = fields.Integer(compute="onchange_function_medical",string="Total declared in ₹",tracking=True)

    @api.onchange('declared_amount_1','declared_amount_2','declared_amount_3','declared_amount_4','declared_amount_5')
    def onchange_function_medical(self):
        self.total_declared_medical = self.declared_amount_1+self.declared_amount_2+self.declared_amount_3+self.declared_amount_4+self.declared_amount_5

    #Income/loss from House Property
    income_loss_ids = fields.One2many('income.loss','income_loss_id', string="Income/Loss From House Property")
    interest_on_housing_loan = fields.Integer(string="Interest on Housing Loan (Self Occupied) in ₹",tracking=True)
    lender_self_name = fields.Char(string="Lender’s Name",tracking=True)
    lender_self_pan  = fields.Char(string="Lender’s PAN",tracking=True)
    total_income_loss = fields.Integer(compute="onchange_function_total",string="Total Income/Loss from Let Out Property",tracking=True)
    total_exemption = fields.Integer(compute="onchange_function_exemption",string="Total Exemption in ₹",tracking=True)

    @api.onchange('income_loss_ids')
    def onchange_function_total(self):
        total = 0
        grand_total = 0
        for total in self.income_loss_ids:
            grand_total += total.income_loss_let_out
        self.total_income_loss = grand_total

    @api.onchange('income_loss_ids')
    def onchange_function_exemption(self):
        self.total_exemption = -self.interest_on_housing_loan + self.total_income_loss 


    #Other Income
    other_income_ids = fields.One2many('other.income','other_income_id', string="Other Income")
    total_declared_other = fields.Integer(compute="onchange_function_other",string="Total declared in ₹",tracking=True)

    @api.onchange('other_income_ids')
    def onchange_function_other(self):
        other = 0
        other_total = 0
        for other in self.other_income_ids:
            other_total += other.declared_amount
        self.total_declared_other = other_total

    #Income From Previous Employer
    income_after_exemptions = fields.Integer(string="Income after Exemptions",tracking=True)
    professional_tax = fields.Integer(string="Profession Tax - PT",tracking=True)
    provident_fund = fields.Integer(string="Provident Fund - PF",tracking=True)
    tax_on_income = fields.Integer(string="Tax On Income",tracking=True)
    surcharge = fields.Integer(string="Surcharge",tracking=True)
    education_cess = fields.Integer(string="Education Cess",tracking=True)
    total_tax_previous_employer= fields.Integer(compute="depends_function_previous",string="Total Tax in ₹", help="Total Tax = Tax On Income + Surcharge + Education Cess",tracking=True)
    
    @api.depends('tax_on_income','surcharge','education_cess')
    def depends_function_previous(self):
        self.total_tax_previous_employer = self.tax_on_income - self.surcharge - self.education_cess

class Hra(models.TransientModel):
    _name = 'homerent.allowance'
    _description = 'House Rent Allowances'

    house_allowance_id = fields.Many2one('hr.payslip', string="House Rent Allowances")
    from_possession = fields.Date(string="From",tracking=True)
    to_possession = fields.Date(string="To",tracking=True)
    monthly_rent_amount = fields.Integer(string="Monthly Rent Amount",tracking=True)
    annual_rent_amount =  fields.Integer(compute="depends_function_annual_rent",string="Annual Rent Amount",tracking=True)
    house_name_number = fields.Char(string="House Name/Number",tracking=True)
    street_area_locality = fields.Char(string="Street/Area/Locality",tracking=True)
    town_city = fields.Char(string="Town/City",tracking=True)
    state = fields.Char(string="State",tracking=True)
    country = fields.Char(string="Country",tracking=True)
    pin_code = fields.Integer(string="Pincode",tracking=True)
    pan_info_landlord = fields.Selection( [
            ("yes", "Yes"),
            ("no", "No"),
        ],
        tracking=True,
    )
    landlord_name = fields.Char(string="Landlord's Name", tracking=True)
    landlord_pan = fields.Char(string="Landlord's PAN", tracking=True)
    landlord_house_name_number = fields.Char(string="House Name/Number", tracking=True)
    landlord_street_area = fields.Char(string="Street/Area/Locality", tracking=True)
    landlord_town_city = fields.Char(string="Town/City", tracking=True)
    landlord_pincode = fields.Char(string="Pincode", tracking=True)
       
    @api.depends('monthly_rent_amount')
    def depends_function_annual_rent(self):
        for rent in self:
            rent.annual_rent_amount = rent.monthly_rent_amount*12

    

class Income_loss_from_house_property(models.TransientModel):
    _name = 'income.loss'
    _description = 'Income or Loss From House Property'


    income_loss_id = fields.Many2one('hr.payslip', string="Income/Loss From House Property")
    annual_letable_received = fields.Integer(string="Annual Letable Value/Rent Received or Receivable",tracking=True)
    munciple_tax_paid = fields.Integer(string="Less: Municipal Taxes Paid During the Year",tracking=True)
    unreleased_rent = fields.Integer(string="Less: Unrealized Rent",tracking=True)
    tax_on_income = fields.Integer(compute="depends_function_net_value",string="NET VALUE IN ₹",tracking=True)
    standard_deduction = fields.Integer(compute="depends_function_standard_deduction",string="Standard Deduction at 30 Percent of Net Annual Value",tracking=True)
    interest_housing_loan = fields.Integer(string="Interest on Housing Loan",tracking=True)
    lender_name = fields.Char(string="Lender’s Name",tracking=True)
    lender_pan  = fields.Char(string="Lender’s PAN",tracking=True)
    income_loss_let_out = fields.Integer(compute="depends_function_income",string="Income/Loss from Let Out Property",tracking=True)
   
    @api.depends('annual_letable_received','munciple_tax_paid','unreleased_rent')
    def depends_function_net_value(self):
        for rent in self:
            rent.tax_on_income = rent.annual_letable_received-(rent.munciple_tax_paid+rent.unreleased_rent)
    
    @api.depends('tax_on_income')
    def depends_function_standard_deduction(self):
        for deduction in self:
            deduction.standard_deduction = deduction.tax_on_income *0.30
    
    @api.depends('tax_on_income','standard_deduction','interest_housing_loan')
    def depends_function_income(self):
        for income in self:
            income.income_loss_let_out = income.tax_on_income - income.standard_deduction -income.interest_housing_loan

class Other_income(models.TransientModel):
    _name = 'other.income'
    _description = 'Other Income'

    other_income_id = fields.Many2one('hr.payslip', string="Other Income")
    particulars = fields.Char(string="Particulars")
    declared_amount = fields.Integer(string="Declared Amount")



    