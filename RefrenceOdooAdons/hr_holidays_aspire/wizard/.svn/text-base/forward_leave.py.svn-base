from openerp.osv import fields, osv
from datetime import date
from openerp.tools.translate import _
import logging

class ForwardLeave(osv.osv_memory):
    _name = 'forward.leave'

    _columns = {
        'forward_to': fields.many2one('hr.employee','Employee',domain=[('with_organization','=',True)]),
        'comment': fields.text("Comment"),
        'leave_id':fields.many2one('hr.holidays',"Leave Id"),
    }

    def forward(self, cr, uid, ids, context):
        print "Call applicant forward method"
        print "Context",self, cr, uid, ids,context
        ForwardLeaveObj =  self.pool.get('forward.leave')
        ForwardLeaveData = ForwardLeaveObj.browse(cr, uid, ids, context=None)
        print ForwardLeaveData.forward_to.name
        if context['leave_id']:

            self.pool.get('hr.holidays').write(cr, uid,context['leave_id'],{'forward_to':ForwardLeaveData.forward_to.id },context=None)
            ForwardLeaveObj.write(cr, uid,ids,{'leave_id':context['leave_id']}, context=None)
            holy_obj = self.pool.get('hr.holidays').browse(cr, uid, context['leave_id'], context=None)
            from_emp_obj = self.pool.get('res.users').browse(cr, uid,uid, context=None)

            message = _("<p> Leave request forwarded <br> From: %s  <br> To: %s <br> Note: %s </p>") % (holy_obj.forward_to.name, from_emp_obj.name, str(ForwardLeaveData.comment))

            self.pool['hr.holidays'].message_post(cr,uid,context['leave_id'],
            body=message,context=None)
		
