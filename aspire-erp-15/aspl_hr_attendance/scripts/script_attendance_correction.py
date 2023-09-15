import odoorpc
from datetime import datetime
import time
# Odoo 9 Environment server and login credentials
odoo_9 = odoorpc.ODOO('localhost', port=8009)
odoo_9.login('9_hrms_test_2821', 'admin', 'admin')

# Odoo 15 Environment server and login credentials
odoo_15 = odoorpc.ODOO('localhost', port=8017)
odoo_15.login('feb28', 'admin', 'admin')

hr_attendance_correction_fields = ['id', 'name', 'employee_id', 'in_time', 'out_time',
                                   'work_state', 'user_id', 'total_time', 'loged_in_user', 'note']
attendance_correction_info_v9 = odoo_9.execute('attendance.corrections', 'search_read',
                                               # YYYY-MM-DD HH:MM:SS
                                               [['in_time', '>', '2021-02-01 00:00:00']],
                                               hr_attendance_correction_fields)  # ['employee_id', '=', 107]
print('Length Application -->>', len(attendance_correction_info_v9))
for correction in attendance_correction_info_v9:
    # if employee.get('state') in ('validate', 'confirm'):
    odoo9_emp = odoo_9.env['hr.employee'].browse(correction.get('employee_id')[0])
    hr_employee = odoo_15.env['hr.employee']
    existing_rec = hr_employee.search([('v9_employee_no', '=', odoo9_emp.employee_no)], limit=1)
    v9_correction_id_check = odoo_15.env['attendance.corrections'].search([('v9_correction_id', '=', int(correction.get('id')))], limit=1)
    print('-------------existing_rec--------v9_correction_id_check-------------')
    print('-------------', existing_rec, '--------', v9_correction_id_check, '-------------')
    print("Attendance Correction Data", correction)
    float_diff = 0.0
    print("\nIn time\n", correction.get('in_time'))
    if correction.get('in_time') and correction.get('out_time'):
        start = correction.get('in_time').split()[-1].split(':')
        start_time = datetime.strptime(start[0]+':'+start[1], "%H:%M")
        end = correction.get('out_time').split()[-1].split(':')
        end_time = datetime.strptime(end[0]+':'+end[1], "%H:%M")
        diff = end_time-start_time
        float_diff = diff.seconds / 3600
    if v9_correction_id_check:
        print('----------------------------------------EXIST---------------------------------------------------')
    else:
        if existing_rec:
            v15_user = odoo_15.env['res.users'].search([('employee_id', '=', existing_rec[0])], limit=1)
            v15_correction_vals = {
                'name':  correction.get('name'),
                'employee_id': existing_rec[0],
                'in_time': correction.get('in_time'),
                'out_time': correction.get('out_time'),
                'work_state': correction.get('work_state'),
                'user_id': v15_user[0],
                'total_time': float_diff,
                'logged_in_user': correction.get('loged_in_user'),
                'note': correction.get('note'),
                'v9_correction_id': int(correction.get('id'))
            }
            v_15_attachment_id = odoo_15.execute('attendance.corrections', 'create', v15_correction_vals)
        print('--------------------------------------------Created-----------------------------------------------')

print('\n========== ॐ ==========\n')
