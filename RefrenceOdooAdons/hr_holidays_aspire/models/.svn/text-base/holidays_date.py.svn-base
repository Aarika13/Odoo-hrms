# Inherit hr.holiday module
import logging
import datetime
import calendar
import math
import time
from operator import attrgetter
from openerp.exceptions import Warning
from openerp import tools
from openerp.osv import fields, osv
from openerp.tools.translate import _
from dateutil.relativedelta import relativedelta
from dateutil import parser

_logger = logging.getLogger(__name__)


class hr_holidays(osv.osv):
    _name = "hr.holidays.detail"
    _description = "Holidays Detail"
    
    _columns = {
        'holiday_status_id' :fields.many2one('hr.holidays.status','Holiday'),
        'name': fields.char('Holiday Type', default="Holiday Leave", readonly=True),  
        'leave_status' : fields.char('Holiday Status',default = 'Holiday -'),
        'holiday_from':fields.date('From Date',required=True),
        'des':fields.char('Description', required = True),
        'color_name': fields.selection([('red', 'Red'),('blue','Blue'), ('lightgreen', 'Light Green'), ('lightblue','Light Blue')],'Color in Report'),
    }

    _defaults = {
        'color_name': 'red',
    }