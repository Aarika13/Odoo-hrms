import pymssql
from odoo import fields, models
import logging
from openpyxl import Workbook
from datetime import datetime

_logger = logging.getLogger(__name__)
import base64
import os


class AttendanceWizard(models.TransientModel):
    _name = 'attendance.wizard'
    _description = 'Attendance Wizard'

    start_date = fields.Date('Start date', required=True)
    end_date = fields.Date('End date', required=True)

    def generate_attendance(self):
        active_id = self.env.context['connection_id']
        connector_obj = self.env['connector.sqlserver'].search([('id', '=', active_id)])
        sql = "select * from formatted_attendance where date >= '" + str(
            self.start_date) + "' and date <= '" + str(
            self.end_date) + "' order by employeecode,date;"
        conn = pymssql.connect(server=connector_obj.db_ip, user=connector_obj.db_user,
                               password=connector_obj.password, database=connector_obj.db_name,port=connector_obj.db_port)
        cursor = conn.cursor()
        cursor.execute(sql)
        row = cursor.fetchone()
        wb = Workbook()
        ws = wb.active
        ws.append(
            ["Dept. Name", "Staff no.", "Name", "Date", "Punch1", "Punch2", "Punch3", "Punch4", "Punch5", "Punch6",
             "Punch7", "Punch8", "Punch9", "Punch10", "Punch11", "Punch12", "Punch13", "Punch14", "Punch15", "Punch16",
             "Punch17", "Punch18", "Punch19", "Punch20", "Punch21", "Punch22", "Punch23", "Punch24", "Punch25",
             "Punch26", "Punch27", "Punch28", "Punch29", "Punch30", "Punch31", "Punch32", "Punch33", "Punch34",
             "Punch35", "Punch36", "Punch37", "Punch38", "Punch39", "Punch40", "Punch41", "Punch42", "Punch43",
             "Punch44", "Punch45", "Punch46", "Punch47"])
        while row is not None:
            data = [str(row[var]) for var in range(len(row))]
            punch_list = data[4].split(",")
            data.pop()
            full_data_list = data + punch_list
            ws.append(full_data_list)
            row = cursor.fetchone()
        name = '/opt/odoo/name.xlsx'
        wb.save(name)
        conn.close()
        start_date = self.start_date
        end_date = self.end_date
        self.add_biometric_file(name, connector_obj, start_date, end_date, active_id)

    def add_biometric_file(self, name, connector_obj, start_date, end_date, active_id):
        file_string = open(name, 'rb').read()
        file_name = connector_obj.name + '_' + str(start_date) + '_' + str(end_date)
        file_id = self.env['attendance.biometric.file'].create({
            'name': file_name,
            'type': 'binary',
            'datas_fname': file_name + '.xlsx',
            'datas': base64.encodebytes(file_string),
            'start_date': start_date,
            'end_date': end_date,
            'connection_id': active_id
        })
        os.remove(name)
        self.emp_attendance_time_scheduler(file_id)
        # data = self.pool.get('hr.attendance').emp_attendance_time_scheduler(cr, uid, file_id, context)

    def emp_attendance_time_scheduler(self, file_id):
        """ Employee attendance scheduler """
        attend_file_obj = self.env['attendance.biometric.file'].search([('id', '=', file_id.id)])
        attendance_obj = self.env['hr.attendance']
        if self.ids:
            attendanceSheetDataObj = attend_file_obj.browse(self.ids)
        else:
            att_file_obj = self.env['attendance.biometric.file'].search([('id', '=', self.file_id.id)])
            attenExcSheetDataObjSearch = att_file_obj.search([])
            attendanceSheetDataObj = att_file_obj.browse(attenExcSheetDataObjSearch)

        count = 0
        try:
            attend_file_obj.write({'status': 'in_progress'})
            time = datetime.now()
            # iterate attendance biometric file record
            for record in attend_file_obj:
                file_id = record.id
                # check file status is failure
                if 'failure' in str(record.status) or str(record.status).upper() in 'FAILURE':
                    count += 1
                    attendance_obj.delete_hr_attendance(file_id)
                    # self.delete_attendance_daily_summary(file_id)
                    # self.delete_attendance_monthly_summary(file_id)
                    attendance_obj.update_attendance_file_status_is_in_progress(time, file_id)
                    attendance_obj.excel_sheet_emp_attendance_record(time, file_id)
            # call first time if file record is not created
            if count == 0:
                attendance_obj.update_attendance_file_status_is_in_progress(time, file_id)
                attendance_obj.excel_sheet_emp_attendance_record(time, file_id)
        except Exception as e:
            _logger.error('Something is wrong')
            _logger.error(str(e))
