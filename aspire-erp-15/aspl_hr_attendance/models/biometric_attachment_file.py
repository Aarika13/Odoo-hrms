# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import logging
import traceback
_logger = logging.getLogger(__name__)
try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')
try:
    import cStringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')
_logger = logging.getLogger(__name__)

options = [
    ('success', 'Success'),
    ('in_progress', 'In Progress'),
    ('failure', 'Failure'),
]


class AttendanceBiometricFile(models.Model):
    _name = 'attendance.biometric.file'
    _description = 'Attendance Biometric File'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _compute_file_status(self):
        for record in self:
            if str(record.status).upper() in 'SUCCESS':
                record.file_status = True
            elif str(record.status).upper() in 'IN_PROGRESS':
                record.file_status = True
            else:
                record.file_status = False

    @api.onchange('status')
    def on_change_join_training_date(self):
        for record in self:
            record.end_time = None

    name = fields.Char("File Name", required=True)
    start_time = fields.Datetime("Start Time ")
    end_time = fields.Datetime("End Time")
    status = fields.Selection(options, 'Status')
    datas_fname = fields.Char('Data File Name')
    datas = fields.Binary('File Content', required=True)
    type = fields.Selection([('url', 'URL'), ('binary', 'File'), ],
                            'Type',
                            help="You can either upload a file from your computer "
                                 "or copy/paste an internet link to your file",
                            required=True, change_default=True, default='binary')
    url = fields.Char('Url', size=1024)
    file_status = fields.Boolean(compute='_compute_file_status', string="File Status")
    start_date = fields.Date("Start Date ", required=True)
    end_date = fields.Date("End Date", required=True)

    connection_id = fields.Many2one('connector.sqlserver', 'connector')

    def process_attendance_file(self):
        self.env['hr.attendance'].emp_attendance_time_scheduler()
        return True
        

    def unlink(self):
        """ override parent delete method and delete all record related to this file """
        # TODO: Will modify after migrate Timesheet module
        # self.cr._execute('UPDATE hr_attendance SET sheet_id=Null WHERE file_id=' + str(self.id))
        for rec in self:
            rec.delete_hr_attendance_record()
        # if len(self.id) == 1:
        #     self.delete_hr_attendance_record()
        #     # self.delete_attendance_daily_summary()
        #     # self.delete_attendance_monthly_summary()
        # else:
        #     for record in self:
        #         record.delete_hr_attendance_record()
        #         # record.delete_attendance_daily_summary()
        #         # record.delete_attendance_monthly_summary()

        return super(AttendanceBiometricFile, self).unlink()

    def delete_hr_attendance_record(self):
        """ delete hr attendance record """
        hr_attendance_obj = self.env['hr.attendance'].search([('file_id', '=', self.id)])
        try:
            if hr_attendance_obj:
                delete_sql = 'DELETE FROM public.hr_attendance WHERE id in' + str(hr_attendance_obj.ids).replace("[",
                                                                                                                 "(").replace(
                    "]", ")") + ';'
                self.env.cr.execute(delete_sql)
            return True
        except Exception as e:
            _logger.error('Something is wrong')
            _logger.error(str(e))
            return False

    # def delete_attendance_daily_summary(self):
    #     """ delete attendance daily summary record """
    #     attendance_daily_summary_obj = self.env['attendance.daily.summary'].search([('file_id', '=', self.id)])
    #     try:
    #         if attendance_daily_summary_obj:
    #             attendance_daily_summary_obj.unlink()
    #         return True
    #     except Exception as e:
    #         _logger.error('Something is wrong')
    #         _logger.error(str(e))
    #         return False

    # def delete_attendance_monthly_summary(self):
    #     """ delete attendance monthly summary record """
    #     attendance_monthly_summary = self.env['attendance.monthly.summary'].search([('file_id', '=', self.id)])
    #     try:
    #         if attendance_monthly_summary:
    #             attendance_monthly_summary.unlink()
    #         return True
    #     except Exception as e:
    #         _logger.error('Something is wrong')
    #         _logger.error(str(e))
    #         return False

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
