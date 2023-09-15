# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from datetime import datetime


class EquipmentReplaced(models.TransientModel):
    _name = 'equipment.replaced'
    _description = 'Equipment Replaced'

    replaced_serial_no = fields.Char(string="Replaced Serial No", required=True)
    replacement_date = fields.Date(string='Replacement Date', default=datetime.today())

    def action_replace(self):
        active_id = self._context['active_ids']
        equipment_req_obj = self.env['maintenance.request']
        search_domain = [('name', '=', 'Replaced'), ]
        stage_id = self.env['maintenance.stage'].search(search_domain)
        if stage_id:
            if active_id:
                request = equipment_req_obj.browse(active_id)
                if request:
                    request.write({'stage_id': stage_id.id,
                                   'close_date': self.replacement_date})
                    
                    new_quipment_id = request.equipment_id.copy({
                        'stock_type': 'out_ward', 
                        'serial_no':self.replaced_serial_no,
                        'maintenance_stock_type': True,
                        'replacement_date': self.replacement_date,
                        'replacing':request.equipment_id.id
                    })
                    request.equipment_id.write({
                        'stock_type': 'out_ward', 
                        'maintenance_stock_type': True,
                        # 'serial_no': self.replaced_serial_no,
                        # 'replacement_date': self.replacement_date,
                        'replace_with':new_quipment_id.id,
                        'active':False
                        })

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
