# -*- coding: utf-8 -*-
from datetime import datetime,timedelta
from odoo.exceptions import ValidationError, UserError
from odoo import models, fields, api, _, exceptions
from bs4 import BeautifulSoup
from odoo.exceptions import ValidationError
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

RATINGS = [
    ('1', 'Very Poor'),
    ('2', 'Poor'),
    ('3', 'Average'),
    ('4', 'Good'),
    ('5', 'Excellent')
]

ADDRESS = [
    ('202, Parishram Complex, Mithakhali Six Roads Navrangpura',
     '202, Parishram Complex,Mithakhali Six Roads Navrangpura'),
    ('online', 'Online'),
]


def get_experience(exp):
    total_months = exp
    years, months = divmod(total_months, 12)
    return f"{years} year {months} months"


def calculate_years_months(total_exp, year, month):
    total_exp_years = total_exp
    cal_years = round(total_exp_years // 12)
    cal_months = round(total_exp_years % 12)
    years = cal_years + year
    months = month+cal_months
    if months >= 12:
        years += round(months//12)
        months = round(months % 12)
        return years, months
    return years, months


class CurrentCompany(models.Model):
    _name = 'current.company'
    _description = 'Current Company'

    name = fields.Char("Company Name")
    # candidate_ids = fields.One2many('res.partner', 'current_company_id', string="Candidates")
    all_candidates_count = fields.Integer(compute='_compute_all_candidates_count', string='Candidate Count')

    def _compute_all_candidates_count(self):
        res_partner_obj = self.env['res.partner'].search(
            [('current_company_id', '=', self.id)])
        for rec in self:
            rec.all_candidates_count = len(res_partner_obj)


class CurrentLocation(models.Model):
    _name = "current.location.city"
    _description = "Current Location City"
    _rec_name = 'location_name'

    location_name = fields.Char("Location Name", required=True)
    location_id = fields.Integer("Location Id")


class Partner(models.Model):
    _inherit = 'res.partner'

    @api.depends('total_exp_years')
    def _calculate_current_experience(self):
        for partner in self:
            if partner.total_exp_years:
                if partner.create_date:
                    application_create_date = datetime.strftime(partner.create_date, '%Y:%m:%d')
                    experience_in_day = int(
                        (datetime.now().date() - datetime.strptime(application_create_date, '%Y:%m:%d').date()).days)
                    year = experience_in_day // 365
                    month = (experience_in_day % 365) // 30
                    exp = ""
                    years = 0
                    months = 0
                    experience = ""
                    if partner.total_exp_years > 1:
                        experience += get_experience(int(partner.total_exp_years))
                        calculate = calculate_years_months(partner.total_exp_years, year, month)
                        years += calculate[0]
                        months += calculate[-1]
                    else:
                        experience += get_experience(int(partner.total_exp_years))
                        calculate = calculate_years_months(partner.total_exp_years, year, month)
                        years += calculate[0]
                        months += calculate[-1]
                    if year >= 0:
                        exp = exp + str(years) + " year "
                    if month >= 0:
                        exp = exp + str(months) + " months "
                    partner.current_experience = exp
                    partner.total_exp = experience
                else:
                    partner.total_exp = 0
                    partner.current_experience = 0
            else:
                partner.total_exp = 0
                partner.current_experience = 0

    name = fields.Char(index=True)
    mobile = fields.Char()
    email = fields.Char()
    # origin = fields.Many2one('utm.source', 'Source', help="This is the source of the link")
    type_id = fields.Many2one('hr.recruitment.degree', "Degree")
    job_id = fields.Many2one('hr.job', "Applied Job", tracking=True)
    current_company_id = fields.Many2one('current.company', "Current Company")
    current_location_city = fields.Many2one('current.location.city', 'Current City')
    date_received = fields.Date(string='Date Received')
    stage = fields.Char(string='Stage')
    categ_ids = fields.Many2many('hr.applicant.category', string="Skills")
    salary_current = fields.Integer("Current Salary", group_operator="avg", help="Current Salary of Applicant",
                                  )  # tracking=True
    salary_expected = fields.Integer("Expected Salary", group_operator="avg", help="Salary Expected by Applicant",
                                   )  # tracking=True
    partner_id = fields.Many2one('res.partner', 'Referred By', ondelete='set null',
                                 tracking=True, domain=[('is_employee', '=', True)])
    is_applicant = fields.Boolean(string="Is Applicant")
    is_candidate = fields.Boolean(string="Is Candidate")
    is_employee = fields.Boolean(string="Is Employee")
    in_application = fields.Boolean(string="In Application")
    active_employee = fields.Boolean("Active Employee", readonly=True)
    total_exp_years = fields.Integer(string="Experience in Months")
    total_exp = fields.Char(string="Total Experience")
    current_experience = fields.Char(string="Current Experience", compute='_calculate_current_experience')
    linked_in_profile = fields.Char('LinkedIn Profile')
    year_of_passing = fields.Integer('Year of Passing')
    job_opening_id = fields.Many2one('job.opening', "Job Opening")
    job_opening_ids = fields.Many2many('job.opening', string="Job Openings")
    v9_an_id = fields.Integer(string='V9 Application ID')
    source_id = fields.Many2one('utm.source', 'Source',
                                help="This is the source of the link")
    user_id = fields.Many2one(
        'res.users', "Sales Person",
        store=True,
        readonly=True)
    sourced_by = fields.Many2one('res.users', default=lambda self: self.env.user.id)
    candidate_skill_ids = fields.One2many('hr.candidate.skill', 'partner_id', string="Skills")
    # Added for manage multi application to single contact
    all_application_count = fields.Integer(compute='_compute_all_application_count',
                                           string="All Application Count")
    private_note = fields.Text("Private Note")
    description = fields.Text('Application Summary')
    app_status = fields.Boolean(compute='_compute_app_status', string='Status')
    active = fields.Boolean(default=True)
    aspire_candidate_id = fields.Integer("Candi Id")

    # Update partner as candidate_applicant_employee
    @api.model
    def _update_partner(self):
        # Step 1:- Update with false to all partners
        partners = self.env['res.partner'].search([])
        for partner in partners:
            partner.write({
                'active_employee': False,
                'is_employee': False,
                'is_applicant': False,
                'is_candidate': False,
            })
        # Step 2:- Update partner as candidate based on Skills
        skill_obj = self.env['hr.skill'].search([]).ids
        candidate_in_partners = self.env['res.partner'].search([('categ_ids', 'in', skill_obj)])
        for partner in candidate_in_partners:
            partner.write({
                'is_candidate': True,
                'active_employee': False,
                'is_employee': False,
                'is_applicant': False,
            })
        # Step 3:- Update partner as applicant
        partner_ids_obj = self.env['res.partner'].search([]).ids
        applicant_ids = self.env['hr.applicant'].search([('partner_id', 'in', partner_ids_obj)])
        for applicant in applicant_ids:
            applicant.partner_id.write({
                'is_applicant': True,
                'active_employee': False,
                'is_employee': False,
                'is_candidate': True,
                'in_application': True,
            })
        # Step 4:- Update partner as employee
        active_emp_ids = self.env['hr.employee'].search([('with_organization', '=', True)]).ids
        active_users = self.user_id.search([('employee_id', 'in', active_emp_ids)])
        for active in active_users:
            active.partner_id.write({
                'is_employee': True,
                'active_employee': True,
                'is_applicant': False,
                'is_candidate': True,
            })

    # Update partner as active employee
    @api.model
    def _active_employee(self):
        # First deactivate all partner
        active_emp_partner_obj = self.partner_id.search([('active_employee', '=', True)])
        for de_active_partner in active_emp_partner_obj:
            de_active_partner.write({'active_employee': False})
        active_emp_ids = self.env['hr.employee'].search([('with_organization', '=', True)]).ids
        active_users = self.user_id.search([('employee_id', 'in', active_emp_ids)])
        for active in active_users:
            active.partner_id.write({
                'active_employee': True,
                'is_employee': True,
                'is_applicant': False,
                'is_candidate': False,
            })
        # inactive_emp_ids = self.env['hr.employee'].search([('with_organization', '=', False)]).ids
        # inactive_users = self.user_id.search([('employee_id', 'in', inactive_emp_ids)])
        # for inactive in inactive_users:
        #     partner_obj = self.partner_id.search([('email', '=', inactive.login)])
        #     partner_obj.write({
        #         'is_employee': True,
        #         'is_applicant': False,
        #         'is_candidate': False,
        #     })

    def _compute_app_status(self):
        for rec in self:
            rec.app_status = False
            application_obj = self.env['hr.applicant'].search(
                [('partner_id', '=', rec.id)])
            for app in application_obj:
                if app.active:
                    rec.app_status = True

    def _compute_all_application_count(self):
        for applicant in self:
            application_obj = self.env['hr.applicant'].search(
                [('partner_id', '=', applicant.id), ('active', 'in', [True, False])])
            for job in self:
                job.all_application_count = len(application_obj)

    @api.model
    def create_application(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _("Move To Application"),
            'res_model': 'transfer.to.application',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_ids': self.env.context.get('active_ids')},
        }
    '''
        hr_application = self.env['hr.applicant']
        job_opening_id = self.env.context.get('active_domain')[0][2]
        job_opening_obj = self.env['job.opening'].browse(job_opening_id)
        skill_lines = []
        for skill in job_opening_obj.opening_skill_ids:
            skill_lines.append([0, 0, {
                'skill_id': skill.skill_id.id,
                'skill_level_id': skill.skill_level_id.id,
                'skill_type_id': skill.skill_type_id.id,
                'level_progress': skill.level_progress,
            }
                                ])
        for rec in self:
            if hr_application.search([('active', 'in', [True])]).filtered(lambda p: p.partner_id.id == rec.id):
                pass
            else:
                applicant = hr_application.create({
                    'name': rec.name,
                    'partner_id': rec.id,
                    'partner_name': rec.name,
                    'email_from': rec.email,
                    'partner_phone': rec.phone,
                    'partner_mobile': rec.mobile,
                    'type_id': rec.type_id.id,
                    'source_id': rec.source_id.id,
                    'categ_ids': rec.categ_ids.ids,
                    'job_id': job_opening_obj.job_id.id,
                    'department_id': job_opening_obj.department_id.id,
                    'stage_id': self.env.ref('aspl_hr_recruitment.initial').id,
                    'user_id': job_opening_obj.user_id.id,
                    'job_opening_id': job_opening_id,
                    'private_note': rec.private_note,
                    'date_received': rec.date_received,
                    # 'message_main_attachment_id': rec.message_main_attachment_id.id,
                })
                applicant.update({'applicant_skill_ids': skill_lines})
                rec.in_application = True
    '''
    # Method added for create candidates based on the incoming email server.

    @api.model
    def message_new(self, msg, custom_values=None):
        """ Overrides mail_thread message_new that is called by the mail gateway
            through message_process.
            This override updates the document according to the email.
        """
        val = msg.get('from').split('<')[0]
        if '<' in msg.get('from'):
            email = (msg.get('from').split("<"))[1].split(">")[0]
        else:
            email = msg.get('from')

        defaults = {
            'name': val,
            'email': email,
            'date_received': fields.Date.context_today(self),
        }
        res_partner_obj = self.env['res.partner'].search([('email', '=', msg.get('from'))])
        if res_partner_obj:
            # self.env['res.partner'].search([('email', '=', msg.get('from'))]).unlink()
            self.env['candidate'].search([('email', '=', msg.get('from'))]).unlink()
        try:
            i = 0
            message_body = (msg.get('body'))
            soup = BeautifulSoup(message_body, "lxml")
            soup.unicode
            message_table = soup.find("table", border=1)
            message_body = soup.find('tbody')
            message_row = soup.find_all('tr')
            dist = {}
            for td in message_row:
                key = soup.find_all("td")[i].get_text()
                i = i + 2
                value = soup.find_all("td")[i].get_text()
                i = i + 1
                dist[str(key.strip('\n'))] = str(value.strip('\n'))
            if msg.get('priority'):
                defaults['priority'] = msg.get('priority')
            if custom_values:
                defaults.update(custom_values)

            if 'Full Name' in dist:
                defaults['name'] = dist['Full Name']
            if 'Email' in dist:
                defaults['email'] = dist['Email']
            if 'Contact Number' in dist:
                defaults['mobile'] = dist['Contact Number']
            if 'Current Location' in dist:
                location = dist['Current Location']
                existing_location_city = self.env['current.location.city']
                existing_location_city_id = existing_location_city.search([('location_name', '=', location.lower())],
                                                                          limit=1)
                if existing_location_city:
                    defaults['current_location_city'] = existing_location_city_id.id
                else:
                    location_city = existing_location_city.create({'location_name': location})
                    defaults['current_location_city'] = location_city.id
            '''
            if 'Total Experience' in dist:
                try:
                    defaults['total_exp_years'] = dist['Total Experience']
                except ValueError:
                    pass
            if 'Expected CTC' in dist:
                try:
                    defaults['salary_expected'] = float(dist['Expected CTC'])
                except ValueError:
                    pass
            if 'Current CTC' in dist:
                try:
                    defaults['salary_current'] = float(dist['Current CTC'])
                except ValueError:
                    pass
            if 'Notice Period' in dist:
                try:
                    defaults['availability'] = int(dist['Notice Period'])
                except ValueError:
                    pass
            '''

        except Exception as e:
            print(e)

        existing_email = self.env['res.partner'].search([('email', '=', email)])
        # custom model of OLD env

        multiple_candidates_emails = self.env['multiple.candidates.emails'].search([])
        allowed_emails = []

        if len(multiple_candidates_emails) > 0:
            for eml in multiple_candidates_emails:
                allowed_emails.append(eml.name)

        is_available = False
        if (len(existing_email) > 0 and email == existing_email[0].email) and (email not in allowed_emails):
            is_available = True

        blocked_emails = self.env['blocked.emails'].search([('name', '=', email)])
        if len(blocked_emails) > 0 and email == blocked_emails.name:
            pass
        elif is_available:
            return existing_email[0].write(defaults)
        else:
            result = super(Partner, self).message_new(msg, custom_values=defaults)
            result.write(defaults)
            return result


class Applicant(models.Model):
    _inherit = 'hr.applicant'

    def candidate_on_boarding_process(self):

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'candidate.onboarding.wizard',
            'view_type':'form',
            'view_mode':'form',
            'name':_('Candidate On-boarding Link'),
            'target':'new',
            'context': {'applicant_id': self.id},
        }   
    
    def get_attach_id(self):
        url = self.env['ir.config_parameter'].get_param('web.base.url')
        attachment_id_logo = self.env.ref('aspl_hr_recruitment.company_logo_data').sudo().id
        attachment_id_face_to_face = self.env.ref('aspl_hr_recruitment.interview_schedule_face_to_face').sudo().id
        attachment_id_telephonic = self.env.ref('aspl_hr_recruitment.interview_schedule_Telephonic').sudo().id

        return url ,attachment_id_logo ,attachment_id_face_to_face,attachment_id_telephonic

    def create_employee_from_aspire_applicant(self):
        activity_status = self.env['mail.activity.type'].search([('name', 'ilike','joined'),('res_model','ilike','hr.applicant')])
        context = self._context
        current_uid = self.env.context.get('uid') if self.env.context.get('uid') else context.get('uid')
        user = self.env['res.users'].browse(current_uid)
        _logger.info('Current User == %s %s',user.name,activity_status.name)
        self.write({
            'applicant_activity_ids':[(0,0,{
                'activity':activity_status.id,
                'track_date':datetime.now(),
                'user_id':user.id,
                'job_opening':self.job_opening_id.id
            })],
        })

        """ Create an hr.employee from the hr.applicants """
        status_ = self.env['hr.recruitment.stage'].search([('name', 'ilike', 'Joined')])
        self.write({'stage_id':status_})
        self.write({'offer':'joined'})
        self.write({'stage_status':'joined'})
        skill_lines = []
        skill_lines_dict = []
        employee = False
        employee_data = {}
        for applicant in self:
            contact_name = False
            if applicant.candidate_id:
                # address_id = applicant.candidate_id.address_get(['contact'])['contact']
                contact_name = applicant.candidate_id.display_name
            else:
                if not applicant.partner_name:
                    raise UserError(_('You must define a Contact Name for this applicant.'))
                new_partner_id = self.env['res.partner'].create({
                    'is_employee': True,
                    'is_candidate': True,
                    'is_applicant': False,
                    'type': 'private',
                    'name': applicant.partner_name,
                    'email': applicant.email_from,
                    'phone': applicant.partner_phone,
                    'mobile': applicant.partner_mobile,
                    'active_employee': True
                })
                applicant.partner_id = new_partner_id
                # address_id = new_partner_id.address_get(['contact'])['contact']
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
                    # 'address_home_id': address_id,
                    'default_department_id': applicant.department_id.id or False,
                    'default_address_id': applicant.company_id and applicant.company_id.partner_id
                                          and applicant.company_id.partner_id.id or False,
                    'default_work_email': applicant.email_from,
                    # applicant.department_id and applicant.department_id.company_id and applicant.department_id.company_id.email or False
                    'default_per_phone1': applicant.partner_mobile,  # department_id.company_id.phone
                    'default_personal_email':applicant.email_from,
                    'form_view_initial_mode': 'edit',
                    'default_applicant_id': applicant.ids,
                    'default_employee_skill_ids': skill_lines
                }
        dict_act_window = self.env['ir.actions.act_window']._for_xml_id('hr.open_view_employee_list')
        dict_act_window['context'] = employee_data
        return dict_act_window

    def create_employee_from_applicant(self):
        """ Create an hr.employee from the hr.applicants """
        skill_lines = []
        skill_lines_dict = []
        employee = False
        employee_data = {}
        for applicant in self:
            contact_name = False
            if applicant.candidate_id:
                # address_id = applicant.candidate_id.address_get(['contact'])['contact']
                contact_name = applicant.candidate_id.display_name
            else:
                if not applicant.partner_name:
                    raise UserError(_('You must define a Contact Name for this applicant.'))
                new_partner_id = self.env['candidate'].create({
                    'is_company': False,
                    'is_employee': True,
                    'is_candidate': True,
                    'is_applicant': False,
                    'type': 'private',
                    'name': applicant.partner_name,
                    'email': applicant.email_from,
                    'phone': applicant.partner_phone,
                    'mobile': applicant.partner_mobile,
                    'active_employee': True
                })
                applicant.partner_id = new_partner_id
                # address_id = new_partner_id.address_get(['contact'])['contact']
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
                    # 'address_home_id': address_id,
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
        

    
    def action_schedule_interview(self):
        if self.stage_id.name == 'Shortlisted':
            activity_data = self.env['mail.activity.type'].search([('name','=','First Interview')])
        else:
            activity_data = self.env['mail.activity.type'].search([('name','=','Second Interview')])

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'recruitment.send.interview.wizard',
            'view_type':'form',
            'view_mode':'form',
            'name':_('Interview Invitation'),
            'target':'new',
            'context': {'default_interview_round': activity_data.id},
        }
    
    @api.depends('current_ctc', 'salary_expected')
    def _calculate_expected_hike(self):
        for rec in self:
            if rec.current_ctc > 0 and rec.salary_expected > 0.0:
                rec.expected_hike = str(int((100 * (rec.salary_expected - rec.current_ctc)) / rec.current_ctc)) + "%"
            else:
                rec.expected_hike = ''

    @api.depends('current_ctc', 'salary_proposed')
    def _calculate_proposed_hike(self):
        for rec in self:
            if rec.current_ctc > 0 and rec.salary_expected > 0.0:
                rec.proposed_hike = str(int((100 * (rec.salary_proposed - rec.current_ctc)) / rec.current_ctc)) + "%"
            else:
                rec.proposed_hike = ''

    @api.model
    def default_get(self, fields):
        res = super(Applicant, self).default_get(fields)
        app_fk_que = self.env['applicant.feedback.que'].search([])
        questions = [que.name for que in app_fk_que]
        if app_fk_que:
            res['que1'] = questions[0]
            res['que2'] = questions[1]
            res['que3'] = questions[2]
            res['que4'] = questions[3]
            res['que5'] = questions[4]
        return res

    def _domain_get_reviewers(self):
        reviewers = self.env.ref('aspl_hr_recruitment.group_recruiter_user').users.ids
        return [('active', '=', True), ('id', 'in', reviewers)]

    def _domain_get_interviewers(self):
        interviewers = self.env.ref('aspl_hr_recruitment.group_recruiter_user').users.ids
        return [('active', '=', True), ('id', 'in', interviewers)]

    def _domain_get_recruiters(self):
        hr_managers = self.env.ref('hr_recruitment.group_hr_recruitment_manager').users.ids
        hr_officers = self.env.ref('hr_recruitment.group_hr_recruitment_user').users.ids
        if hr_managers and hr_officers:
            recruiters = hr_managers + hr_officers
        elif hr_managers:
            recruiters = hr_managers
        elif hr_officers:
            recruiters = hr_officers
        else:
            recruiters = []
        return [('active', '=', True), ('id', 'in', recruiters)]

    @api.depends('total_exp_years')
    def _calculate_current_experience(self):
        print("\nhr applicant\n", self.total_exp_years)
        if self.total_exp_years:
            application_create_date = datetime.strftime(self.create_date, '%Y:%m:%d')
            experience_in_day = int((datetime.now().date() - datetime.strptime(application_create_date, '%Y:%m:%d').date()).days)
            year = experience_in_day // 365
            month = (experience_in_day % 365) // 30
            exp = ""
            years = 0
            months = 0
            experience = ""
            if self.total_exp_years > 1:
                experience += get_experience(int(self.total_exp_years))
                calculate = calculate_years_months(self.total_exp_years, year, month)
                years += calculate[0]
                months += calculate[-1]
            else:
                experience += get_experience(int(self.total_exp_years))
                calculate = calculate_years_months(self.total_exp_years, year, month)
                years += calculate[0]
                months += calculate[-1]
            if year >= 0:
                exp = exp + str(years) + " year "
            if month >= 0:
                exp = exp + str(months) + " months "
            self.current_experience = exp
            self.total_exp = experience
        else:
            self.current_experience = 0
            self.total_exp = 0

    # def _get_job_opening_owner(self):
    #     for record in self:
    #         owner = record.job_opening_id
    #         owner_id = owner.owner_id
    #         print("owner == ",owner_id)
    #         self.job_opening_owner = owner_id.id

    # def _get_current_user(self):
    #     context = self._context
    #     current_uid = context.get('uid')
    #     user = self.env['res.users'].browse(current_uid)
    #     print("user == ",user)
    #     self.current_logged_user = user.id
        
    def _get_owner_and_current_user(self):
        context = self._context
        current_uid = self.env.context.get('uid') if self.env.context.get('uid') else context.get('uid')
        user = self.env['res.users'].browse(current_uid)

        for record in self:
            owner = record.job_opening_id
            owner_id = owner.owner_id

        if user.id == owner_id.id or self.env['res.users'].has_group('hr_recruitment.group_hr_recruitment_manager') or self.env['res.users'].has_group('hr_recruitment.group_hr_recruitment_user'):
            self.check_owner_and_current_user = True
        else:
            self.check_owner_and_current_user = False  

    name = fields.Char("Subject / Application Name", help="Email subject for applications sent via email")
    candidate_id = fields.Many2one('candidate', "Candidate", copy=False)
    user_id = fields.Many2one(
        'res.users', "Recruiter",
        tracking=True,
        store=True,
        readonly=False,
        domain=_domain_get_recruiters, default=lambda self: self.env.user)
    current_job_id = fields.Many2one('hr.job', "Current Job Opening", tracking=True)
    job_opening_id = fields.Many2one('job.opening', "Job Opening",
                                     )  # domain=_domain_get_active_opening
    job_opening_ids = fields.Many2many('job.opening', string="Job Openings")
    current_company_id = fields.Many2one('current.company', "Current Company")
    ready_to_relocate = fields.Boolean("Ready To Relocate")
    year_of_passing = fields.Integer('Year of Passing')
    current_location_city = fields.Many2one('current.location.city', 'Current City')
    date_received = fields.Date(string='Date Received')  # , required=True
    private_note = fields.Text("Private Note")
    reviewer_user_ids = fields.Many2many('res.users', 'hr_applicant_reviewer_user_rel', 'applicant_id', 'user_id',
                                         'Reviewer', tracking=True)
    interviewers_ids = fields.Many2many('res.users', 'res_users_hr_applicant_int_rel', 'user_id',
                                        'applicant_id', 'Interviewers')
    total_exp_years = fields.Integer(string="Experience in Months")
    total_exp = fields.Char(string="Total Experience")
    current_experience = fields.Char(string="Current Experience", compute='_calculate_current_experience')
    referred_id = fields.Many2one('res.partner', 'Referred By', ondelete='set null',
                                  tracking=True, domain=[('is_employee', '=', True)])
    # Override
    salary_proposed = fields.Integer("Proposed Salary", group_operator="avg", help="Salary Proposed by the Organisation",
                                   tracking=True)
    salary_expected = fields.Integer("Expected Salary", group_operator="avg", help="Salary Expected by Applicant",
                                   tracking=True)
    current_ctc = fields.Integer("Current CTC (Yearly)")
    expected_hike = fields.Char(compute='_calculate_expected_hike', string='Expected Hike')
    proposed_hike = fields.Char(compute='_calculate_proposed_hike', string='Proposed Hike')
    # resume_line_ids = fields.One2many('hr.resume.line', 'applicant_id', string="Resume lines")
    applicant_skill_ids = fields.One2many('hr.applicant.skill', 'applicant_id', string="Skills")
    feedbacks_ids = fields.One2many('int.feedbacks', 'applicant_id', string="Interviewer Skills Feedbacks")
    questions_ids = fields.One2many('app.questions.line', 'applicant_id', string="HR Questions")
    # app_fk_que_ans_ids = fields.One2many('app.feedback.que.ans.line', 'applicant_id', string="Applicant Feedbacks")
    interview = fields.Selection([
        ('na', "Applicant Not Available"),
        ('reschedule', "Re-Schedule"),
        ('done', "Done"),
    ], string='Interview Status')
    offer = fields.Selection([
        ('given', "Given"),
        ('accepted', "Accepted"),
        ('joined', "Joined"),
    ],default='given', string='Offer Status')
    

    screen_date = fields.Date("Screened Date")
    # interview_date = fields.Date("Interview Date")
    shortlisted_date = fields.Date("Shortlisted Date")
    offered_date = fields.Date("Offered Date")
    refused_date = fields.Date("Refused Date")
    source_user = fields.Many2one('res.users',compute='_calculate_current_user')
    work_location_id = fields.Many2one('hr.work.location', 'Work Location', store=True, readonly=False)
        


    availability2 = fields.Selection([
        ('immediate', 'Immediate'),
        ('less_than_a_month', 'Less than a month'),
        ('less_than_two_months', 'Less than two months'),
        ('less_than_three_months', 'Less than three months'),
        ('more_than_three_months', 'More than three months')
    ], 'Available In', tracking=True, track_visibility='always')
    expected_join_date = fields.Date('Expected Joining')
    applicant_activity_ids = fields.One2many('applicant.activity', 'applicant_id', "Applicant Activity")
    # job_opening_owner = fields.Integer(compute='_get_job_opening_owner', string="Job Opening Owner")
    # current_logged_user = fields.Integer(compute='_get_current_user',string="Current Logged user")
    check_owner_and_current_user = fields.Boolean(compute="_get_owner_and_current_user",string="Check owner and current user" )
    # custom fields for Applicant Feedbacks and Email templates
    # candidate_feedback = fields.Char('Candidate Feedback')
    # rating = fields.Selection([
    #     ('poor', 'Poor'),
    #     ('good', 'Good'),
    #     ('avg', 'Average'),
    #     ('exc', 'Excellent')
    # ], string='Ratings')
    # feedback_status = fields.Boolean("Feedback Received", default=False)
    telephonic = fields.Boolean("Telephonic")
    interview_type = fields.Char('Interview Type')
    interview_type_message = fields.Text('Interview Message')
    meeting_description = fields.Text("Meeting Description")
    interview_date = fields.Date('Interview Date')
    interview_time = fields.Char('At')
    interview_day = fields.Char('Day')
    stage_status = fields.Char('Stage Status', compute="_hide_button")
    que1 = fields.Char('Question 1')
    rating1 = fields.Selection(RATINGS, "Rating 1")
    que2 = fields.Char('Question 2')
    rating2 = fields.Selection(RATINGS, "Rating 2")
    que3 = fields.Char('Question 3')
    rating3 = fields.Selection(RATINGS, "Rating 3")
    que4 = fields.Char('Question 4')
    rating4 = fields.Selection(RATINGS, "Rating 4")
    que5 = fields.Char('Question 5')
    rating5 = fields.Selection(RATINGS, "Rating 5")
    feedback_status = fields.Boolean("Feedback Received", default=False)
    is_partner = fields.Boolean("Is Partner")
    is_candidate = fields.Boolean("Is Candidate")

    def _calculate_current_user(self):
        current_uid = request.env.context.get('uid')
        self.source_user = current_uid

    def _hide_button(self):
        _logger.info('Application == %s',self)
        for self in self:
            self.stage_status = 'O' if self.stage_id.name == 'Offered' else 'In'\
                if self.stage_id.name == 'New' else 'Int' if self.stage_id.name == 'Interview' else 'Sc' \
                if self.stage_id.name == 'Screened' else 'Sh' if self.stage_id.name == 'Shortlisted' else 'Sel' \
                if self.stage_id.name == 'Selected' else 'Jo' if self.stage_id.name == 'Joined' else ''

   
    def get_question(self):
        print("stage_id----------------",self.stage_id)
        hr_que_obj = self.env['hr.questions'].search([('active', '!=', False)])
        questions_lines = []
        for hqo in hr_que_obj:
            questions_lines.append((0, 0, {
                'name': hqo.name
            }))
        return {
            'type': 'ir.actions.act_window',
            'name': _('HR Question'),
            'res_model': 'hr.questions.wiz',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_questions_ids': questions_lines},
            'views': [[False, 'form']]
        }

    @api.onchange('kanban_state')
    def on_change_kanban_state(self):
        stage_status = self.env['hr.recruitment.stage'].search([('name', 'ilike', 'Offered')])
        print(".............................................",stage_status,self.stage_id,self.stage_status)
        if self.kanban_state == 'done' and self.stage_status == 'O':
            print("test == ",self.stage_status)
            self.write({'offer':'accepted'})
            
        

    def send_feedback_form(self):
        receipt_list = [self.email_from]
        email_cc = ''
        url = self.get_base_url()
        mail_values = {
            'subject': 'Feedback against your application',
            'body_html':
                """
                <table class="body-wrap" style="width: 100%; border-collapse: collapse; border-spacing: 0;">
                    <tbody>
                        <tr>
                            <td bgcolor="#FFFFFF">
                                <div class="container"
                                     style="display: block!important; max-width: 600px!important; margin: 0 auto!important; clear: both!important;">
                                    <div class="content"
                                         style="padding: 10px; max-width: 600px; margin: 0 auto; display: block;">
                                        <table width="100%">
                                            <tbody>
                                                <tr>
                                                    <td>
                                                        <h3 style="font-weight: 500; font-size: 27px; margin-bottom: 15px;">
                """ 'Dear ' + self.partner_name + """
                                                            </h3>
                                                            <p style="margin-bottom: 10px; font-weight: normal; font-size: 14px; line-height: 1.6;">
                                                                As a process of our recruitment, We would like you to
                                                                share your experience with us through out the hiring
                                                                process.
                                                                You can simply click on the below link to redirect to
                                                                the
                                                                feedback page.
                                                                Thank You!
                                                            </p>
                    """
                + url + '/feedback/' + str(self.id) +
                """
                                                        <p>
                                                            Note: The link will get deactivated after 24 Hrs.
                                                        </p>
                                                        <br/>
                                                        <p>
                                                            <img src="https://aspiresoftware.in/images/odoo_images/logo.png"/>
                                                        </p>
                                                        <p style="margin-bottom: 0px; font-weight: normal; font-size: 14px; line-height: 1.6;">
                                                            <strong>Arti Patel | Sr. HR Executive</strong>
                                                        </p>
                                                        <p style="margin: 0px; font-weight: normal; font-size: 14px; line-height: 1.6;">
                                                            Cell: +91-635-308-6224 | Desk: +91-79-2640-9959
                                                        </p>
                                                        <p style="margin: 0px; font-weight: normal; font-size: 14px; line-height: 1.6;">
                                                            <a style="color: #2ba6cb;"
                                                               href="mailto:hr@aspiresoftware.in" target="_blank"
                                                               rel="noopener">hr@aspiresoftware.in
                                                            </a>
                                                            |
                                                            <a style="color: #2ba6cb;" href="www.aspiresoftware.in"
                                                               target="_blank" rel="noopener">www.aspiresoftware.in
                                                            </a>
                                                        </p>
                                                        <ul style="list-style: none; margin: 5px 0 0; padding: 0;">
                                                            <li style="float: left; margin: 0 5px 0 0; display: inline-block;">
                                                                <a href="https://www.google.com/url?q=https://is.gd/un2WZj&amp;source=gmail&amp;ust=1548822142933000&amp;usg=AFQjCNHp-wjG12BdxvbbNeM0SamdJy5QgA">
                                                                    <img src="https://aspiresoftware.in/images/odoo_images/skype.png"/>
                                                                </a>
                                                            </li>
                                                            <li style="float: left; margin: 0 5px 0 0; display: inline-block;">
                                                                <a href="https://www.google.com/url?q=https://www.facebook.com/aspiresoftware&amp;source=gmail&amp;ust=1548822142933000&amp;usg=AFQjCNGUOcuCXbtDoMuuXkmc8V9sKr35eQ">
                                                                    <img src="https://aspiresoftware.in/images/odoo_images/facebook.png"/>
                                                                </a>
                                                            </li>
                                                            <li style="float: left; margin: 0 5px 0 0;">
                                                                <a href="https://twitter.com/aspiresoftware2">
                                                                    <img src="https://share1.cloudhq-mkt3.net/ef63fac777.png"/>
                                                                </a>
                                                            </li>
                                                            <li style="float: left; margin: 0 5px 0 0; display: inline-block;">
                                                                <a href="https://www.linkedin.com/company/aspire-software-solutions">
                                                                    <img src="https://share1.cloudhq-mkt3.net/09d547ed91.png"/>
                                                                </a>
                                                            </li>
                                                            <li style="float: left; margin: 0 5px 0 0; display: inline-block;">
                                                                <a href="https://www.google.com/url?q=https://plus.google.com/u/0/%2BAspireSoftwareSolutionsAhmedabad/&amp;source=gmail&amp;ust=1548822142933000&amp;usg=AFQjCNEFyUAFSdeFo96qkLGB7aeTFPW04w">
                                                                    <img src="https://aspiresoftware.in/images/odoo_images/twitter.png"/>
                                                                </a>
                                                            </li>
                                                            <li style="float: left; margin: 0 5px 0 0; display: inline-block;">
                                                                <a href="https://www.pinterest.com/aspiresoftware/">
                                                                    <img src="https://aspiresoftware.in/images/odoo_images/pinterest.png"/>
                                                                </a>
                                                            </li>
                                                            <li style="float: left; margin: 0 5px 0 0; display: inline-block;">
                                                                <a href="https://www.instagram.com/aspiresoftware/">
                                                                    <img src="https://aspiresoftware.in/images/odoo_images/instagram.png"/>
                                                                </a>
                                                            </li>
                                                        </ul>
                                                    </td>
                                                </tr>
                                            </tbody>
                                        </table>
                                        <br/>
                                    </div>
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            """,
            'email_to': ';'.join(map(lambda x: x, receipt_list)),
            'email_cc': ';'.join(map(lambda x: x, email_cc)),
            'email_from': self.user_id.login,
        }
        self.env['mail.mail'].create(mail_values).send()

    def level_progress_average_calculation(self, avg):
        na, beg, inter, adv, exp = 0, 25, 50, 75, 100
        if avg < 101 and avg >= 75:
            return exp if (abs(exp - avg)) < (abs(adv - avg)) else adv
        elif avg < 75 and avg >= 50:
            return adv if (abs(adv - avg)) < (abs(inter - avg)) else inter
        elif avg < 50 and avg >= 25:
            return inter if (abs(inter - avg)) < (abs(beg - avg)) else beg
        elif avg < 25 and avg >= 0:
            return beg if (abs(beg - avg)) < (abs(na - avg)) else na
        else:
            pass

    @api.onchange('feedbacks_ids')
    def onchange_feedbacks_ids(self):
        skill_lines = []
        skill_lines_dict = []
        if len(self.feedbacks_ids) == 1:
            for skill in self.feedbacks_ids.feedbacks_skill_ids:
                skill_lines_dict.append({
                    'skill_id': skill.skill_id.id,
                    'skill_level_id': skill.skill_level_id.id,
                    'skill_type_id': skill.skill_type_id.id,
                    'level_progress': skill.level_progress,
                })
            for ski in self.applicant_skill_ids:
                for skill_set in skill_lines_dict:
                    if ski.skill_id.id == skill_set['skill_id']:
                        ski.update({
                            'skill_level_id': skill_set['skill_level_id']
                        })
                        skill_lines_dict.remove(skill_set)
            for skill_data in skill_lines_dict:
                skill_lines.append([0, 0, skill_data])
            self.write({'applicant_skill_ids': skill_lines})
        else:
            list_c = []
            centric_list = []
            for feedback in self.feedbacks_ids:
                for inter in feedback.feedbacks_skill_ids:
                    list_c.append((inter.skill_id.id, inter.skill_level_id.id))
                    skills = {'skill_type_id': inter.skill_type_id.id,
                              'skill_id': inter.skill_id.id,
                              'skill_level_id': inter.skill_level_id.id,
                              'level_progress': inter.level_progress,
                              }
                    centric_list.append(skills)
            groups = {}
            for group, value in list_c:
                if group not in groups:
                    groups.update({group: [value]})
                else:
                    groups[group].append(value)
            lev_progress_list = []
            sum = 0
            for key, value in groups.items():
                if len(value) > 1:
                    total_lev_progress = [self.env['hr.skill.level'].browse(val).level_progress for val in value]
                    for progress in total_lev_progress:
                        sum += progress
                    lev_progress_list.append(int(sum / len(value)))
                    sum = 0
                else:
                    lev_progress_list.append(self.env['hr.skill.level'].browse(value).level_progress)

            avg_lev_progress_list = [self.level_progress_average_calculation(avg) for avg in lev_progress_list]

            data_dict = {}
            for lst_dict in centric_list:
                for key in groups:
                    if lst_dict['skill_id'] == key:
                        data_dict[key] = lst_dict['skill_type_id']

            skill_type_level = [[skilltype_id] for skilltype_id in data_dict.values()]

            count_for_level = 0
            for lev_val in range(len(avg_lev_progress_list)):
                skill_type_level[count_for_level].append(avg_lev_progress_list[lev_val])
                count_for_level += 1

            count_for_key = 0
            for dict_key in groups.keys():
                skill_type_level[count_for_key].append(dict_key)
                count_for_key += 1

            list_skill_level_id = []
            for sk_id_lev in skill_type_level:
                obj_skill_level = self.env['hr.skill.level'].search(
                    [('skill_type_id', '=', sk_id_lev[0]), ('level_progress', '=', sk_id_lev[1])])
                list_skill_level_id.append(obj_skill_level.id)

            count_for_skill_id = 0
            for id_skill_level in list_skill_level_id:
                skill_type_level[count_for_skill_id].append(id_skill_level)
                count_for_skill_id += 1
            result = centric_list

            for key_id in result:
                for val in skill_type_level:
                    if (key_id['skill_type_id'] and key_id['skill_id']) in val:
                        break
                break

            for list_vals in skill_type_level:
                for dict_data in result:
                    if (dict_data['skill_type_id'] == list_vals[0] and dict_data['skill_id'] == list_vals[2]):
                        dict_data['skill_level_id'] = list_vals[3]
                        dict_data['level_progress'] = list_vals[1]

            for ski in self.applicant_skill_ids:
                for skill_set in result:
                    if ski.skill_id.id == skill_set['skill_id']:
                        ski.update({
                            'skill_level_id': skill_set['skill_level_id']
                        })
                        result.remove(skill_set)

            dup_fin_list = [[0, 0, dict_data] for dict_data in result]

            final_result = []
            for data in dup_fin_list:
                if data not in final_result:
                    final_result.append(data)
            self.write({'applicant_skill_ids': final_result})
            remove_dup_skills = [{'skill_id': ski.skill_id.id, 'skill_type_id': ski.skill_type_id.id,
                                  'skill_level_id': ski.skill_level_id.id} for ski in self.applicant_skill_ids]

            main_list = []
            for skill_dict in remove_dup_skills:
                if skill_dict not in main_list:
                    main_list.append(skill_dict)

            result_main_list = [[0, 0, skill_dict_main] for skill_dict_main in main_list]
            self.write({'applicant_skill_ids': False})
            self.write({'applicant_skill_ids': result_main_list})

    @api.onchange('stage_id')
    def onchange_stage_id(self):
        candidate_skills = []
        app_candidate_skills = []
        context = self._context
        current_uid = self.env.context.get('uid') if self.env.context.get('uid') else context.get('uid')
        user = self.env['res.users'].browse(current_uid)
        
        if self.stage_id.name == 'Offered':
            skill_name = [candi_skills.skill_id.name for candi_skills in self.partner_id.candidate_skill_ids]
            if not self.partner_id.candidate_skill_ids:
                for applicant_skill in self.applicant_skill_ids:
                    app_skills_dict = {
                        'skill_type_id': applicant_skill.skill_type_id.id,
                        'skill_id': applicant_skill.skill_id.id,
                        'skill_level_id': applicant_skill.skill_level_id.id
                    }
                    app_candidate_skills.append(app_skills_dict)
                fin_app_skills_list = [[0, 0, data] for data in app_candidate_skills]
                self.partner_id.write({'candidate_skill_ids': fin_app_skills_list})
            else:
                for cskils in self.partner_id.candidate_skill_ids:
                    for app_skill in self.applicant_skill_ids:
                        if ((cskils.skill_id.id == app_skill.skill_id.id) and (
                                cskils.skill_type_id.id == app_skill.skill_type_id.id)):
                            skill_level_id_var = app_skill.skill_level_id.id
                            cskils.update({
                                'skill_level_id': skill_level_id_var
                            })
                        else:
                            if app_skill.skill_id.name not in skill_name:
                                skills_dict = {
                                    'skill_type_id': app_skill.skill_type_id.id,
                                    'skill_id': app_skill.skill_id.id,
                                    'skill_level_id': app_skill.skill_level_id.id
                                }
                                candidate_skills.append(skills_dict)
                list_candidate = []
                for candidate in candidate_skills:
                    if candidate not in list_candidate:
                        list_candidate.append(candidate)
                fin_candidate_list = [[0, 0, data] for data in list_candidate]
                self.partner_id.write({'candidate_skill_ids': fin_candidate_list})
                self.candidate.write({'candidate_skill_ids': fin_candidate_list})
        
        if self.stage_id.name in ("Shortlisted","Screened","Offered","Joined"):
            activity_status = self.env['mail.activity.type'].search([('name', '=',self.stage_id.name),('res_model','ilike','hr.applicant')])
            applicant_id = self .env['hr.applicant'].search([('id','=',self._origin.id)])
            _logger.info('Current User == %s %s',user.name,activity_status.name)
            try:
                applicant_id.write({
                    'applicant_activity_ids':[(0,0,{
                        'activity':activity_status.id,
                        'track_date':datetime.now(),
                        'user_id':user.id,
                        'job_opening':self.job_opening_id.id
                    })],
                })

                if self.stage_id.name == 'Shortlisted':
                    self.shortlisted_date = datetime.now()
                elif self.stage_id.name == "Screened":
                    self.screen_date = datetime.now()
                elif self.stage_id.name == "Offered":
                    self.offered_date = datetime.now()
                else:
                    self.joined_date = datetime.now()

            except Exception as e:
                _logger.error('Reason of Application Activity Failed %s',e)        
    
    '''
    @api.model
    def update_candidate_skill(self):
        for rec in self:
            candidate_skills = []
            for skills in rec.applicant_skill_ids:
                rec.partner_id.write({'candidate_skill_ids': False})
                skills_dict = {'skill_type_id': skills.skill_type_id.id,
                               'skill_id': skills.skill_id.id,
                               'skill_level_id': skills.skill_level_id.id,
                               'level_progress': skills.level_progress,
                               }
                candidate_skills.append([0, 0, skills_dict])

            rec.partner_id.write({'candidate_skill_ids': candidate_skills})
    '''

    def offer_accepted_applicant(self):
        for self in self:
            self.write({
                'kanban_state':'done',
                'offer':'accepted'
            })

class HrApplicantSkill(models.Model):
    _name = 'hr.applicant.skill'
    _description = "Skill level for Applicant"
    _rec_name = 'skill_id'
    _order = "skill_level_id"

    applicant_id = fields.Many2one('hr.applicant', required=True, ondelete='cascade')
    skill_id = fields.Many2one('hr.skill', required=True)
    skill_level_id = fields.Many2one('hr.skill.level', required=True)
    skill_type_id = fields.Many2one('hr.skill.type', required=True)
    level_progress = fields.Integer(related='skill_level_id.level_progress')

    _sql_constraints = [
        ('_unique_skill', 'unique (applicant_id, skill_id)', "Two levels for the same skill is not allowed"),
    ]

    @api.constrains('skill_id', 'skill_type_id')
    def _check_skill_type(self):
        for record in self:
            if record.skill_id not in record.skill_type_id.skill_ids:
                raise ValidationError(
                    _("The skill %(name)s and skill type %(type)s doesn't match", name=record.skill_id.name,
                      type=record.skill_type_id.name))

    @api.constrains('skill_type_id', 'skill_level_id')
    def _check_skill_level(self):
        for record in self:
            if record.skill_level_id not in record.skill_type_id.skill_level_ids:
                raise ValidationError(_("The skill level %(level)s is not valid for skill type: %(type)s",
                                        level=record.skill_level_id.name, type=record.skill_type_id.name))


class HrCandidateSkill(models.Model):
    _name = 'hr.candidate.skill'
    _description = "Skill level for Candidate"
    _rec_name = 'skill_id'
    _order = "skill_level_id"

    candidate_id = fields.Many2one('candidate', required=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', ondelete='cascade')
    skill_id = fields.Many2one('hr.skill', required=True)
    skill_level_id = fields.Many2one('hr.skill.level', required=True)
    skill_type_id = fields.Many2one('hr.skill.type', required=True)
    level_progress = fields.Integer(related='skill_level_id.level_progress')

    _sql_constraints = [
        ('_unique_skill', 'unique (partner_id, skill_id)', "Two levels for the same skill is not allowed"),
    ]

    @api.constrains('skill_id', 'skill_type_id')
    def _check_skill_type(self):
        for record in self:
            if record.skill_id not in record.skill_type_id.skill_ids:
                raise ValidationError(
                    _("The skill %(name)s and skill type %(type)s doesn't match", name=record.skill_id.name,
                      type=record.skill_type_id.name))

    @api.constrains('skill_type_id', 'skill_level_id')
    def _check_skill_level(self):
        for record in self:
            if record.skill_level_id not in record.skill_type_id.skill_level_ids:
                raise ValidationError(_("The skill level %(level)s is not valid for skill type: %(type)s",
                                        level=record.skill_level_id.name, type=record.skill_type_id.name))


class AppQuestionsLine(models.Model):
    _name = 'app.questions.line'
    _description = 'Application HR Questions Lines'

    applicant_id = fields.Many2one('hr.applicant', string="Applicant")
    name = fields.Char('Question')
    ans = fields.Char('Answer')


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    @api.model
    def _default_time(self):
        notification_obj = self.env['calendar.alarm'].search([('duration', '=', 15), ('interval', '=', 'minutes')])
        if notification_obj:
            return notification_obj.ids

    meeting_location = fields.Selection(ADDRESS, 'Meeting Location', tracking=True, help="Location of Event")
    alarm_ids = fields.Many2many(
        'calendar.alarm', 'calendar_alarm_calendar_event_rel',
        string='Reminders', ondelete="restrict",  default=_default_time,
        help="Notifications sent to all attendees to remind of the meeting.")

    additional_activity = fields.Many2one('mail.activity.type','Additional Activity')

    def _get_attendee_emails(self):
        """ Get comma-separated attendee email addresses. """

        self.ensure_one()
        return ",".join([e for e in self.attendee_ids.mapped("email") if e])


class ResCompany(models.Model):
    _inherit = 'res.company'

    logo_url = fields.Char("Logo URL")

    _sql_constraints = [
        ('social_linkedin_uniq', 'unique (social_linkedin)', 'Company already exist with same linkedin profile!')
    ]


class Candidate(models.Model):
    _name = 'candidate'
    _description = "Aspire Candidate"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "write_date desc"

    @api.depends('total_exp_years')
    def _compute_current_experience(self):
        print("\ncandidate\n", self.total_exp_years)
        if self.total_exp_years:
            year = 0
            month = 0
            if self.res_partner_id:
                old_create_date = datetime.strftime(self.partner_create_date, '%Y:%m:%d')
                old_experience_in_day = int((datetime.now().date() - datetime.strptime(old_create_date, '%Y:%m:%d').date()).days)
                year += old_experience_in_day // 365
                month += (old_experience_in_day % 365) // 30
            else:
                candidate_create_date = datetime.strftime(datetime.now(), '%Y:%m:%d')
                can_experience_in_day = int(
                    (datetime.now().date() - datetime.strptime(candidate_create_date, '%Y:%m:%d').date()).days)
                year += can_experience_in_day // 365
                month += (can_experience_in_day % 365) // 30
            exp = ""
            years = 0
            months = 0
            experience = ""
            if self.total_exp_years > 1:
                experience += get_experience(int(self.total_exp_years))
                calculate = calculate_years_months(self.total_exp_years, year, month)
                years += calculate[0]
                months += calculate[-1]
            else:
                experience += get_experience(int(self.total_exp_years))
                calculate = calculate_years_months(self.total_exp_years, year, month)
                years += calculate[0]
                months += calculate[-1]
            if year >= 0:
                exp = exp + str(years) + " year "
            if month >= 0:
                exp = exp + str(months) + " months "
            self.current_experience = exp
            self.total_exp = experience
        else:
            self.total_exp = 0
            self.current_experience = 0

    name = fields.Char(index=True)
    notice_period = fields.Integer(string="Notice Period")
    mobile = fields.Char()
    email = fields.Char()
    type_id = fields.Many2one('hr.recruitment.degree', "Degree")
    job_id = fields.Many2one('hr.job', "Applied Job", tracking=True)
    current_company_id = fields.Many2one('current.company', "Current Company")
    current_location_city = fields.Many2one('current.location.city', 'Current City')
    date_received = fields.Date(string='Date Received')
    stage = fields.Char(string='Stage')
    categ_ids = fields.Many2many('hr.applicant.category', string="Skills")
    salary_current = fields.Integer("Current Salary", group_operator="avg",
                                    help="Current Salary of Applicant", tracking=True)     # tracking=True
    salary_expected = fields.Integer("Expected Salary", group_operator="avg",
                                     help="Salary Expected by Applicant", tracking=True)    # tracking=True
    partner_id = fields.Many2one('res.partner', 'Referred By', ondelete='set null',
                                 tracking=True)  # domain=[('is_employee', '=', True)]
    is_applicant = fields.Boolean(string="Is Applicant", tracking=True)
    is_candidate = fields.Boolean(string="Is Candidate", tracking=True)
    is_employee = fields.Boolean(string="Is Employee", tracking=True)
    in_application = fields.Boolean(string="In Application")
    active_employee = fields.Boolean("Active Employee", readonly=True)
    total_exp_years = fields.Integer(string="Experience in Months", store=True)
    total_exp = fields.Char(string="Total Experience", store=True)
    current_experience = fields.Char(string="Current Experience", compute="_compute_current_experience")
    linked_in_profile = fields.Char('LinkedIn Profile')
    year_of_passing = fields.Integer('Year of Passing')
    job_opening_id = fields.Many2one('job.opening', "Job Opening")
    job_opening_ids = fields.Many2many('job.opening', string="Job Openings")
    v9_an_id = fields.Integer(string='V9 Application ID')
    source_id = fields.Many2one('utm.source', 'Source',
                                help="This is the source of the link")
    user_id = fields.Many2one(
        'res.users', "Sales Person",
        store=True,
        readonly=True)
    sourced_by = fields.Many2one('res.users', default=lambda self: self.env.user.id)
    # candidate_skill_ids = fields.One2many('hr.candidate.skill', 'partner_id', string="Skills")
    candidate_skill_ids = fields.One2many('hr.candidate.skill', 'candidate_id', string="Skills")
    # Added for manage multi application to single contact
    all_aspire_application_count = fields.Integer(compute='_compute_all_aspire_application_count',
                                           string="All Application Count")
    private_note = fields.Text("Private Note")
    description = fields.Text('Application Summary')
    app_status = fields.Boolean(compute='_compute_app_status',string='Status')
    # app_refused = fields.Boolean(string = "Application Refused",default=True)
    application_refused = fields.Boolean(compute='_compute_application_refused',search="_compute_application_refuse_search",string='Refused Data')
    active = fields.Boolean(default=True)
    candidate_id = fields.Many2one('candidate', "Candidate")
    res_partner_id = fields.Integer('Partner Candidate')
    partner_create_date = fields.Date('Partner Create Date')
    ref = fields.Char(string='Reference', index=True)

    @api.constrains('mobile', 'email')
    def check_candidate_mobile_email(self):
        for obj in self:
            if obj.mobile and obj.email:
                exist = self.search([('mobile', '=', obj.mobile), ('email', '=', obj.email), ('id', '!=', obj.id)])
                if exist:
                    raise exceptions.ValidationError(_('Candidate already exist with same mobile and email.'))

    # Update partner as active employee
    @api.model
    def _active_employee(self):
        # First deactivate all partner
        active_emp_partner_obj = self.partner_id.search([('active_employee', '=', True)])
        for de_active_partner in active_emp_partner_obj:
            de_active_partner.write({'active_employee': False})
        active_emp_ids = self.env['hr.employee'].search([('with_organization', '=', True)]).ids
        active_users = self.user_id.search([('employee_id', 'in', active_emp_ids)])
        for active in active_users:
            active.partner_id.write({
                'active_employee': True,
                'is_employee': True,
                'is_applicant': False,
                'is_candidate': False,
            })

    def _compute_app_status(self):
        for rec in self:
            rec.app_status = False
            application_obj = self.env['hr.applicant'].search(
                [('candidate_id', '=', rec.id)])
            for app in application_obj:
                if app.active:
                    rec.app_status = True

    def _compute_application_refused(self):
        job_opening = self.env.context.get('active_id')
        for rec in self:
            rec.application_refused = False
            application_obj = self.env['hr.applicant'].search(
                [('candidate_id', '=', rec.id),('job_opening_id','=',job_opening),('active','=',False)])
            if application_obj:
                rec.application_refused = True

    def _compute_application_refuse_search(self, operator,value):
        job_opening = self.env.context.get('active_id')
        candidate = self.env['candidate'].search([])
        current_job_opening = self.env['job.opening'].search([('id','=',job_opening)])
        refused_candidate = []
        refused_candidate_false = []
        for rec in candidate:
            application_obj = self.env['hr.applicant'].search(
                [('candidate_id', '=', rec.id),('job_opening_id','=',job_opening),('active','=',False)])
            if application_obj:
                opening_criteria_days = int(current_job_opening.re_eligable_criteria) * 30
                current_date = datetime.now().date()

                if application_obj.refused_date:
                    diff_date = current_date - application_obj.refused_date
                else:
                    diff_date = current_date - (application_obj.write_date).date()  
                
                if diff_date > timedelta(opening_criteria_days):
                    refused_candidate_false.append(rec.id)
                
                else:
                    refused_candidate.append(rec.id)
            else:
                refused_candidate_false.append(rec.id)                
        org_refused_candidate = tuple(refused_candidate)
        org_refused_candidate_false = tuple(refused_candidate_false)
        if value:
            return [('id', 'in',org_refused_candidate)]
        else:
            return [('id', 'in',org_refused_candidate_false)]


    def _compute_all_aspire_application_count(self):
        for applicant in self:
            application_obj = self.env['hr.applicant'].search(
                [('candidate_id', '=', applicant.id), ('active', 'in', [True, False])])
            for job in self:
                job.all_aspire_application_count = len(application_obj)

    @api.model
    def aspire_create_application(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _("Move To Application"),
            'res_model': 'aspire.transfer.to.application',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_ids': self.env.context.get('active_ids')},
        }

    # Method added for create candidates based on the incoming eaction_schedule_interviewmail server.
    @api.model
    def message_new(self, msg, custom_values=None):
        """ Overrides mail_thread message_new that is called by the mail gateway
            through message_process.
            This override updates the document according to the email.
        """
        # val = msg.get('from').split("<")[0]
        val = msg.get('from').split("<")[0].split('"')[1]
        if '<' in msg.get('from'):
            email = (msg.get('from').split("<"))[1].split(">")[0]
        else:
            email = msg.get('from')

        defaults = {
            'name': val,
            'email': email,
            'date_received': fields.Date.context_today(self),
            'source_id': self.env['utm.source'].search([('name', '=', 'Email')], limit=1).id,
        }
        res_partner_obj = self.env['candidate'].search([('email', '=', msg.get('from'))])
        if res_partner_obj:
            self.env['candidate'].search([('email', '=', msg.get('from'))]).unlink()
        try:
            i = 0
            message_body = (msg.get('body'))
            soup = BeautifulSoup(message_body, "lxml")
            soup.unicode
            message_table = soup.find("table", border=1)
            message_body = soup.find('tbody')
            message_row = soup.find_all('tr')
            dist = {}
            for td in message_row:
                key = soup.find_all("td")[i].get_text()
                i = i + 2
                value = soup.find_all("td")[i].get_text()
                i = i + 1
                dist[str(key.strip('\n'))] = str(value.strip('\n'))
            if msg.get('priority'):
                defaults['priority'] = msg.get('priority')
            if custom_values:
                defaults.update(custom_values)

            if 'Full Name' in dist:
                defaults['name'] = dist['Full Name']
            if 'Email' in dist:
                defaults['email'] = dist['Email']
            if 'Contact Number' in dist:
                defaults['mobile'] = dist['Contact Number']
            if 'Current Location' in dist:
                location = dist['Current Location']
                existing_location_city = self.env['current.location.city']
                existing_location_city_id = existing_location_city.search([('location_name', '=', location.lower())],
                                                                          limit=1)
                if existing_location_city:
                    defaults['current_location_city'] = existing_location_city_id.id
                else:
                    location_city = existing_location_city.create({'location_name': location})
                    defaults['current_location_city'] = location_city.id

        except Exception as e:
            print(e)

        existing_email = self.env['candidate'].search([('email', '=', email)])
        # custom model of OLD env

        multiple_candidates_emails = self.env['multiple.candidates.emails'].search([])
        allowed_emails = []

        if len(multiple_candidates_emails) > 0:
            for eml in multiple_candidates_emails:
                allowed_emails.append(eml.name)

        is_available = False
        if (len(existing_email) > 0 and email == existing_email[0].email) and (email not in allowed_emails):
            is_available = True

        blocked_emails = self.env['blocked.emails'].search([('name', '=', email)])
        if len(blocked_emails) > 0 and email == blocked_emails.name:
            pass
        elif is_available:
            return existing_email[0].write(defaults)
        else:
            result = super(Candidate, self).message_new(msg, custom_values=defaults)
            result.write(defaults)
            return result


class MailActivityInherit(models.Model):
    _inherit = 'mail.activity'

    def action_refuse(self):
        self.unlink()
        return True

    @api.model
    def create(self,vals):
        _logger.info('vals_data %s',vals)

        if 'calendar_event_id' in vals:
            calender_data = self.env['calendar.event'].search([('id','=',vals['calendar_event_id'])])
            _logger.info('Calender Data %s',calender_data)
            if calender_data.additional_activity:
                vals['activity_type_id'] = calender_data.additional_activity.id
        return super(MailActivityInherit, self).create(vals)


    def write(self,vals):
        if self.res_model_id.name == 'Applicant':
            applicant = self.env['hr.applicant'].search([('id', '=',self.res_id)])
            context = self._context
            _logger.info('Uid1: %s     - Uid2: %s',self.env.context.get('uid') , self._context.get('uid'))
            current_uid = self.env.context.get('uid') if self.env.context.get('uid') else self._uid

            user = self.env['res.users'].browse(current_uid)

            _logger.info('Current User == %s %s',user.name,self.activity_type_id.name)

            _logger.info('Calender Data %s',applicant)

            if 'active' in vals and vals['active'] == False:
                applicant.write({
                    'applicant_activity_ids':[(0,0,{
                        'activity':self.activity_type_id.id,
                        'track_date':datetime.now(),
                        'user_id':user.id,
                        'job_opening':applicant.job_opening_id.id
                    })]
                })
                
        return super(MailActivityInherit, self).write(vals)
