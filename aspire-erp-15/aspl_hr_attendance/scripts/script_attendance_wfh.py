import odoorpc
from datetime import datetime

# Odoo 9 Environment server and login credentials
odoo_9 = odoorpc.ODOO('localhost', port=8009)
odoo_9.login('9_hrms_test_2821', 'admin', 'admin')

# Odoo 15 Environment server and login credentials
odoo_15 = odoorpc.ODOO('localhost', port=8017)
odoo_15.login('feb28', 'admin', 'admin')

hr_attendance_wfh_fields = ['id', 'name', 'employee_id', 'start_date', 'end_date', 'flag', 'record_status',
                            'work_summary', 'work_state', 'user_id', 'total_time', 'loged_in_user']
attendance_wfh_info_v9 = odoo_9.execute('attendance.work_from_home', 'search_read',
                                        [['start_date', '>', '2021-06-01 00:00:00']],
                                        hr_attendance_wfh_fields)  # ['employee_id', '=', 172],
print('Length Application -->>', len(attendance_wfh_info_v9))
for attendance in attendance_wfh_info_v9:
    # if employee.get('state') in ('validate', 'confirm'):
    odoo9_emp = odoo_9.env['hr.employee'].browse(attendance.get('employee_id')[0])
    hr_employee = odoo_15.env['hr.employee']
    existing_rec = hr_employee.search([('v9_employee_no', '=', odoo9_emp.employee_no)], limit=1)
    v9_attendance_id_check = odoo_15.env['attendance.work.from.home'].search([('v9_attendance_id', '=', int(attendance.get('id')))], limit=1)
    print('-------------existing_rec--------v9_attendance_id-------------')
    print('-------------', existing_rec, '--------', v9_attendance_id_check, '-------------')
    print("Attendance Data", attendance)
    float_diff = 0.0
    if attendance.get('start_date') and attendance.get('end_date'):
        start = attendance.get('start_date').split()[-1].split(':')
        start_time = datetime.strptime(start[0]+':'+start[1], "%H:%M")
        end = attendance.get('end_date').split()[-1].split(':')
        end_time = datetime.strptime(end[0]+':'+end[1], "%H:%M")
        diff = end_time-start_time
        float_diff = diff.seconds / 3600
    if v9_attendance_id_check:
        print('----------------------------------------EXIST---------------------------------------------------')
    else:
        if existing_rec:
            v15_user = odoo_15.env['res.users'].search([('employee_id', '=', existing_rec[0])], limit=1)
            v15_wfh_vals = {
                'name':  attendance.get('name'),
                'employee_id': existing_rec[0],
                'start_date': attendance.get('start_date'),
                'end_date': attendance.get('end_date'),
                'flag': attendance.get('flag'),
                'record_status': attendance.get('record_status'),
                'work_summary': attendance.get('work_summary'),
                'work_state': attendance.get('work_state'),
                'user_id': v15_user[0],
                'total_time': float_diff,
                'logged_in_user': attendance.get('loged_in_user'),
                'v9_attendance_id': int(attendance.get('id'))
            }
            print(v15_wfh_vals)
            v_15_attachment_id = odoo_15.execute('attendance.work.from.home', 'create', v15_wfh_vals)
        print('--------------------------------------------Created-----------------------------------------------')

print('\n========== ॐ ==========\n')
