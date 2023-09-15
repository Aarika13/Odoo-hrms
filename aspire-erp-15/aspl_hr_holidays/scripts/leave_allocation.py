import odoorpc
# from datetime import datetime, date

# Odoo 9 Environment server and login credentials
odoo_9 = odoorpc.ODOO('localhost', port=8009)
odoo_9.login('9_hrms_test_2821', 'admin', 'admin')

# Odoo 15 Environment server and login credentials
odoo_15 = odoorpc.ODOO('localhost', port=8017)
odoo_15.login('leave1', 'admin', 'admin')

hr_leave_fields = ['id', 'type', 'holiday_status_id', 'employee_id', 'state', 'date_from', 'date_to', 'granted_date', 'name', 'sequence', 'number_of_days', 'number_of_days_temp']
leave_info_v9 = odoo_9.execute('hr.holidays', 'search_read', [['type', 'in', ('add', 'carry_forward', 'lapsed')]], hr_leave_fields)     # ['employee_id', '=', 172],
print('Length Application -->>', len(leave_info_v9))
for employee in leave_info_v9:
    if employee.get('state') == 'validate':
        odoo9_emp = odoo_9.env['hr.employee'].browse(employee.get('employee_id')[0])
        hr_employee = odoo_15.env['hr.employee']
        existing_rec = hr_employee.search([('v9_employee_no', '=', odoo9_emp.employee_no)], limit=1)
        alloc_id_check = odoo_15.env['hr.leave.allocation'].search([('allocation_id', '=', int(employee.get('id')))], limit=1)
        print(int(employee.get('id')))
        print('20 existing_rec', existing_rec)
        print("Allocation Id", alloc_id_check)
        if alloc_id_check:
            print('----------------------------------------EXIST---------------------------------------------------')
        else:
            if existing_rec:
                hr_leave_type = odoo_15.env['hr.leave.type'].search([
                    ('name', '=', employee.get('holiday_status_id')[1])])
                print("Employee", employee)
                print("Leave Type", hr_leave_type)
                leave_vals = {
                    'holiday_status_id': hr_leave_type[0],
                    'name': employee.get('name'),
                    'date_from': employee.get('granted_date'),
                    'state': 'validate',
                    'employee_id': existing_rec[0],
                    'type': employee.get('type'),
                    'holiday_type': 'employee',
                    'number_of_days': employee.get('number_of_days'),
                    'adjust_planned_leave': False,
                    'allocation_id': int(employee.get('id'))
                    }
                v_15_attachment_id = odoo_15.execute('hr.leave.allocation', 'create', leave_vals)
            print('---------------------------------------Created----------------------------------------------------')

print('\n========== ॐ ==========\n')
