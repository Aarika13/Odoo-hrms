import xlsxwriter
from io import BytesIO
import base64
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
import traceback
import logging
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class TimeSheetActivityReport(models.Model):
    _name = 'timesheet.activity.xls.report'
    _description = "Timesheet Activity Report"

    start_date = fields.Date("Start Date", required=True)
    end_date = fields.Date("End Date", required=True)
    project_id = fields.Many2one('account.analytic.account', 'Project', required=True)

    def get_employee_leave(self, cr, uid, start_month_date_obj, temp_emp_id, context):
        """ calculate total employee leaves """
        try:
            start_date = str(start_month_date_obj)
            # holiday_obj = self.env['hr.holidays']
            holiday_obj = self.env['hr.leave']
            holiday_search_obj = holiday_obj.search([
                ('date_from', '<=', start_date),
                ('date_to', '>=', start_date),
                ('state', 'in', ['validate1', 'validate']),
                ('user_id', '=', temp_emp_id)
            ])

            holiday_data_obj = holiday_obj.browse(cr, uid, holiday_search_obj, context=context)
            total_leave = 0.0
            if holiday_data_obj:
                total_leave = 1.0
                return total_leave
            else:
                return total_leave

        except Exception as e:
            traceback.format_exc()
            _logger.error('Something is wrong')
            _logger.error(str(e))
            return 0

    def get_public_holidays(self, cr, uid, start_month_date_obj, context):
        """ calculate public holidays """
        res = {}
        try:
            start_date = str(start_month_date_obj)
            # holiday_obj = self.env['hr.holidays.detail']
            holiday_obj = self.env['resource.calendar.leaves']
            holiday_search_obj = holiday_obj.search([
                ('holiday_from', '<=', start_date),
                ('holiday_from', '>=', start_date)
            ])

            holiday_data_obj = holiday_obj.browse(cr, uid, holiday_search_obj, context=context)
            if holiday_data_obj:
                res['1'] = holiday_data_obj.des
                return res
            else:
                return res

        except Exception as e:
            traceback.format_exc()
            _logger.error('Something is wrong')
            _logger.error(str(e))
            return res

    def print_report(self, cr, uid, ids, context=None):

        data = self.env['timesheet.activity.xls.report'].browse(ids)
        tms_activity_obj = self.env['account.analytic.line']
        tms_activity_search_obj = tms_activity_obj.search([
            ('date', '<=', data.end_date),
            ('date', '>=', data.start_date),
            ('account_id', '=', data.project_id.id)
        ], order="date asc")
        tms_activity_data_obj = tms_activity_obj.browse(tms_activity_search_obj)
        start_date = datetime.strptime(data.start_date, DEFAULT_SERVER_DATE_FORMAT)
        end_date = datetime.strptime(data.end_date, DEFAULT_SERVER_DATE_FORMAT)
        total_days = (end_date - start_date).days
        start_month_date = datetime(start_date.year, start_date.month, 1).date()
        excel_data = {}
        pro_obj = self.env['project.project']
        pro_search_obj = pro_obj.search([('analytic_account_id', '=', data.project_id.id)])
        pro_data_obj = pro_obj.browse(pro_search_obj)
        total_developer = len(pro_data_obj.member_id)

        developers_list = []
        for record in pro_data_obj.member_id:
            # if not record.end_date:
            # 	dev_end_date= date.today()
            # else:
            # 	dev_end_date=datetime.strptime(record.end_date,DEFAULT_SERVER_DATE_FORMAT).date()

            # if not record.start_date:
            # 	raise Warning(_('Please set project member start date.'))
            # else:
            # 	dev_start_date = datetime.strptime(record.start_date,DEFAULT_SERVER_DATE_FORMAT).date()

            res = dict(emp_name=record.name.name, emp_id=record.name.id)
            developers_list.append(res)

        developers = {}
        for record in pro_data_obj.member_id:
            try:
                if developers[record.name.name]:
                    pass
            except Exception as e:
                developers[record.name.name] = dict(name=record.name.name, user_id=record.name.id)
        # developers[record.display_name.name] = dict(name=record.display_name.name,user_id=record.display_name.id)
        # print "===+++===",asasas
        time_sheet_dict = {}
        if tms_activity_data_obj:
            for record in tms_activity_data_obj:
                activity_date = datetime.strptime(record.date, DEFAULT_SERVER_DATE_FORMAT).date()
                try:
                    if time_sheet_dict[record.date]:
                        try:
                            for dev in developers_list:
                                # print "dev==",dev
                                if record.user_id.id == dev['emp_id']:
                                    if time_sheet_dict[record.date][dev['emp_name']]:
                                        time = float(record.unit_amount) + float(
                                            time_sheet_dict[record.date][dev['emp_name']]['hours'])
                                        comment_obj = str(
                                            time_sheet_dict[record.date][dev['emp_name']]['description']) + '\n' + str(
                                            record.name)
                                        time_sheet_dict[record.date][dev['emp_name']]['hours'] = time
                                        time_sheet_dict[record.date][dev['emp_name']]['description'] = comment_obj
                        except Exception as e:
                            for dev in developers_list:
                                if record.user_id.id == dev['emp_id']:
                                    user_id = dev['emp_id']
                                    display_name = dev['emp_name']
                                    break

                            comment = str('(') + str(display_name) + str(')') + '\n' + ' ' + str(record.name)
                            time_sheet_dict[record.date][display_name] = dict(user_id=user_id, hours=record.unit_amount,
                                                                            name=display_name, description=comment)
                except KeyError:
                    time_sheet_dict[record.date] = dict(date=record.date)
                    for dev in developers_list:
                        # print "===++++===+++===",dev
                        if record.user_id.id == dev['emp_id']:
                            user_id = dev['emp_id']
                            display_name = dev['emp_name']
                            break
                    # elif record.user_id.id == dev['emp_id']:
                    # 	display_name=dev['display_name']
                    # 	user_id = dev['emp_id']

                    comment = str('(') + str(display_name) + str(')') + '\n' + ' ' + str(record.name)
                    time_sheet_dict[record.date][display_name] = dict(user_id=user_id, hours=record.unit_amount,
                                                                    name=display_name, description=comment)

        filename = str(data.project_id.name) + ' Timsheet ' + str(start_date.strftime("%b")) + ' ' + str(
            start_date.year) + '.xlsx'

        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        # Add a bold format to use to highlight cells.
        bold = workbook.add_format({'bold': 1})

        text_format = workbook.add_format({'text_wrap': True, 'align': 'left', 'font_size': 10, 'font_name': 'Calibri'})
        bg_color = workbook.add_format(
            {'bg_color': '#C6EFCE', 'font_size': 10, 'align': 'right', 'font_name': 'Calibri'})
        numb_format = workbook.add_format(
            {'text_wrap': True, 'align': 'right', 'font_size': 10, 'font_name': 'Calibri'})
        column_alignment = workbook.add_format({'align': 'right'})

        header_format = workbook.add_format(
            {'text_wrap': True, 'align': 'left', 'font_size': 10, 'font_name': 'Calibri', 'bold': 1})

        none_work_day_format = workbook.add_format(
            {'align': 'right', 'font_size': 10, 'font_name': 'Calibri', 'bg_color': 'EAC6E9'})

        weekEndExtraWorkDayNumFormat = workbook.add_format(
            {'bg_color': '#C6EFCE', 'font_size': 10, 'align': 'left', 'font_name': 'Calibri'})

        work_day_num_format = workbook.add_format({'font_size': 10, 'align': 'right', 'font_name': 'Calibri'})

        weekEndWorkDayNumFormat = workbook.add_format(
            {'bg_color': '#4BA85D', 'font_size': 10, 'align': 'right', 'font_name': 'Calibri'})
        weekEndWorkDayTextFormat = workbook.add_format(
            {'bg_color': '#4BA85D', 'font_size': 10, 'align': 'left', 'font_name': 'Calibri'})

        # Write some data headers.
        worksheet = workbook.add_worksheet('Summary')
        worksheet.write('A1', 'Date', header_format)
        worksheet.write('B1', '# Week', header_format)
        worksheet.write('C1', 'Description', header_format)
        worksheet.set_column('A:A', 6, header_format)
        worksheet.set_column('B:B', 5, header_format)
        worksheet.set_column('C:C', 50, header_format)

        count = 100
        reg = 3
        col_data_dict = {}
        for record in developers:
            column_name = str(chr(count).upper()) + str('1')
            col_data_dict[record] = dict(col=column_name, index=reg, emp_name=developers[record]['name'])
            worksheet.write(column_name, record, header_format)
            count += 1
            reg += 1

        column_name = str(chr(count).upper()) + str('1')
        worksheet.write(column_name, 'Total Hours', header_format)
        row = 1
        day = 0
        date_row_index = {}

        for i in range(0, total_days + 1):
            start_month_date = datetime(start_date.year, start_date.month, row).date()
            merge_comment = ''
            dateObj = str(start_month_date.day) + '-' + str(start_month_date.strftime("%b"))
            week_num = (start_month_date.day - 1) // 7 + 1
            week_day = start_month_date.weekday()
            start_month_date_obj = str(start_month_date)
            pubHoliday = self.get_public_holidays(cr, uid, start_month_date_obj, context)

            count = 100
            first_column = str(chr(count).upper()) + str(row + 1)
            last_column = str(chr(count + len(col_data_dict) - 1).upper()) + str(row + 1)

            if week_day == 5 or week_day == 6:
                try:
                    if time_sheet_dict[str(start_month_date_obj)]:
                        if pubHoliday:
                            merge_comment = str(merge_comment) + '\n' + str('Holiday: ') + str(pubHoliday['1'])
                        for emp in developers:
                            col = col_data_dict[emp]['index']
                            try:
                                if time_sheet_dict[str(start_month_date_obj)][emp]:
                                    worksheet.write(row, 0, str(dateObj), bg_color)
                                    worksheet.write(row, 1, week_num, bg_color)
                                    merge_comment = str(merge_comment) + '\n' + str(
                                        time_sheet_dict[str(start_month_date_obj)][emp]['description'])
                                    worksheet.write(row, col,
                                                    float(time_sheet_dict[str(start_month_date_obj)][emp]['hours']),
                                                    bg_color)

                            except Exception as e:
                                worksheet.write(row, col, 0.0, bg_color)

                        worksheet.write(row, 2, str(merge_comment), weekEndExtraWorkDayNumFormat)
                        worksheet.write(row, int(len(col_data_dict) + 3),
                                        '=SUM(' + first_column + ':' + last_column + ')', bg_color)

                except KeyError:
                    comment = ''
                    if pubHoliday:
                        comment = str(merge_comment) + '\n' + str('Holiday: ') + str(pubHoliday['1'])
                        row_num_format = weekEndWorkDayNumFormat
                        row_text_format = weekEndWorkDayTextFormat
                    else:
                        row_text_format = bg_color
                        row_num_format = bg_color

                    worksheet.write(row, 0, str(dateObj), row_num_format)
                    worksheet.write(row, 1, week_num, row_num_format)
                    for emp in developers:
                        if col_data_dict[emp]:
                            col = col_data_dict[emp]['index']
                            worksheet.write(row, col, 0.0, row_num_format)
                    worksheet.write(row, 2, comment, row_text_format)
                    worksheet.write(row, int(len(col_data_dict) + 3), '=SUM(' + first_column + ':' + last_column + ')',
                                    row_num_format)

            else:
                try:
                    if time_sheet_dict[str(start_month_date_obj)]:

                        if pubHoliday:
                            merge_comment = str(merge_comment) + '\n' + str('Holiday: ') + str(pubHoliday['1'])
                            row_num_format = weekEndWorkDayNumFormat
                            row_text_format = weekEndWorkDayTextFormat
                        else:
                            row_text_format = text_format
                            row_num_format = numb_format

                        for emp in developers:
                            col = col_data_dict[emp]['index']
                            try:
                                if time_sheet_dict[str(start_month_date_obj)][emp]:
                                    worksheet.write(row, 0, str(dateObj), row_num_format)
                                    worksheet.write(row, 1, week_num, row_num_format)
                                    merge_comment = str(merge_comment) + '\n\n' + str(
                                        time_sheet_dict[str(start_month_date_obj)][emp]['description'])
                                    worksheet.write(row, col,
                                                    float(time_sheet_dict[str(start_month_date_obj)][emp]['hours']),
                                                    row_num_format)

                            except Exception as e:
                                user_id = developers[emp]['user_id']
                                leave = self.get_employee_leave(cr, uid, start_month_date_obj, user_id, context)
                                if leave == 0.0:
                                    worksheet.write(row, col, 0.0, row_num_format)
                                else:
                                    worksheet.write(row, col, 0.0, none_work_day_format)

                        worksheet.write(row, 2, str(merge_comment), row_text_format)
                        worksheet.write(row, int(len(col_data_dict) + 3),
                                        '=SUM(' + first_column + ':' + last_column + ')', row_num_format)

                except KeyError:
                    comment = ''
                    if pubHoliday:
                        comment = str(merge_comment) + '\n' + str('Holiday: ') + str(pubHoliday['1'])
                        row_num_format = weekEndWorkDayNumFormat
                        row_text_format = weekEndWorkDayTextFormat
                    else:
                        row_text_format = text_format
                        row_num_format = numb_format

                    worksheet.write(row, 0, str(dateObj), row_num_format)
                    worksheet.write(row, 1, week_num, row_num_format)
                    for emp in developers:
                        if col_data_dict[emp]:
                            col = col_data_dict[emp]['index']
                            worksheet.write(row, col, 0.0, row_num_format)
                    worksheet.write(row, 2, comment, row_text_format)
                    worksheet.write(row, int(len(col_data_dict) + 3), '=SUM(' + first_column + ':' + last_column + ')',
                                    row_num_format)

            row += 1

        indexNum = 0
        for emp in developers:
            count = 100
            first_row_column = str(chr(count + indexNum).upper()) + str(2)
            last_row_column = str(chr(count + indexNum).upper()) + str(total_days + 2)
            if col_data_dict[emp]:
                col = col_data_dict[emp]['index']
                worksheet.write(total_days + 2, col, '=SUM(' + first_row_column + ':' + last_row_column + ')',
                                numb_format)
                indexNum += 1

        sum_first_column = str(chr(count).upper()) + str(total_days + 3)
        sum_last_column = str(chr(count + len(col_data_dict) - 1).upper()) + str(total_days + 3)

        worksheet.write(total_days + 2, int(len(col_data_dict) + 3),
                        '=SUM(' + sum_first_column + ':' + sum_last_column + ')', numb_format)

        workbook.close()
        excel_file_id = self.pool.get('timesheet.activity.xls').create(cr, uid,
                                                                       {'file': base64.encodestring(output.getvalue()),
                                                                        'file_name': filename}, context=context)

        return {
            'res_id': excel_file_id,
            'res_model': 'timesheet.activity.xls',
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'context': context,
            'target': 'new',

        }
