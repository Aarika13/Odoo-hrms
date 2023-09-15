import odoorpc
# from datetime import datetime, date

# Odoo 9 Environment server and login credentials
odoo_9 = odoorpc.ODOO('localhost', port=8009)
odoo_9.login('9_hrms_test_2821', 'admin', 'admin')

# Odoo 15 Environment server and login credentials
odoo_15 = odoorpc.ODOO('localhost', port=8017)
odoo_15.login('leave1', 'admin', 'admin')

public_holiday_fields = ['des', 'holiday_from']
public_holiday_info_v9 = odoo_9.execute('hr.holidays.detail', 'search_read', [], public_holiday_fields)
print('Length Application -->>', len(public_holiday_info_v9))
for public_holiday in public_holiday_info_v9:
    print('Public Holiday', public_holiday)
    public_holiday_vals = {
        'name': public_holiday.get('des'),
        'date_from': public_holiday.get('holiday_from'),
        'date_to': public_holiday.get('holiday_from'),
        }
    v_15_attachment_id = odoo_15.execute('resource.calendar.leaves', 'create', public_holiday_vals)
    print('--------------------------------------------Created-----------------------------------------------')

print('\n========== ॐ ==========\n')
