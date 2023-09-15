import re
from openerp import tools
from datetime import datetime
from dateutil import tz
from openerp.osv import fields, osv
from openerp.tools.translate import _

class calendar_event(osv.Model):
    """ Model for Calendar Event """
    _inherit = 'calendar.event'

    # Only create calendar event not send mail
    def create(self, cr, uid, vals, context):
        
        if 'type' in context:
            if context is None:
                context = {}
            
            self._set_date(cr, uid, vals, id=False, context=context)
            if not 'user_id' in vals:  # Else bug with quick_create when we are filter on an other user
                vals['user_id'] = uid
            res = osv.osv.create(self, cr, uid, vals, context=context)
            final_date = self._get_recurrency_end_date(cr, uid, res, context=context)
            self.write(cr, uid, [res], {'final_date': final_date}, context=context)
            return res
        else:
            return super(calendar_event, self).create(cr, uid, vals, context=context)
