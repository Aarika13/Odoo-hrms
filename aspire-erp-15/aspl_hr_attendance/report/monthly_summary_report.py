from datetime import datetime
from odoo import models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import logging

_logger = logging.getLogger(__name__)


class HrAttendanceSummaryReport(models.AbstractModel):
    _name = 'report.aspl_hr_attendance.attendance_summary_report'
    _description = 'HR Attendance Summary Report'

    def _get_attendance_daily_summary(self, data, empid):
        res = {}
        daily_summary_obj = self.env['attendance.daily.summary']
        start_date = data['form']['date_from']
        end_date = data['form']['date_to']
        try:
            daily_summary_ids = daily_summary_obj.search([('emp_id', '=', empid), ('date', '>=', start_date),
                                                          ('date', '<=', end_date)])
            total_time = 0
            break_time = 0
            net_time = 0
            total_break = 0

            for daily_summary in daily_summary_ids:
                total_time = total_time + daily_summary.total_time_decimal
                break_time = break_time + daily_summary.total_break_time_decimal
                net_time = net_time + daily_summary.net_time_decimal
                total_break = total_break + daily_summary.total_break

            res['total_time'] = "{:0.2f}".format(total_time)
            res['break_time'] = "{:0.2f}".format(break_time)
            res['net_time'] = "{:0.2f}".format(net_time)
            res['total_break'] = total_break
            return res
        except Exception as e:
            _logger.error('Something is wrong')
            _logger.error(str(e))

    def _get_data_from_report(self, data):
        res = []
        emp_obj = self.env['hr.employee'].search([])
        try:
            daily_summary_obj = self.pool['attendance.daily.summary']
            count = 1
            for emp in emp_obj:
                daily_summary_ids = daily_summary_obj.search([('emp_id', '=', emp.id)])
                if daily_summary_ids:
                    res.append({
                        'no': count,
                        'emp_name': emp.name,
                        'emp_code': emp.employee_no,
                        'summary': self._get_attendance_daily_summary(data, emp.id)
                    })
                    count += 1
            return res
        except Exception as e:
            _logger.error('Something is wrong')
            _logger.error(str(e))

    def _get_company_info(self):
        comp_obj = self.env['res.company'].search([])
        res = []
        try:
            for record in comp_obj:
                data_obj = dict(name=record.name, street=record.street, street2=record.street2, city=record.city,
                                zip=record.zip)
                res.append(data_obj)
            return res
        except Exception as e:
            _logger.error('Something is wrong')
            _logger.error(str(e))

    def _get_header_info(self, data):
        try:
            return {
                'start_date': datetime.strptime(data['form']['date_from'], DEFAULT_SERVER_DATE_FORMAT).strftime(
                    ' %d, %b %Y'),
                'end_date': datetime.strptime(data['form']['date_to'], DEFAULT_SERVER_DATE_FORMAT).strftime(
                    '%d, %b %Y'),
            }
        except Exception as e:
            _logger.error('Something is wrong')
            _logger.error(str(e))

    # Deprecated this in Odoo 15
    # def render_html(self, cr, uid, ids, data=None, context=None):
    #     report_obj = self.pool['report']
    #     holidays_report = report_obj._get_report_from_name(cr, uid, 'hr_attendance_aspire.attendance_summary_report')
    #     selected_records = self.pool['attendance.daily_summary'].browse(cr, uid, ids, context=context)
    #     docargs = {
    #         'doc_ids': ids,
    #         'doc_model': holidays_report.model,
    #         'docs': self,
    #         'get_header_info': self._get_header_info(data),
    #         'get_company_info': self._get_company_info(cr, uid, ids, context=context),
    #         'get_data_from_report': self._get_data_from_report(cr, uid, ids, data, context=context),
    #     }
    #
    #     return report_obj.render(cr, uid, ids, 'hr_attendance_aspire.attendance_summary_report', docargs,
    #                              context=context)
