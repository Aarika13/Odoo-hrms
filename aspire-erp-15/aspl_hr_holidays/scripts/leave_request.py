import odoorpc

# Odoo 9 Environment server and login credentials
odoo_9 = odoorpc.ODOO('localhost', port=8009)
odoo_9.login('9_hrms_test_2821', 'admin', 'admin')

# Odoo 15 Environment server and login credentials
odoo_15 = odoorpc.ODOO('localhost', port=8017)
odoo_15.login('28_march', 'admin', 'admin')

hr_leave_fields = ['id', 'adjust_plannedleave', 'type', 'holiday_status_id', 'employee_id', 'state', 'date_from', 'date_to', 'granted_date', 'name', 'sequence', 'number_of_days', 'number_of_days_temp']
leave_info_v9 = odoo_9.execute('hr.holidays', 'search_read', [['type', '=', 'remove']], hr_leave_fields)    # ['employee_id', '=', 172],
print('Length Application -->>', len(leave_info_v9))
for employee in leave_info_v9:
    if employee.get('state') in ('validate', 'confirm'):
        odoo9_emp = odoo_9.env['hr.employee'].browse(employee.get('employee_id')[0])
        hr_employee = odoo_15.env['hr.employee']
        existing_rec = hr_employee.search([('v9_employee_no', '=', odoo9_emp.employee_no)], limit=1)
        request_id_check = odoo_15.env['hr.leave'].search([('request_id', '=', int(employee.get('id')))], limit=1)
        print('Existing_Employee_Record', existing_rec)
        print("Req Id", request_id_check)
        if request_id_check:
            hr_leave_type = odoo_15.env['hr.leave.type'].search([
                ('name', '=', employee.get('holiday_status_id')[1])])
            hr_leave_req_id = odoo_15.env['hr.leave'].browse(request_id_check[0])
            if hr_leave_req_id.number_of_days != employee.get('number_of_days_temp'):
                vals = {
                    'holiday_status_id': hr_leave_type[0],
                    'name': employee.get('name'),
                    'request_date_from': employee.get('date_from'),
                    'date_from': employee.get('date_from'),
                    'request_date_to': employee.get('date_to'),
                    'date_to': employee.get('date_to'),
                    'state': employee.get('state'),
                    'employee_id': existing_rec[0],
                    'holiday_type': 'employee',
                    'number_of_days': employee.get('number_of_days_temp'),
                    'adjust_planned_leave': employee.get('adjust_plannedleave'),
                    'request_id': int(employee.get('id'))
                }
                hr_leave_req_id.write(vals)
                print('---------------------------------------Updated-------------------------------------------')
        else:
            if existing_rec:
                hr_leave_type = odoo_15.env['hr.leave.type'].search([
                    ('name', '=', employee.get('holiday_status_id')[1])])
                print("Employee", employee)
                print("Leave Type", hr_leave_type)
                leave_vals = {
                    'holiday_status_id': hr_leave_type[0],
                    'name': employee.get('name'),
                    'request_date_from': employee.get('date_from'),
                    'date_from': employee.get('date_from'),
                    'request_date_to': employee.get('date_to'),
                    'date_to': employee.get('date_to'),
                    'state': employee.get('state'),
                    'employee_id': existing_rec[0],
                    'holiday_type': 'employee',
                    'number_of_days': employee.get('number_of_days_temp'),
                    'adjust_planned_leave': employee.get('adjust_plannedleave'),
                    'request_id': int(employee.get('id'))
                    }
                v_15_attachment_id = odoo_15.execute('hr.leave', 'create', leave_vals)
            print('--------------------------------------------Created-----------------------------------------------')

print('\n========== END ==========\n')
