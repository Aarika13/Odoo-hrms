# -*- coding: utf-8 -*-

from odoo import tools, models, fields, api, _
from dateutil import parser
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta


# from collections import Iterable


class MaintenanceEquipment(models.Model):
    _name = 'maintenance.equipment'
    _inherit = 'maintenance.equipment'
    _description = 'Equipment'
    _check_company_auto = False

    def _compute_replaced_with_name(self):
        for record in self:
            replace_name_id = self.search([('replace_with', 'in', (self.ids))])
            if replace_name_id:
                for record_data in replace_name_id:
                    record.replaced_with_name = record_data.name
            else:
                record.replaced_with_name = ""

    def _compute_parent_child_record(self):
        values = self.search([('parent', 'in', self.ids)])
        if len(values) > 0:
            self.child_record = len(values)
        else:
            self.child_record = 0

    @api.onchange('parent')
    def on_change_parent(self):
        for record in self:
            if record.parent:
                record.employee_id = record.parent.employee_id.id

    replace_with = fields.Many2one('maintenance.equipment', 'Replaced With', tracking=True)
    replacing = fields.Many2one('maintenance.equipment', 'Replacing', tracking=True)
    replaced_with_name = fields.Char(compute='_compute_replaced_with_name', string='Replaced With')
    # replaced_with_id = fields.Many2one('maintenance.equipment', 'Replaced With id')
    # name = fields.Char('Asset Name', readonly=True, translate=True, copy=False) # already exist in Odoo 15
    # category_id = fields.Many2one('maintenance.equipment.category', string='Asset Category',
    #                               track_visibility='onchange',
    #                               required=True) # already exist in Odoo 15
    name = fields.Char('Equipment Name', required=False, translate=True, readonly=False)
    replacement_date = fields.Date('Replacement Date', tracking=True)
    parent = fields.Many2one('maintenance.equipment', 'Parent', tracking=True)
    categ_ids = fields.Many2many('equipment.tag', string="Tags")
    child_record = fields.Integer(compute='_compute_parent_child_record', string='Related Equipments')
    manufacturing = fields.Many2one('equipment.manufacturing', 'Manufacturing')
    bill_no = fields.Char('Bill No.')
    equipment_histy = fields.One2many('equipment.history', 'equipment_id', 'Employee Equipment History')
    # scrap_date = fields.Date('Scrap Date', readonly=True) # already exist in Odoo 15
    warranty = fields.Date('Warranty Start Date')
    warranty_end_date = fields.Date('Warranty End Date', readonly=True)
    warranty_period = fields.Integer('Warranty Period')
    in_warranty = fields.Integer(string='In Warranty')
    stock_type = fields.Selection([('in_ward', 'Inward'), ('out_ward', 'Outward')], string='Location',
                                  required=True, default='in_ward')
    # Already exist but added for add domain
    employee_id = fields.Many2one('hr.employee', string='Employee', domain=[('with_organization', "=", True)])

    usable_asset = fields.Boolean('Usable Asset', default=True)
    purchase_date = fields.Date('Purchase Date')
    maintenance_stock_type = fields.Boolean('Maintenance Stock Type', default=False)
    technician_id = fields.Many2one('res.partner', string='Technician Id', domain="[('supplier', '=', 1)]")
    # Already exist in Odoo 15
    # company_id = fields.Many2one('res.company', 'Company', required=True)
    equipment_sequence_no = fields.Integer('Equipment Sequence No')
    v9_id = fields.Integer('ID from V9')

    @api.onchange('purchase_date')
    def _onchange_purchase_date(self):
        self.warranty = self.purchase_date

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        for rec in self:
            parent = rec.get_parent_equipment(rec.employee_id.id)
            if parent:
                rec.parent = parent

    # Commented for script
    @api.model
    def create(self, vals):
        if vals.get('category_id') and vals.get('company_id'):
            equipment_short_code = self.env['maintenance.equipment.category'].browse(
                [vals.get('category_id')]).short_code
            company_short_code = self.env['res.company'].browse([vals.get('company_id')]).code
            equipment_format = company_short_code + '/AST/' + equipment_short_code + '/'
            equipment_id = self.sudo().search([('name', 'like', equipment_format)], order='equipment_sequence_no desc',
                                              limit=1)
            if equipment_id:
                vals['name'] = company_short_code + '/AST/' + equipment_short_code + '/' + str(
                    equipment_id.equipment_sequence_no + 1).zfill(4)
                vals['equipment_sequence_no'] = equipment_id.equipment_sequence_no + 1
            else:
                vals['name'] = company_short_code + '/AST/' + equipment_short_code + '/' + str(1).zfill(4)
                vals['equipment_sequence_no'] = 1

        if vals.get('employee_id'):
            vals['equipment_histy'] = [[0, False,
                                        {'employee': vals.get('employee_id'),
                                         'effective_from': datetime.today(),
                                         # 'ticket_no': 'N/A',
                                         'effective_to': False,
                                         'mt_sequence_no': 'N/A'}]]

        if vals.get('warranty_period'):
            if int(vals['warranty_period']) != 0:
                if vals['warranty'] is not False:
                    warranty_end_date = parser.parse(str(vals['warranty'])) + relativedelta(
                        months=+int(vals['warranty_period'])) - relativedelta(days=1)
                    vals['warranty_end_date'] = warranty_end_date
        return super(MaintenanceEquipment, self).create(vals)

    def write(self, vals):
        user_ids = []
        data = {}
        # equipmentBrowseObj = self.env['hr.equipment'].search([])
        if 'equipment_histy' in vals:
            for values in vals['equipment_histy']:
                for val in values:
                    if isinstance (val,dict):
                        # if isinstance(val, Iterable):
                        equipmentBoj = self.env['maintenance.equipment'].search([('id', '=', self.id)])
                        equipmentBrowseObj = self.env['maintenance.equipment'].search([('parent', '=', self.id)])
                        if val.get('effective_to') is False and val.get('employee') or val.get(
                                'effective_from') and val.get('employee'):
                            equipment_histy_obj = self.env['equipment.history']
                            equipment_id = self.id
                            if equipmentBrowseObj:
                                for record in equipmentBrowseObj:

                                    history_id = self.env['equipment.history'].search(
                                        [('current_employee', '=', True), ('equipment_id', '=', equipment_id)])

                                    if history_id:
                                        for history_Obj in history_id:
                                            self.env['equipment.history'].browse(history_Obj.id).write(
                                                {'effective_to': date.today() - timedelta(days=1),
                                                'current_employee': False})

                                        data['effective_from'] = val['effective_from']
                                        data['equipment_id'] = record.id
                                        data['employee'] = val['employee']
                                        # data['ticket_no'] = val['ticket_no']
                                        equipment_histy_obj.create(data)

                                    else:

                                        data['effective_from'] = val['effective_from']
                                        data['equipment_id'] = record.id
                                        data['employee'] = val['employee']
                                        # data['ticket_no'] = val['ticket_no']
                                        equipment_histy_obj.create(data)

                                    equipmentChilRecObj = self.env['maintenance.equipment'].search(
                                        [('parent', '=', record.id)])

                                    equipment_child_histy_obj = self.env['equipment.history']

                                    if equipmentChilRecObj:
                                        for recordObj in equipmentChilRecObj:
                                            history_id = self.env['equipment.history'].search(
                                                [('current_employee', '=', True), ('equipment_id', '=', recordObj.id)])
                                            if history_id:
                                                for history_Obj in history_id:
                                                    self.env['equipment.history'].browse(history_Obj.id).write(
                                                        {'effective_to': date.today() - timedelta(days=1),
                                                        'current_employee': False})

                                                data['effective_from'] = val['effective_from']
                                                data['equipment_id'] = recordObj.id
                                                data['employee'] = val['employee']
                                                # data['ticket_no'] = val['ticket_no']
                                                equipment_child_histy_obj.create(data)
                                            else:

                                                data['effective_from'] = val['effective_from']
                                                data['equipment_id'] = recordObj.id
                                                data['employee'] = val['employee']
                                                # data['ticket_no'] = val['ticket_no']
                                                # print data
                                                equipment_child_histy_obj.create(data)

                                            self.env['maintenance.equipment'].browse(recordObj.id).write(
                                                {'employee_id': val['employee']})

                                    self.env['maintenance.equipment'].browse(record.id).write(
                                        {'employee_id': val['employee']})

                            vals['employee_id'] = val['employee']

                        elif val.get('effective_to') is not False:

                            equipmentBrowseObj = self.env['maintenance.equipment'].search([('parent', '=', self.id)])
                            for record in equipmentBrowseObj:
                                self.env['maintenance.equipment'].browse(record.id).write(
                                    {'employee_id': None})  # 'ticket_no': None
                            vals['employee_id'] = None
                            # vals['ticket_no'] = None

        # subscribe employee or department manager when equipment assign to employee or department.
        if vals.get('employee_id'):
            user_id = self.env['hr.employee'].browse(vals['employee_id'])['user_id']['partner_id']
            vals['equipment_histy'] = [[0, False,
                                        {'employee': vals.get('employee_id'),
                                         'effective_from': datetime.today(),
                                         # 'ticket_no': 'N/A',
                                         'effective_to': False,
                                         'mt_sequence_no': 'N/A'}]]
            if self.env['maintenance.equipment'].search([('parent', '=', self.id)]):
                for record in self.env['maintenance.equipment'].search([('parent', '=', self.id)]):
                    record.write({'employee_id': vals.get('employee_id')})
            if user_id:
                user_ids.append(user_id.id)

        if vals.get('department_id'):
            department = self.env['hr.department'].browse(vals['department_id'])
            if department and department.manager_id and department.manager_id.user_id:
                user_ids.append(department.manager_id.user_id.id)

        if vals.get('warranty_period'):
            if int(vals['warranty_period']) != 0:
                count = 0
                for record in self.env['maintenance.equipment'].browse(self.id):
                    if record.warranty:
                        warranty_end_date = parser.parse(str(record.warranty)) + relativedelta(
                            months=+int(vals['warranty_period'])) - relativedelta(days=1)
                        vals['warranty_end_date'] = warranty_end_date
                        count += 1
                if count == 0:
                    warranty_end_date = parser.parse(str(vals['warranty'])) + relativedelta(
                        months=+int(vals['warranty_period'])) - relativedelta(days=1)
                    vals['warranty_end_date'] = warranty_end_date

        if vals.get('warranty'):
            for record in self.env['maintenance.equipment'].browse(self.id):
                if record.warranty_period != 0:
                    warranty_end_date = parser.parse(str(vals['warranty'])) + relativedelta(
                        months=+int(record.warranty_period)) - relativedelta(days=1)
                    vals['warranty_end_date'] = warranty_end_date

        if vals.get('serial_no') and vals.get('replacement_date'):
            for record in self.env['maintenance.equipment'].browse(self.id):
                if record.serial_no and record.replacement_date and str(record.serial_no) != str(vals.get('serial_no')):
                    message = 'Equipment Replaced' + '<ul><li>' + 'Serial No: ' + str(
                        record.serial_no) + ' ' + '&#8594;' + ' ' + vals.get(
                        'serial_no') + '</li> <li>' + 'Replacement Date: ' + str(
                        vals.get('replacement_date')) + '</li></ul> '
                    self.message_post(subject='Replaced', body=message)

        if user_ids:
            self.message_subscribe(partner_ids=user_ids)
        return super(MaintenanceEquipment, self).write(vals)

    def calculate_in_warranty_scheduler(self):
        today = datetime.today()
        for record in self.search([]):
            if record.warranty_end_date:
                warranty_end_date = datetime.strptime(record.warranty_end_date, '%Y-%m-%d')
                if warranty_end_date >= today:
                    record.write({'in_warranty': 1})
                else:
                    record.write({'in_warranty': 0})

    def unassign_equipment(self):
        for equipment in self.search([('parent', '=', self.id)]):
            equipment.write({'employee_id': None})
            # self.update_equipment_history(equipment)

        self.write({'employee_id': None, 'parent': None})
        self.update_equipment_history(self.id)

    def update_equipment_history(self, equipment):
        history_id = self.env['equipment.history'].search([('current_employee', '=', True),
                                                           ('equipment_id', '=', [equipment])])
        print('equipment_id', '=', [equipment])

        if history_id:
            history_id.write({'effective_to': date.today(),
                              'current_employee': False,
                              'mt_sequence_no': 'N/A',
                              # 'ticket_no': ticket_no
                              })

    def get_parent_equipment(self, employee_id):
        category_id = self.env['maintenance.equipment.category'].search([('short_code', '=', 'COM')], limit=1)
        if self.category_id.id != category_id.id:
            parent_equipment = self.env['maintenance.equipment'].search(
                [('category_id', '=', category_id.id), ('employee_id', '=', employee_id)])
            if parent_equipment and len(parent_equipment) == 1:
                return parent_equipment.id
        return None


class Manufacturing(models.Model):
    _name = 'equipment.manufacturing'
    _description = 'Equipment Manufacturing'

    name = fields.Char('Company Name', required=True)


class EquipmentTags(models.Model):
    _name = 'equipment.tag'
    _description = 'Equipment Tag'

    name = fields.Char('Tag Name', required=True)
    color = fields.Integer('Color Index')


class MaintenanceRequest(models.Model):
    _name = 'maintenance.request'
    _inherit = 'maintenance.request'
    _check_company_auto = False

    mt_sequence_no = fields.Char("Maintenance No.", readonly=True)
    # close_date = fields.Date('Actual Close Date') # Already exists in Odoo 15
    tentative_date = fields.Date('Tentative Return Date', tracking=True)
    equip_stage = fields.Char(related='stage_id.name', string="Stage")
    v9_id = fields.Integer('ID from V9')
    close_date = fields.Date('Close Date', help="Date the maintenance was finished. ", tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('name'):
            vals['mt_sequence_no'] = self.env['ir.sequence'].next_by_code('maintenance.request') or '/'
        # vals['mt_sequence_no'] = self.env.get('ir.sequence').get('maintenance.request')
        equipment_req = super(MaintenanceRequest, self).create(vals)
        return equipment_req

    def archive_equipment_in_progress_request(self):
        search_domain = [('name', '=', 'In Progress')]
        stage_ids = self.env['maintenance.stage'].search(search_domain)
        if stage_ids:
            self.write({'stage_id': stage_ids[0]})
            if self.equipment_id:
                self.equipment_id.write({'stock_type': 'out_ward',
                                         'maintenance_stock_type': True,
                                         'employee_id': None,
                                         'parent': None})
                for record in self:

                    history_id = self.env['equipment.history'].search([('current_employee', '=', True),
                                                                       ('equipment_id', '=',
                                                                        record.equipment_id.id)])
                    if history_id:
                        history_id.write({'effective_to': date.today(),
                                          'current_employee': False,
                                          'mt_sequence_no': self.mt_sequence_no,
                                          })

        return True

    def archive_equipment_repaired_request(self):
        stage_id = self.env['maintenance.stage'].search([('name', '=', 'Repaired')])
        date_obj = date.today()
        if stage_id:
            self.write({'stage_id': stage_id.id,
                        'close_date': date_obj,
                        'tentative_date': date_obj})
            if self.equipment_id:
                self.equipment_id.write({'stock_type': 'in_ward',
                                         'maintenance_stock_type': False})
        return True

    def archive_equipment_replace_request(self):
        return {
            'name': _("Replacement"),
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'equipment.replaced',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'domain': '[]',
            'context': {'active_id': self._context.get('active_id') if self._context else ''},
        }

    def archive_equipment_scarp_request(self):
        date_obj = date.today()
        stage_id = self.env['maintenance.stage'].search([('name', '=', 'Scrap')])
        if stage_id:
            self.write({'stage_id': stage_id.id,
                        'close_date': date_obj})
            if self.equipment_id:
                self.equipment_id.write({'stock_type': 'out_ward',
                                         'scrap_date': date_obj,
                                         'maintenance_stock_type': True,
                                         'usable_asset': False})
        return True

    def archive_equipment_cancel_request(self):
        stage_id = self.env['maintenance.stage'].search([('name', '=', 'Cancel')])
        if stage_id:
            self.write({'stage_id': stage_id.id})
        return True


class MaintenanceEquipmentCategory(models.Model):
    _name = 'maintenance.equipment.category'
    _inherit = ['maintenance.equipment.category']

    short_code = fields.Char('Category Code', required=True, translate=True)

