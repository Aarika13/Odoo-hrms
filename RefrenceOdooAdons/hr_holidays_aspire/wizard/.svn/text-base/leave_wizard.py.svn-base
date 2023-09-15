from openerp import models, fields, api
from datetime import datetime, timedelta
import logging
from openerp.exceptions import UserError, ValidationError, Warning
_logger = logging.getLogger(__name__)

class leave_wizard(models.TransientModel):
	"""docstring for last_month_leave_wizard"""
	_name = 'leave.wizard'

	startDate = fields.Date('Start Date', required=True)
	endDate = fields.Date('End Date', required=True)
	reportType = fields.Selection([
		('approved', 'Approved'),
		('toapprove', 'To Approve'),
		('unapplied', 'Un Applied'),
		('needtoreject', 'Need To Reject '),
		],'Report Type')
	
	def create_report(self, cr, uid, ids, context=None):
		
		data = self.read(cr, uid, ids, context=context)[0]
		
		datas = {
			'ids': [],
			'model': 'leave.wizard',
			'form': data
			}
		return self.pool['report'].get_action(cr, uid,[],
			'hr_holidays_aspire.last_month_leave_summary_report_view', 
			data=datas, context=context)

	@api.constrains('endDate')
	def _check_something(self):
		_logger.info("============================call constrains")
		for record in self:
			if record.startDate > record.endDate:
				raise ValidationError("Enter correct endDate: %s" % record.endDate)
