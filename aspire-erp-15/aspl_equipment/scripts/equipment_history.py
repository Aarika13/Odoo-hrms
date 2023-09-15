import odoorpc

# Odoo 9 Environment server and login credentials
odoo_9 = odoorpc.ODOO('192.168.2.44', port=8009)
odoo_9.login('9_hrms_test_2821', 'admin', 'admin')

# Odoo 15 Environment server and login credentials
odoo_15 = odoorpc.ODOO('192.168.2.110', port=8069)
odoo_15.login('2710_for_tester', 'admin', 'admin')

equipment_history_fields = ['current_employee', 'mt_sequence_no', 'id', 'display_name', 'effective_from',
                            'effective_to', 'employee', 'equipment_id']


class CreateEquipmentHistory:

    # Equipment History Values
    def equipment_history_result(self, equip_hist):
        equipment_result = {'current_employee': equip_hist.get('current_employee'),
                            'mt_sequence_no': equip_hist.get('mt_sequence_no'),
                            'display_name': equip_hist.get('display_name'),
                            'effective_from': equip_hist.get('effective_from'),
                            'effective_to': equip_hist.get('effective_to'),
                            'v9_id': equip_hist.get('id'),
                            }
        return equipment_result

    # Employee
    def fetch_employee(self, values):
        employee = odoo_15.execute('hr.employee', 'search_read',
                                   [['name', '=', values]], ['id'])
        return employee

    # Equipment
    def fetch_equipment(self, values):
        employee = odoo_15.execute('maintenance.equipment', 'search_read',
                                   [['v9_id', '=', values]], ['id'])
        return employee

    # Equipment History
    def create_equipment_history(self):
        equipment_history_info_v9 = odoo_9.execute('hr.equipment.history', 'search_read',
                                                   [], equipment_history_fields)  # ['id', '=', 1702]
        print('Length Equipment History ---- >>>>', len(equipment_history_info_v9))
        employee_list = []
        for equip_hist in equipment_history_info_v9:
            equipment_history = odoo_15.env['equipment.history']
            existing_rec = equipment_history.search([('v9_id', '=', equip_hist.get('id'))], limit=1)
            if existing_rec:
                print('\n 50 IF ->', existing_rec)
            else:
                print('\n 52 ELSE equip_hist -->>', equip_hist)
                equip_hist_values = self.equipment_history_result(equip_hist)
                if equip_hist.get('employee'):
                    values = equip_hist.get('employee')[1]
                    employee = self.fetch_employee(values)
                    print('\n employee', employee)
                    if employee:
                        equip_hist_values['employee'] = employee[0].get('id')
                    else:
                        print('Else ->')
                        employee_list.append(equip_hist.get('employee'))
                        equip_hist_values['employee'] = 21
                if equip_hist.get('equipment_id'):
                    values = equip_hist.get('equipment_id')[0]
                    equipment_id = self.fetch_equipment(values)
                    if equipment_id:
                        equip_hist_values['equipment_id'] = equipment_id[0].get('id')
                equipment_history_of_odoo15 = odoo_15.execute('equipment.history', 'create', equip_hist_values)
                print('\n Equipment History Of Odoo 15 --->>', equipment_history_of_odoo15)
                print('\n Employee List --->>', employee_list)


x = CreateEquipmentHistory()
x.create_equipment_history()
print('\n ॐ \n')
