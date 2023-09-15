from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import timedelta, date
import logging

_logger = logging.getLogger(__name__)

class yimesheetTaskChange(models.TransientModel):
    _name = "timesheet.task.change"
    _description = "Timesheet Task Change"

    def _get_task_list(self):  
        if 'uid' in self.env.context:
            domain = [('user_ids', 'in', self.env.context['uid'])]
        else:
            domain = [('user_ids', '=', [])]      
        return domain
    
    task_id = fields.Many2one('project.task',string='Select task', required=True, domain=_get_task_list)
     
    def interchange_task_timesheet_project_record(self):
        if 'task_id' in self.env.context:
            task_id = self.env['project.task'].browse(self.env.context['task_id'])
            timesheet_records = task_id.timesheet_ids.filtered(lambda l: l.task_id == task_id)
            match_product = self.task_id.project_id.product_id
            
            if timesheet_records:
                for timesheet in timesheet_records:
                    if timesheet.product_type.id in match_product.ids:
                        timesheet.write({'task_id':self.task_id.id})
                    else:
                        timesheet.write({
                            'task_id':self.task_id.id,
                            'product_type':None,
                            })
