from odoo import models, fields, api, _
import base64
import os
import pymssql
from openpyxl import Workbook
from odoo.exceptions import UserError, ValidationError


class Connector(models.Model):
    _name = 'connector.sqlserver'
    _description = 'SQL Server connector class for fetch attendance from the device'
    _rec_name = 'name'

    @api.onchange('db_name', 'db_ip', 'db_user', 'password', 'db_port')
    def on_info(self):
        self.state = 'new'

    name = fields.Char(string='Name', required=True)
    db_name = fields.Char(string='Database', required=True)
    db_ip = fields.Char(string='Server', required=True)
    db_user = fields.Char(string='User', required=True)
    password = fields.Char(string='Password', required=True)
    db_port = fields.Char(string='Database port', required=True)
    state = fields.Selection([('new', 'New'), ('active', 'Active'), ('deactive', 'De Active')], default='new')
    auto_gen_attendance = fields.Boolean("Automatic Attendance Generation")

    # company_id = fields.Many2one('res.company', 'Company'),

    def connect(self):
        for rec in self:
            server = rec.db_ip
            try:
                conn = pymssql.connect(
                    host=server, user=rec.db_user, password=rec.password, database=rec.db_name, port=rec.db_port)
                rec.write({'state': 'active'})
            except ValueError as e:
                raise ValidationError(_('Connection error: ' + e))
            conn.close()

    # def connect(self):
    #     pass

    def attendance_process(self):
        return {
            'name': _("Attendance"),
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'attendance.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'domain': '[]',
            'context': {'connection_id': self.id},
        }

    def active(self):
        self.write({'state': 'active'})

    def deactive(self):
        self.write({'state': 'deactive'})

    def disconnect(self, conn):
        conn.close()

    def getNewCursor(self, conn):
        return conn.cursor()

    def selectView(self, cursor, view_name):
        cursor.execute('SELECT * FROM ' + view_name)
        return cursor

    # def attendance_biometric_process(self,cr,uid,context=None):
    #
    #     try:
    #         connectionOId = self.search(cr,uid,[],context)
    #         connectionOData = self.browse(cr,uid,connectionOId,context)
    #         for connection in connectionOData:
    #             biometricObj = self.pool.get('attendance.biometric.file')
    #             biometricId = biometricObj.search(cr,uid,[('connection_id','=',connection.id)],context,limit=1,order='id desc')
    #             biometricData = biometricObj.browse(cr,uid,biometricId,context)
    #             start_date = datetime.strptime(biometricData.end_date, DEFAULT_SERVER_DATE_FORMAT).date() + timedelta(days=1)
    #             end_date =  datetime.now().date() - timedelta(days=1)
    #             active_id = [connection.id]
    #             sql = "exec create_attendance_view select * from formatted_attendance where date >= '" +str(start_date)+ "' and date <= '" +str(end_date)+ "' ; "
    #             conn = pymssql.connect(server=connection.db_ip, user=connection.db_user, password=connection.password,database=connection.db_name)
    #             cursor = conn.cursor()
    #             cursor.execute(sql)
    #             row = cursor.fetchone()
    #             if row is not None:
    #                 wb = Workbook()
    #                 ws = wb.active
    #                 ws.append(["Dept. Name","Staff no.","Name","Date","Punch1","Punch2","Punch3","Punch4","Punch5","Punch6","Punch7","Punch8","Punch9","Punch10","Punch11","Punch12","Punch13","Punch14","Punch15","Punch16","Punch17","Punch18","Punch19","Punch20","Punch21","Punch22","Punch23","Punch24","Punch25","Punch26","Punch27","Punch28","Punch29","Punch30","Punch31","Punch32","Punch33","Punch34","Punch35","Punch36","Punch37","Punch38","Punch39","Punch40","Punch41","Punch42","Punch43","Punch44","Punch45","Punch46","Punch47"])
    #                 while row is not None:
    #                     data = [str(row[var]) for var in range(len(row))]
    #                     punch_list = data[4].split(",")
    #                     data.pop()
    #                     full_data_list = data + punch_list
    #                     ws.append(full_data_list)
    #                     row = cursor.fetchone()
    #                 wb.save('name.xlsx')
    #                 conn.close()
    #                 name = 'name.xlsx'
    #                 self.add_biometric_file(cr, uid, name,connection,start_date,end_date,active_id,context)
    #     except Exception,e:
    #         print e

    # parent method is commented, Useless the below method
    # def add_biometric_file(self, name, connection, start_date, end_date, active_id):
    #     file_obj = open(name, "r")
    #     file_string = file_obj.read()
    #     file_name = self.get_biometric_file_name(connection.name, start_date, end_date)
    #     file_id = self.env['attendance.biometric.file'].create({
    #         'name': file_name,
    #         'type': 'binary',
    #         'datas_fname': file_name + '.xlsx',
    #         'datas': base64.encodestring(file_string),
    #         'start_date': start_date,
    #         'end_date': end_date,
    #         'connection_id': active_id[0]
    #     })
    #     os.remove('name.xlsx')
    #     self.env['hr.attendance'].emp_attendance_time_scheduler(file_id)

    def get_biometric_file_name(self, name, start_date, end_date):
        file_name = name + '_' + str(start_date) + '_' + str(end_date)
        return file_name
