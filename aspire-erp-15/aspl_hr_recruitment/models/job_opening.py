# -*- coding: utf-8 -*-
from datetime import datetime,timedelta
from odoo import models, fields, api, _
import ast
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta
from odoo.http import request


# def date_diff_in_seconds(dt2, dt1):
#     diff = relativedelta(dt2, dt1)
#     temp = "{}:{}:{} {}:{}:{}".format(diff.years, diff.months, diff.days, diff.hours, diff.minutes, diff.seconds)
#     res = ['0'+i if len(i) == 1 else i for i in temp.split()[0].split(':') + temp.split()[-1].split(':')]
#     return "{}:{}:{} {}:{}:{}".format(res[0], res[1], res[2], res[3], res[4], res[5])


class JobOpening(models.Model):
    _name = 'job.opening'
    _description = 'Job Opening'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin', 'utm.mixin']
    _order = "state desc, name asc"

    # method inherited from hr recruitment

    @api.model
    def _default_address_id(self):
        return self.env.company.partner_id

    def _get_default_favorite_user_ids(self):
        return [(6, 0, [self.env.uid])]

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

    def _domain_get_owner(self):
        hr_owners = self.env.ref('aspl_hr_recruitment.group_recruiter_owner').users.ids
        if hr_owners:
            return [('id', 'in', hr_owners)]

    name = fields.Char(string='Job Opening', required=True, index=True, translate=True)
    active = fields.Boolean("Active", default=True,
                            help="If the active field is set to false, it will allow you to hide the case without removing it.")
    expected_employees = fields.Integer(compute='_compute_employees', string='Total Forecasted Employees', store=True,
                                        help='Expected number of employees for this job position after new recruitment.')
    expected_end_date = fields.Date("Expected End Date", tracking=True)
    end_date = fields.Date("End Date")
    no_of_employee = fields.Integer(compute='_compute_employees', string="Current Number of Employees", store=True,
                                    help='Number of employees currently occupying this job position.')
    no_of_recruitment = fields.Integer(string='Expected New Employees', copy=False,
                                       help='Number of new employees you expect to recruit.', default=1, tracking=True)
    no_of_hired_employee = fields.Integer(compute='_compute_hired_emp', string='Hired Employees',
                                          help='Number of hired employees for this job position during recruitment phase.')
    hired_employee = fields.Integer('Employee Hired')
    employee_ids = fields.One2many('hr.employee', 'job_id', string='Employees', groups='base.group_user')
    description = fields.Html(string='Responsibilities', tracking=True)
    image = fields.Binary("Image", help="Select image here")
    essential_requirements= fields.Html(string='Requirements', tracking=True)
    # desired_skills= fields.Html(string='Desired Skills')
    requirements = fields.Text('Requirements')
    department_id = fields.Many2one('hr.department', string='Department',
                                    domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    state = fields.Selection([
        ('recruit', 'In Progress'),
        ('open', 'Done')
    ], string='Status', readonly=True, required=True, tracking=True, copy=False, default='recruit',
        help="Set whether the recruitment process is open or closed for this job position.")
    applicant_feedback = fields.Float("Feedback Average")
    # HR Recruitment fields
    address_id = fields.Many2one(
        'res.partner', "Job Location", default=_default_address_id,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="Address where employees are working")
    application_ids = fields.One2many('hr.applicant', 'job_id', "Applications")
    application_count = fields.Integer(compute='_compute_application_count', string="Application Count")
    all_application_count = fields.Integer(compute='_compute_all_application_count',
                                           string="All Application Count")
    all_aspire_application_count = fields.Integer(compute='_compute_all_aspire_application_count',
                                                  string="All Application Count")
    new_application_count = fields.Integer(
        compute='_compute_new_application_count', string="New Application",
        help="Number of applications that are new in the flow (typically at first step of the flow)")
    manager_id = fields.Many2one(
        'hr.employee', related='department_id.manager_id', string="Department Manager",
        readonly=True, store=True)
    user_id = fields.Many2one('res.users', "Recruiter",
                              tracking=True,
                              domain=_domain_get_recruiters, default=lambda self: self.env.user)
    owner_id = fields.Many2one('res.users', "Owner", tracking=True, domain=_domain_get_owner)
    hr_responsible_id = fields.Many2one(
        'res.users', "HR Responsible", tracking=True,
        help="Person responsible of validating the employee's contracts.")
    alias_id = fields.Many2one(
        'mail.alias', "Alias", ondelete="restrict", required=True,
        help="Email alias for this job position. New emails will automatically create new applicants for this job position.")
    color = fields.Integer("Color Index")
    is_favorite = fields.Boolean(compute='_compute_is_favorite', inverse='_inverse_is_favorite')
    favorite_user_ids = fields.Many2many('res.users', 'job_opening_favorite_user_rel', 'job_opening_id', 'user_id',
                                         default=_get_default_favorite_user_ids)

    # Custom fields Start
    job_id = fields.Many2one('hr.job', string='Job Position')
    candidate_ids = fields.One2many('res.partner', 'job_opening_id', "Candidates")
    candidate_count = fields.Integer(compute='_compute_candidate_count', string="Candidate Count")
    all_candidate_count = fields.Integer(compute='_compute_all_candidate_count', string="All Candidate Count")  #
    all_aspire_candidate_count = fields.Integer(compute='_compute_aspire_all_candidate_count', string="Aspire Candidate Count")  #
    categ_req_ids = fields.Many2many('hr.applicant.category', 'job_opening_categ_req_user_rel', 'job_opening_id',
                                     'user_id', string="Tags")  # Required

    categ_opt_ids = fields.Many2many('hr.applicant.category', 'job_opening_categ_opt_user_rel', 'job_opening_id',
                                     'user_id', string="Nice to have")
    type_ids = fields.Many2many('hr.recruitment.degree', 'job_opening_type_degree_rel', 'job_opening_id',
                                'degree_id', "Degree")
    minimum_exp = fields.Integer(string="Minimum Experience Required", tracking=True)
    maximum_exp = fields.Integer(string="Maximum Experience Required", tracking=True)
    experience_display_name = fields.Char(string="Experience Display Name")
    opening_skill_ids = fields.One2many('job.opening.skill', 'job_opening_id', string="Skills")
    opened_date =fields.Date(string="Opened Date",default=datetime.today())
    # expected_closing_date =fields.Date(string="Expected Closing Date",default=datetime.today())
    # Reporting fields
    wfh = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string='WFH Available', default='no')
    # exp_range = fields.Char('Exp Range')
    priority = fields.Selection([
        ('0', 'Null'),
        ('1', 'Low'),
        ('2', 'Medium'),
        ('3', 'High'),
    ],required=True, tracking=True)
    re_eligable_criteria = fields.Selection([
        ('0','0'),
        ('3','3'),
        ('6','6'),
    ],default='6',string="Re-Eligible Criteria", tracking=True)
    req_no = fields.Char('Request No', copy=False, readonly=True, default=lambda x: _('New'))
    aspire = fields.Boolean("Aspire", help="Switch between Res Partner and Candidate", default=False)
    kick_off_id = fields.Many2one('opening.kickoff',"Kickoff Opening")
    salary_range = fields.Char(string="Salary Range")
    # End

    def _compute_hired_emp(self):
        self.no_of_hired_employee = len(self.application_ids.search([
            ('offer', 'in', ['joined','accepted']), ('job_opening_id', '=', self.id)
        ]))
        self.hired_employee = self.no_of_hired_employee

    @api.depends('no_of_recruitment', 'employee_ids.job_id', 'employee_ids.active')
    def _compute_employees(self):
        employee_data = self.env['hr.employee'].read_group([('job_id', 'in', self.ids)], ['job_id'], ['job_id'])
        result = dict((data['job_id'][0], data['job_id_count']) for data in employee_data)
        for job in self:
            job.no_of_employee = result.get(job.id, 0)
            job.expected_employees = result.get(job.id, 0) + job.no_of_recruitment

    @api.model
    def create(self, values):
        """ We don't want the current user to be follower of all created job """
        job_opening = super(JobOpening, self.with_context(mail_create_nosubscribe=True)).create(values)
        if job_opening.req_no == 'New':
            number = self.env['ir.sequence'].get('job.opening') or '/'
            company = job_opening.company_id.name
            prefix_list = company.split()
            seq = ""
            for initial in prefix_list:
                seq += initial[0]
            seq_number = seq + str(number)
            job_opening.write({'req_no': seq_number})
        
        if job_opening.kick_off_id:
            job_opening.kick_off_id.write({'job_opening_id':job_opening.id})
            job_opening.kick_off_id.write({'available_opening':True})

        return job_opening

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {})
        if 'name' not in default:
            default['name'] = _("%s (copy)") % (self.name)
        return super(JobOpening, self).copy(default=default)

    def set_recruit(self):
        for record in self:
            no_of_recruitment = 1 if record.no_of_recruitment == 0 else record.no_of_recruitment
            record.write({
                'state': 'recruit',
                'no_of_recruitment': no_of_recruitment,
                'end_date' : False
                })
        return True

    ##

    def get_candidate(self):
        res_partner_job_opening = self.env['res.partner'].search([('job_opening_ids', 'in', self.id)])
        for rec in res_partner_job_opening:
            rec.update({'job_opening_ids': [(3, self.id)]})
        domain = [('categ_ids', '!=', False)]
        candidate_obj = self.env['res.partner'].search(
            domain)
        if candidate_obj:
            for rec in candidate_obj:
                if self.categ_req_ids:
                    if self.id in rec.job_opening_ids.ids:
                        rec.update({'job_opening_ids': [(3, self.id)]})
                    if all([l in rec.categ_ids.ids for l in self.categ_req_ids.ids]):
                        rec.update({'job_opening_ids': [(4, self.id)]})
                else:
                    if self.id in rec.job_opening_ids.ids:
                        rec.update({'job_opening_ids': [(3, self.id)]})

    def move_to_application(self):
        res_partner_obj = self.env['res.partner'].search([('job_opening_ids', 'in', self.id)])
        hr_application = self.env['hr.applicant']
        skill_lines = []
        applicant_activity_list = []
        for skill in self.opening_skill_ids:
            skill_lines.append([0, 0, {
                'skill_id': skill.skill_id.id,
                'skill_level_id': skill.skill_level_id.id,
                'skill_type_id': skill.skill_type_id.id,
                'level_progress': skill.level_progress,
            }])
        for rec in res_partner_obj:
            if hr_application.search([('active', 'in', [True, False])]).filtered(lambda p: p.partner_id.id == rec.id):
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
                    'categ_ids': rec.categ_ids.ids,
                    'interviewers_ids': self.user_id.ids,
                    'reviewer_user_ids': self.user_id.ids,
                    'job_id': self.job_id.id,
                    'department_id': self.department_id.id,
                    'source_id': rec.source_id.id,
                    'stage_id': self.env.ref('aspl_hr_recruitment.initial').id,
                    'user_id': self.user_id.id,
                    'job_opening_id': self.id,
                    'private_note': rec.private_note,
                    'date_received': rec.date_received,
                    'total_exp_years': rec.total_exp_years,
                    'is_partner': True,
                    # 'message_main_attachment_id': rec.message_main_attachment_id.id,
                    # 'job_opening_ids': [(4, self.id)]
                })
                applicant.update({'applicant_skill_ids': skill_lines})
                rec.in_application = True
                rec.is_applicant = True
                rec.is_candidate = True
                rec.is_employee = False
                rec.active_employee = False
                current_uid = request.env.context.get('uid')
                user = self.env['res.users'].browse(current_uid)
                activity_status = self.env['mail.activity.type'].search([('name', '=',applicant.stage_id.name),('res_model','ilike','hr.applicant')])
                applicant.write({
                    'applicant_activity_ids':[(0,0,{
                        'activity':activity_status.id,
                        'track_date':datetime.now(),
                        'user_id':user.id,
                        'job_opening':applicant.job_opening_id.id
                    })]
                })

        for candidate in res_partner_obj:
            candidate.write({'user_id': self.user_id.id})

    def set_open(self):
        res_partner_obj = self.env['res.partner'].search([('job_opening_ids', 'in', self.id)])
        hr_applicant_obj = self.env['hr.applicant'].search([('job_opening_id', '=', self.id)])
        for rec in res_partner_obj:
            rec.update({'job_opening_ids': [(3, self.id)]})
        for app in hr_applicant_obj:
            if app.stage_id.name != 'Joined':
                app.update(
                    {'refuse_reason_id': self.env.ref('aspl_hr_recruitment.opening_stopped').id, 'active': False})
        return self.write({
            'state': 'open',
            'end_date' : datetime.now(),
            # 'no_of_recruitment': 0,
            # 'no_of_hired_employee': 0
        })

    def _compute_is_favorite(self):
        for job in self:
            job.is_favorite = self.env.user in job.favorite_user_ids

    def _inverse_is_favorite(self):
        unfavorited_jobs = favorited_jobs = self.env['hr.job']
        for job in self:
            if self.env.user in job.favorite_user_ids:
                unfavorited_jobs |= job
            else:
                favorited_jobs |= job
        favorited_jobs.write({'favorite_user_ids': [(4, self.env.uid)]})
        unfavorited_jobs.write({'favorite_user_ids': [(3, self.env.uid)]})

    def _compute_document_ids(self):
        applicants = self.mapped('application_ids').filtered(lambda self: not self.emp_id)
        app_to_job = dict((applicant.id, applicant.job_id.id) for applicant in applicants)
        attachments = self.env['ir.attachment'].search([
            '|',
            '&', ('res_model', '=', 'hr.job'), ('res_id', 'in', self.ids),
            '&', ('res_model', '=', 'hr.applicant'), ('res_id', 'in', applicants.ids)])
        result = dict.fromkeys(self.ids, self.env['ir.attachment'])
        for attachment in attachments:
            if attachment.res_model == 'hr.applicant':
                result[app_to_job[attachment.res_id]] |= attachment
            else:
                result[attachment.res_id] |= attachment

        for job in self:
            job.document_ids = result.get(job.id, False)
            job.documents_count = len(job.document_ids)

    def _compute_all_application_count(self):
        print("\n_compute_all_application_count\n")
        applicant_list = []
        res_partner_obj = self.env['hr.applicant'].search(
            [('job_opening_id', '=', self.id), ('active', 'in', [False, True])])
        # , ('is_partner', '=', True)
        print("\nApplicant Obj", res_partner_obj, len(res_partner_obj), "\n")
        for applicant in res_partner_obj:
            applicant_list.append({
                applicant.id: applicant.name
                })
        print(applicant_list, "\n")
        for job in self:
            job.all_application_count = len(res_partner_obj)

        # res_partner = self.env['res.partner'].search([]).ids
        # res_partner_obj = self.env['hr.applicant'].search(
        #     [('job_opening_id', '=', self.id), ('active', 'in', [True]),
        #      ('partner_id', 'in', res_partner)])  # [False, True]
        # for job in self:
        #     job.all_application_count = len(res_partner_obj)

    def _compute_all_aspire_application_count(self):
        candidate = self.env['candidate'].search([]).ids
        res_partner_obj = self.env['hr.applicant'].search(
            [('job_opening_id', '=', self.id), ('active', 'in', [False, True])])   # [False, True]
        # ('candidate_id', 'in', candidate)
        for job in self:
            job.all_aspire_application_count = len(res_partner_obj)

    def _compute_application_count(self):
        pass

    def _compute_candidate_count(self):
        pass

    def _compute_all_candidate_count(self):
        res_partner_obj = self.env['res.partner'].search([('job_opening_ids', 'in', self.id)])
        for job in self:
            job.all_candidate_count = len(res_partner_obj)

    def _compute_aspire_all_candidate_count(self):
        res_partner_obj = self.env['candidate'].search([('job_opening_ids', 'in', self.id)])
        count = 0
        for rec in res_partner_obj:
            application_data = self.env['hr.applicant'].search([('candidate_id', '=', rec.id),('job_opening_id','=',self.id),('active','=',False)],limit=1, order='refused_date desc')
            if application_data:
                opening_criteria_days = int(self.re_eligable_criteria) * 30
                current_date = datetime.now().date()
                if application_data.refused_date:
                    diff_date = current_date - application_data.refused_date
                else:
                    diff_date = current_date - (application_data.write_date).date() 
                if diff_date > timedelta(opening_criteria_days):
                    count += 1
            else:
                count += 1  
        self.all_aspire_candidate_count = count     

    # def _compute_aspire_all_candidate_count(self):
    #     res_partner_obj = self.env['candidate'].search([('job_opening_ids', 'in', self.id)])
    #     for job in self:
    #         job.all_aspire_candidate_count = len(res_partner_obj)

    def _get_first_stage(self):
        self.ensure_one()
        return self.env['hr.recruitment.stage'].search([
            '|',
            ('job_ids', '=', False),
            ('job_ids', '=', self.id)], order='sequence asc', limit=1)

    def _compute_new_application_count(self):
        pass

    def _alias_get_creation_values(self):
        values = super(JobOpening, self)._alias_get_creation_values()
        values['alias_model_id'] = self.env['ir.model']._get('hr.applicant').id
        if self.id:
            values['alias_defaults'] = defaults = ast.literal_eval(self.alias_defaults or "{}")
            defaults.update({
                'job_id': self.id,
                'department_id': self.department_id.id,
                'company_id': self.department_id.company_id.id if self.department_id else self.company_id.id,
            })
        return values

    def _creation_subtype(self):
        return self.env.ref('hr_recruitment.mt_job_new')

    def action_get_attachment_tree_view(self):
        action = self.env["ir.actions.actions"]._for_xml_id("base.action_attachment")
        action['context'] = {
            'default_res_model': self._name,
            'default_res_id': self.ids[0]
        }
        action['search_view_id'] = (self.env.ref('hr_recruitment.ir_attachment_view_search_inherit_hr_recruitment').id,)
        action['domain'] = ['|', '&', ('res_model', '=', 'hr.job'), ('res_id', 'in', self.ids), '&',
                            ('res_model', '=', 'hr.applicant'), ('res_id', 'in', self.mapped('application_ids').ids)]
        return action

    def close_dialog(self):
        return {'type': 'ir.actions.act_window_close'}

    def edit_dialog(self):
        form_view = self.env.ref('hr.view_hr_job_form')
        return {
            'name': _('Job'),
            'res_model': 'hr.job',
            'res_id': self.id,
            'views': [(form_view.id, 'form'), ],
            'type': 'ir.actions.act_window',
            'target': 'inline'
        }

    def get_aspire_candidate(self):
        res_partner_job_opening = self.env['candidate'].search([('job_opening_ids', 'in', self.id)])
        for rec in res_partner_job_opening:
            rec.update({'job_opening_ids': [(3, self.id)]})
        domain = [('categ_ids', '!=', False)]
        candidate_obj = self.env['candidate'].search(
            domain)
        if candidate_obj:
            for rec in candidate_obj:
                # application_data = self.env['hr.applicant'].search([('candidate_id', '=', rec.id),('job_opening_id','=',self.id),('active','=',False)])
                if self.categ_req_ids:
                    if self.id in rec.job_opening_ids.ids:
                        rec.update({'job_opening_ids': [(3, self.id)]})

                    if self.categ_opt_ids: 
                        if all([l in rec.categ_ids.ids for l in self.categ_req_ids.ids]) and any([l in rec.categ_ids.ids for l in self.categ_opt_ids.ids]):
                            rec.update({'job_opening_ids': [(4, self.id)]})
                    else:
                        if all([l in rec.categ_ids.ids for l in self.categ_req_ids.ids]):
                            rec.update({'job_opening_ids': [(4, self.id)]})

                elif self.id in rec.job_opening_ids.ids:
                    rec.update({'job_opening_ids': [(3, self.id)]})

    # def get_aspire_candidate(self):
    #     res_partner_job_opening = self.env['candidate'].search([('job_opening_ids', 'in', self.id)])
    #     for rec in res_partner_job_opening:
    #         rec.update({'job_opening_ids': [(3, self.id)]})
    #     domain = [('categ_ids', '!=', False)]
    #     if self.minimum_exp:
    #         domain += [('total_exp_years', '>=', int(self.minimum_exp*12))]
    #     if self.maximum_exp:
    #         domain += [('total_exp_years', '<=', int(self.maximum_exp*12))]
    #     candidate_obj = self.env['candidate'].search(
    #         domain)
    #     if candidate_obj:
    #         for rec in candidate_obj:
    #             application_data = self.env['hr.applicant'].search([('candidate_id', '=', rec.id),('job_opening_id','=',self.id),('active','=',False)])
    #             if not application_data and self.categ_req_ids:
    #                 if self.id in rec.job_opening_ids.ids:
    #                     rec.update({'job_opening_ids': [(3, self.id)]})

    #                 if self.categ_opt_ids: 
    #                     if all([l in rec.categ_ids.ids for l in self.categ_req_ids.ids]) and any([l in rec.categ_ids.ids for l in self.categ_opt_ids.ids]):
    #                         rec.update({'job_opening_ids': [(4, self.id)]})
    #                 else:
    #                     if all([l in rec.categ_ids.ids for l in self.categ_req_ids.ids]):
    #                         rec.update({'job_opening_ids': [(4, self.id)]})
    
    #             elif application_data and self.categ_req_ids:
    #                 opening_criteria_days = int(self.re_eligable_criteria) * 30
    #                 current_date = datetime.now().date()

    #                 if application_data.refused_date:
    #                     diff_date = current_date - application_data.refused_date
    #                 else:
    #                     diff_date = current_date - (application_data.write_date).date()
                              
    #                 if diff_date > timedelta(opening_criteria_days):
    #                     if self.id in rec.job_opening_ids.ids:
    #                         rec.update({'job_opening_ids': [(3, self.id)]})

    #                     if self.categ_opt_ids: 
    #                         if all([l in rec.categ_ids.ids for l in self.categ_req_ids.ids]) and any([l in rec.categ_ids.ids for l in self.categ_opt_ids.ids]):
    #                             rec.update({'job_opening_ids': [(4, self.id)]})
    #                     else:
    #                         if all([l in rec.categ_ids.ids for l in self.categ_req_ids.ids]):
    #                             rec.update({'job_opening_ids': [(4, self.id)]})

    #                 elif self.id in rec.job_opening_ids.ids:
    #                     rec.update({'job_opening_ids': [(3, self.id)]})

    #             elif self.id in rec.job_opening_ids.ids:
    #                 rec.update({'job_opening_ids': [(3, self.id)]})
    
    
    def move_aspire_candidate_to_application(self):
        res_partner_obj = self.env['candidate'].search([('job_opening_ids', 'in', self.id)])
        hr_application = self.env['hr.applicant']
        skill_lines = []
        # applicant_activity_dict = {}
        applicant_activity_list = []
        for skill in self.opening_skill_ids:
            skill_lines.append([0, 0, {
                'skill_id': skill.skill_id.id,
                'skill_level_id': skill.skill_level_id.id,
                'skill_type_id': skill.skill_type_id.id,
                'level_progress': skill.level_progress,
            }])
        # for rec in res_partner_obj:
            # difference = date_diff_in_seconds(datetime.now(), rec.create_date)
            # applicant_activity_dict[rec.id] = [0, 0, {
            #     'new_stage_id': self.env.ref('aspl_hr_recruitment.initial').id,
            #     'track_date': datetime.now(),
            #     'time_taken': difference,
            # }]
        # applicant_activity_list.append([0, 0, {
        #     'new_stage_id':self.env.ref('aspl_hr_recruitment.initial').id,
        #     'track_date': datetime.now(),
        # }])


        for rec in res_partner_obj:
            if hr_application.search([('active', 'in', [True, False])]).filtered(lambda p: p.candidate_id.id == rec.id):
                pass
            else:
                applicant = hr_application.create({
                    'name': rec.name,
                    'candidate_id': rec.id,
                    'partner_name': rec.name,
                    'email_from': rec.email,
                    'partner_mobile': rec.mobile,
                    'type_id': rec.type_id.id,
                    'categ_ids': rec.categ_ids.ids,
                    'interviewers_ids': self.user_id.ids,
                    'reviewer_user_ids': self.user_id.ids,
                    'job_id': self.job_id.id,
                    'department_id': self.department_id.id,
                    'source_id': rec.source_id.id,
                    'stage_id': self.env.ref('aspl_hr_recruitment.initial').id,
                    'user_id': self.user_id.id,
                    'job_opening_id': self.id,
                    'private_note': rec.private_note,
                    'date_received': rec.date_received,
                    'total_exp_years': rec.total_exp_years,
                    'is_candidate': True,
                    'current_ctc':rec.salary_current,
                    'total_exp':rec.total_exp,
                    'salary_expected':rec.salary_expected,
                    'current_location_city':rec.current_location_city.id,
                    'year_of_passing':rec.year_of_passing,
                    'referred_id':rec.partner_id.id,
                    'current_company_id':rec.current_company_id.id,
                    'description':rec.description,
                    # 'message_main_attachment_id': rec.message_main_attachment_id.id,
                    # 'job_opening_ids': [(4, self.id)]
                })
                applicant.update({'applicant_skill_ids': skill_lines})
                rec.in_application = True
                rec.is_applicant = True
                rec.is_candidate = True
                rec.is_employee = False
                rec.active_employee = False
                # applicant.update({'applicant_activity_ids': applicant_activity_list})

                current_uid = request.env.context.get('uid')
                user = self.env['res.users'].browse(current_uid)
                activity_status = self.env['mail.activity.type'].search([('name', '=',applicant.stage_id.name),('res_model','ilike','hr.applicant')])
                applicant.write({
                    'applicant_activity_ids':[(0,0,{
                        'activity':activity_status.id,
                        'track_date':datetime.now(),
                        'user_id':user.id,
                        'job_opening':applicant.job_opening_id.id
                    })]
                })
                # applicant.update({'applicant_activity_ids': applicant_activity_dict.get(rec.id)})
        for candidate in res_partner_obj:
            candidate.write({'user_id': self.user_id.id})


class JobOpeningSkill(models.Model):
    _name = 'job.opening.skill'
    _description = "Skill level for Job Opening"
    _rec_name = 'skill_id'
    _order = "skill_level_id"

    job_opening_id = fields.Many2one('job.opening', required=True, ondelete='cascade')
    skill_id = fields.Many2one('hr.skill', required=True)
    skill_level_id = fields.Many2one('hr.skill.level')
    skill_type_id = fields.Many2one('hr.skill.type', required=True)
    level_progress = fields.Integer(related='skill_level_id.level_progress')

    _sql_constraints = [
        ('_unique_skill', 'unique (job_opening_id, skill_id)', "Two levels for the same skill is not allowed"),
    ]

    @api.onchange('skill_type_id', 'skill_id')
    def _update_skill_level_progress(self):
        for rec in self:
            if rec.skill_type_id:
                rec.skill_level_id = rec.skill_type_id.skill_level_ids.ids[-1]
                rec.level_progress = self.env['hr.skill.level'].browse(
                    rec.skill_type_id.skill_level_ids.ids[-1]).level_progress

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

# class CalendarMeeting(models.Model):
#     _inherit = 'calendar.event'
#
#     @api.model
#     def _default_partners(self):
    #     """ When active_model is res.partner, the current partners should be attendees """
        # partners = self.env.user.partner_id
        # active_id = self._context.get('active_id')
        # if self._context.get('active_model') == 'res.partner' and active_id and active_id not in partners.ids:
        #     partners |= self.env['res.partner'].browse(active_id)
        # employees = self.employee_ids.search([('with_organization', '=', True)]).ids
        # if employees:
        #     partners |= self.employee_ids.search([('with_organization', '=', True)])
        # print("\nPartners", partners)
        # return employees

    # def _active_employee(self):
    #     employees = self.env['hr.employee'].search([('with_organization', '=', True)]).ids
    #     print("\nEmployees\n", employees)
    #     if employees:
    #         return [('id', 'in', employees)]

    # partner_ids = fields.Many2many(
    #     'res.partner', 'calendar_event_res_partner_rel',
    #     string='Attendees', default=_default_partners)  # domain=_active_employee

    # employee_ids = fields.Many2many('hr.employee', string='Employees') # default=_default_partners
