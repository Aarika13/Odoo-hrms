# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import base64
import io
import xlsxwriter
from datetime import date, timedelta
import datetime


class JobOpeningReport(models.TransientModel):
    _name = 'job.opening.report'
    _description = 'Job Opening Report'

    # recruiters_ids = fields.Many2many('res.users', string="Recruiters")
    recruiter_id = fields.Many2one('res.users', string="Recruiter")
    job_opening_ids = fields.Many2many('job.opening', string="Job Openings")
    date_from = fields.Date('From Date')
    date_to = fields.Date('To Date')
    company_id = fields.Many2one('res.company', string="Company")
    state = fields.Selection([
        ('recruit', 'In Progress'),
        ('open', 'Done')
    ], string='Status', default='recruit',
        help="Set whether the recruitment process is open or closed for this job position.")

    template_id = fields.Many2one('job.opening.report.template', string="Report Template")

    def last_day_of_month(self, dt):
        last_day = (dt.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        return last_day

    def get_quarter_start(self, dt):
        return datetime.date(dt.year, (dt.month - 1) // 3 * 3 + 1, 1)

    def get_quarter_end(self, dt):
        next_qt_yr = dt.year + (1 if dt.month > 9 else 0)
        next_qt_first_mo = (dt.month - 1) // 3 * 3 + 4
        next_qt_first_mo = 1 if next_qt_first_mo == 13 else next_qt_first_mo
        next_qt_first_dy = datetime.date(next_qt_yr, next_qt_first_mo, 1)
        return next_qt_first_dy - datetime.timedelta(days=1)

    @api.onchange('template_id')
    def onchange_template_id(self):
        for rec in self:
            rec.recruiter_id = rec.template_id.recruiter_id.id or False
            rec.company_id = rec.template_id.company_id.id or False
            rec.job_opening_ids = rec.template_id.job_opening_ids.ids or False
            rec.state = rec.template_id.state or False
            if rec.template_id.period:
                if rec.template_id.period == "cm":
                    ld_of_cm = date.today() - timedelta(days=1)
                    sd_of_cm = date.today() - timedelta(days=ld_of_cm.day)
                    rec.date_from = sd_of_cm or False
                    rec.date_to = self.last_day_of_month(sd_of_cm)
                if rec.template_id.period == "lm":
                    ld_of_pm = date.today().replace(day=1) - timedelta(days=1)
                    sd_of_pm = date.today().replace(day=1) - timedelta(days=ld_of_pm.day)
                    rec.date_from = sd_of_pm or False
                    rec.date_to = self.last_day_of_month(sd_of_pm)
                if rec.template_id.period == "cq":
                    dt = datetime.date.today()
                    rec.date_from = self.get_quarter_start(dt)
                    rec.date_to = self.get_quarter_end(dt)
                if rec.template_id.period == "cy":
                    rec.date_from = date(date.today().year, 1, 1)
                    rec.date_to = date(date.today().year, 12, 31)

    @api.constrains('date_from', 'date_to')
    def check_date(self):
        """ This method is used to check constrains on dates."""
        if self.date_from and self.date_to and (self.date_from > self.date_to):
            raise ValidationError(_('To Date should be greater than From Date.'))

    def get_domain(self):
        """Method will filter record based on domain."""
        domain = []
        if self.job_opening_ids:
            domain += [('id', 'in', self.job_opening_ids.ids)]
        if self.recruiter_id:
            domain += [('user_id', '=', self.recruiter_id.id)]
        if self.state:
            domain += [('state', '=', self.state)]
        if self.company_id:
            domain += [('company_id', '=', self.company_id.id)]
        return domain

    def get_job_opening(self):
        """Method will filter job opening based on domain and returns it."""
        domain = self.get_domain()
        job_opening = self.env['job.opening'].search(domain)
        return job_opening

    def get_activity(self, applicant):
        """Method will filter applicant activity based on domain and returns it."""
        applicant_activity = self.env['applicant.activity'].search(
            [('applicant_id', '=', applicant.id)])
        status = False
        for a_a in applicant_activity:
            if a_a.old_stage_id.id == applicant.stage_id.id or a_a.new_stage_id.id == applicant.stage_id.id:
                status = True
                break
        return status

    def print_excel(self):
        """Method will print the excel report."""
        job_opening = self.get_job_opening()
        if not job_opening:
            raise ValidationError(_('No records found.'))
        fp = io.BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        worksheet = workbook.add_worksheet('Opening')
        data_format = workbook.add_format({'align': 'left'})
        data_format.set_border()
        report_header_format = workbook.add_format({'bold': True, 'align': 'center', 'font_size': 18})
        report_header_format.set_border()
        header_format = workbook.add_format({'bold': True, 'align': 'left'})
        header_format.set_border()
        worksheet.set_column('A:A', 40)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('D:D', 30)
        worksheet.set_column('E:E', 12)
        worksheet.set_column('F:F', 12)
        worksheet.set_column('G:G', 12)
        worksheet.set_column('H:H', 12)
        worksheet.set_column('I:I', 10)
        worksheet.set_column('J:J', 10)
        worksheet.set_column('K:K', 12)
        worksheet.set_column('L:L', 10)
        worksheet.set_column('M:M', 10)
        worksheet.set_column('N:N', 12)
        worksheet.set_column('O:O', 12)
        worksheet.set_column('P:P', 10)
        worksheet.merge_range('A1:J1', "Requirements", report_header_format)
        worksheet.merge_range('K1:L1', "Interview", report_header_format)
        worksheet.merge_range('M1:P1', "Offers", report_header_format)
        row = 1
        colm = 0
        if job_opening:
            row += 0
            worksheet.write(row, colm, 'Opening', header_format)
            colm += 1
            worksheet.write(row, colm, 'Recruiter', header_format)
            colm += 1
            worksheet.write(row, colm, 'WFH Available', header_format)
            colm += 1
            worksheet.write(row, colm, 'Company', header_format)
            colm += 1
            worksheet.write(row, colm, 'Request No', header_format)
            colm += 1
            worksheet.write(row, colm, 'Exp Range', header_format)
            colm += 1
            worksheet.write(row, colm, 'Open Positions', header_format)
            colm += 1
            worksheet.write(row, colm, 'Open Date', header_format)
            colm += 1
            worksheet.write(row, colm, 'Priority', header_format)
            colm += 1
            worksheet.write(row, colm, 'Status', header_format)
            colm += 1
            worksheet.write(row, colm, 'Scheduled', header_format)
            colm += 1
            worksheet.write(row, colm, 'Taken', header_format)
            colm += 1
            worksheet.write(row, colm, 'Given', header_format)
            colm += 1
            worksheet.write(row, colm, 'Accepted', header_format)
            colm += 1
            worksheet.write(row, colm, 'Rejected', header_format)
            colm += 1
            worksheet.write(row, colm, 'Joined', header_format)
            colm += 1
            scheduled_list = []
            taken_list = []
            given_list = []
            accepted_list = []
            rejected_list = []
            joined_list = []
            for opening in job_opening:
                colm = 0
                row += 1
                worksheet.write(row, colm, opening.name or "", data_format)
                colm += 1
                worksheet.write(row, colm, opening.user_id.name, data_format)
                colm += 1
                wfh = dict(opening._fields['wfh'].selection).get(opening.wfh)
                worksheet.write(row, colm, wfh, data_format)
                colm += 1
                worksheet.write(row, colm, opening.company_id.name, data_format)
                colm += 1
                worksheet.write(row, colm, opening.req_no, data_format)
                colm += 1
                # if opening.exp_range:
                #     worksheet.write(row, colm, opening.exp_range, data_format)
                # else:
                #     worksheet.write(row, colm, '', data_format)
                colm += 1
                worksheet.write(row, colm, opening.no_of_recruitment, data_format)
                colm += 1
                date = opening.create_date.strftime("%d-%b-%Y")
                worksheet.write(row, colm, date, data_format)
                colm += 1
                priority = dict(opening._fields['priority'].selection).get(opening.priority)
                worksheet.write(row, colm, priority, data_format)
                colm += 1
                state = dict(opening._fields['state'].selection).get(opening.state)
                worksheet.write(row, colm, state, data_format)
                colm += 1
                hr_applicant = self.env['hr.applicant'].search(
                    [('active', 'in', [True, False]), ('job_opening_id', '=', opening.id)])
                scheduled, taken = 0, 0
                given, accepted, rejected, join = 0, 0, 0, 0
                for applicant in hr_applicant:
                    activity = self.get_activity(applicant)
                    if activity:
                        scheduled += 1
                    if applicant.interview == 'done':
                        taken += 1
                    if applicant.stage_id.name == "Offered":
                        if applicant.offer == 'given':
                            given += 1
                        if applicant.offer == 'accepted':
                            accepted += 1
                        if applicant.active is False:
                            rejected += 1
                        if applicant.offer == 'joined':
                            join += 1
                scheduled_list.append(scheduled)
                # Scheduled
                worksheet.write(row, colm, scheduled, data_format)
                colm += 1
                # Taken
                taken_list.append(taken)
                worksheet.write(row, colm, taken, data_format)
                colm += 1
                # Given
                given_list.append(given)
                worksheet.write(row, colm, given, data_format)
                colm += 1
                # Accepted
                accepted_list.append(accepted)
                worksheet.write(row, colm, accepted, data_format)
                colm += 1
                # Rejected
                rejected_list.append(rejected)
                worksheet.write(row, colm, rejected, data_format)
                colm += 1
                # Joined
                joined_list.append(join)
                worksheet.write(row, colm, join, data_format)
                colm += 1
            row += 1
            worksheet.write(row, 5, 'Total', data_format)
            # Total
            opening_total = sum([nor.no_of_recruitment for nor in job_opening])
            scheduled_total = sum(scheduled_list)
            taken_total = sum(taken_list)
            given_total = sum(given_list)
            accepted_total = sum(accepted_list)
            rejected_total = sum(rejected_list)
            join_total = sum(joined_list)
            worksheet.write(row, 6, opening_total, data_format)
            worksheet.write(row, 10, scheduled_total, data_format)
            worksheet.write(row, 11, taken_total, data_format)
            worksheet.write(row, 12, given_total, data_format)
            worksheet.write(row, 13, accepted_total, data_format)
            worksheet.write(row, 14, rejected_total, data_format)
            worksheet.write(row, 15, join_total, data_format)

        # Joining Details
        worksheet = workbook.add_worksheet('Joining Details')
        worksheet.set_column('A:A', 45)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('D:D', 20)
        worksheet.set_column('E:E', 15)
        worksheet.set_column('F:F', 15)
        worksheet.set_column('G:G', 15)
        worksheet.set_column('H:H', 15)
        row = 0
        colm = 0
        if job_opening:
            row += 0
            worksheet.write(row, colm, 'Candidate Name', header_format)
            colm += 1
            worksheet.write(row, colm, 'Request No', header_format)
            colm += 1
            worksheet.write(row, colm, 'Recruiter', header_format)
            colm += 1
            worksheet.write(row, colm, 'Last Interview Date', header_format)
            colm += 1
            worksheet.write(row, colm, 'Offered Date', header_format)
            colm += 1
            worksheet.write(row, colm, 'CTC', header_format)
            colm += 1
            worksheet.write(row, colm, 'Joining Date', header_format)
            colm += 1
            worksheet.write(row, colm, 'Reporting To', header_format)
            colm += 1
            '''
            for opening in job_opening:
                colm = 0
                row += 1
                worksheet.write(row, colm, opening.name, data_format)
                colm += 1
                worksheet.write(row, colm, opening.user_id.name, data_format)
                colm += 1
                wfh = dict(opening._fields['wfh'].selection).get(opening.wfh)
                worksheet.write(row, colm, wfh, data_format)
                colm += 1
                worksheet.write(row, colm, opening.company_id.name, data_format)
                colm += 1
                worksheet.write(row, colm, opening.req_no, data_format)
                colm += 1
                worksheet.write(row, colm, opening.exp_range, data_format)
                colm += 1
                worksheet.write(row, colm, opening.no_of_recruitment, data_format)
                colm += 1
                date = opening.create_date.strftime("%d-%b-%Y")
                worksheet.write(row, colm, date, data_format)
                colm += 1
            '''
        workbook.close()
        fp.seek(0)
        result = base64.b64encode(fp.read())
        attachment_obj = self.env['ir.attachment']
        attachment_id = attachment_obj.create({'name': 'Aspire Recruitment Report.xlsx',
                                               'store_fname': 'Aspire Recruitment Report.xlsx',
                                               'datas': result})
        download_url = '/web/content/' + \
                       str(attachment_id.id) + '?download=True'
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return {
            "type": "ir.actions.act_url",
            "url": str(base_url) + str(download_url),
            "target": "new"
        }
