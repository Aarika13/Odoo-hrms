from datetime import datetime,date ,timedelta
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
import logging
from odoo import fields, osv
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)

DATE_RANGE_FUNCTION = {
    'day': lambda interval: timedelta(days=interval),
    False: lambda interval: timedelta(0),
}


def get_datetime(date_str):
    """ Return a datetime from a date string or a datetime string"""
    # complete date time if date_str contains only a date
    if ' ' not in str(date_str):
        date_str = str(date_str) + " 00:00:00"
    return (datetime.strptime(date_str, DEFAULT_SERVER_DATETIME_FORMAT)).date()


# Notifier Model
class NotifierActionRule(models.Model):
    _name = 'notifier.action'
    _description = 'Notifier Rules'

    name = fields.Char('Notifier Name')  # required=True
    model_id = fields.Many2one('ir.model', 'Related Document Model', domain=[('transient', '=', False)])  # req=True
    model = fields.Char(string='Model')
    create_date = fields.Datetime('Create Date', readonly=1)
    active = fields.Boolean('Active', help="When unchecked, the rule is hidden and will not beexecuted.",
                            default=True)
    kind = fields.Selection(
        [('on_time', 'Based on Timed Condition')],
        string='When to Run', default='on_time', readonly=True)
    trg_date_id = fields.Many2one('ir.model.fields', string='Trigger Date', help="When should the condition be "
                                                                                 "triggered.If present, will be "
                                                                                 "checked by the scheduler."
                                                                                 "If empty, will be checked"
                                                                                 "at creation and update.",
                                  domain="[('model_id', '=', model_id), ('ttype', 'in', ('date', 'datetime'))]")
    trg_date_range = fields.Integer('Delay after trigger date', help="Delay after the trigger date.You can put a "
                                                                     "negative number if you need a delay before the "
                                                                     "trigger date, like sending a reminder 15 "
                                                                     "minutes before a meeting.")
    trg_date_range_type = fields.Selection([('day', 'Days')], 'Delay type', readonly=True, default='day')
    filter_id = fields.Many2one('ir.filters', string='Filter', ondelete='restrict',
                                domain="[('model_id', '=', model_id.model)]",
                                help="If present, this condition must be satisfied before executing the action rule.")
    template_id = fields.Many2one('mail.template', 'Email Notification')  # required=True
    last_run = fields.Datetime('Last Run', readonly=1, copy=False)

    # On_cahnge get model id in model field
    @api.onchange('model_id')
    def onchange_model_id(self):
        data = {'model': False, 'filter_pre_id': False, 'filter_id': False}
        if self.model_id:
            model = self.pool.get('ir.model').browse(self.model_id)
            data.update({'model': model.model})
        return {'value': data}

    def get_datetime_2_5_10_year_complation(self, date_str, action):

        if action == self.env.ref('aspl_hr_employee.2_year_complete_notifier'):
            record_dt = date_str + relativedelta(years=2)
        elif action == self.env.ref('aspl_hr_employee.5_year_complete_notifier'):
            record_dt = date_str + relativedelta(years=5)
        else:
            record_dt = date_str + relativedelta(years=10)

        if ' ' not in str(record_dt):
            record_dt_str = str(record_dt) + " 00:00:00"
        else:
            record_dt_str = record_dt

        return (datetime.strptime(record_dt_str, DEFAULT_SERVER_DATETIME_FORMAT)).date()

    # Calculate dealy of day from define date
    def _check_delay(self, action, record_dt):
        delay = DATE_RANGE_FUNCTION[action.trg_date_range_type](action.trg_date_range)
        action_dt = get_datetime(record_dt) + delay
        return action_dt

    # Calculate dealy for 2 ,5 ,10 year
    def _check_delay_2_5_10_year_complation(self, action, record_dt):
        delay = DATE_RANGE_FUNCTION[action.trg_date_range_type](action.trg_date_range)
        action_dt = self.get_datetime_2_5_10_year_complation(record_dt, action) + delay
        return action_dt

    # This function call by schedular and send mail notification to sender
    def check(self):
        context = {}
        # retrieve all the action rules to run based on a timed condition
        action_ids = self.search([('active', '=', True)])
        for action in action_ids:       #self.browse(action_ids)
            now = (datetime.now()).strftime('%Y-%m-%d')
            now = get_datetime(now)

            # retrieve all the records that satisfy the action's condition
            model = self.env[action.model_id.model]  # Create modle object define in notifier action
            # Define domain for filter
            domain = []
            if action.model_id.model == 'hr.employee':
                domain = [('with_organization', '=', True)]
            # Define context for filter
            ctx = dict(context)

            if action.filter_id:
                # domain = eval(action.filter_id.domain)
                domain = eval(action.filter_id.name)
                ctx.update(eval(action.filter_id.context))

                if 'lang' not in ctx:
                    # Filters might be language-sensitive, attempt to reuse creator lang
                    # as we are usually running this as super-user in background
                    [filter_meta] = action.filter_id.get_metadata()
                    user_id = filter_meta['write_uid'] and filter_meta['write_uid'][0] or filter_meta['create_uid'][0]
                    ctx['lang'] = self.env['res.users'].browse(user_id).lang

            # Get all records based on filter
            record_ids = model.search(domain)

            # determine when action should occur for the records
            date_field = action.trg_date_id.name

            get_record_dt = lambda record: record[date_field]

            # Process action on the records that should be executed
            for record in model.browse(record_ids):
                record_dt = get_record_dt(record.id)

                if not record_dt:
                    continue

                # check for 2,5,10 year .....
                year_complete_2 = self.env.ref('aspl_hr_employee.2_year_complete_notifier')
                year_complete_5 = self.env.ref('aspl_hr_employee.5_year_complete_notifier')
                year_complete_10 = self.env.ref('aspl_hr_employee.10_year_complete_notifier')

                if action in (year_complete_2, year_complete_5, year_complete_10):
                    action_dt = self._check_delay_2_5_10_year_complation(action, record_dt)
                    action_actual_dt = self.get_datetime_2_5_10_year_complation(record_dt , action)
                    if action.trg_date_range < 0:
                        if action_dt <= now and now <= action_actual_dt:
                            try:
                                context = dict(context or {}, action=True)
                                self._process(action,record.id,action_actual_dt)
                            except Exception:
                                _logger.error('Something is wrong')

                    elif action.trg_date_range > 0:
                        if action_actual_dt <= now and now <= action_dt:
                            try:
                                context = dict(context or {}, action=True)
                                self._process(action, [record.id] , action_actual_dt)
                            except Exception:
                                _logger.error('Something is  wrong')
                if action == self.env.ref('aspl_hr_employee.birth_date_notifier'):
                    if action.trg_date_range == 0:
                        if (record_dt.month, record_dt.day) == (now.month, now.day) and record.id.company_id.id in [1, 2]:
                            try:
                                context = dict(context or {}, action=True)
                                self._process(action,record.id,record_dt)
                            except Exception:
                                _logger.error('Something is wrong')
                if ( action == self.env.ref('aspl_hr_employee.probation_end_date') or action == self.env.ref('aspl_hr_employee.Training_end_date') or action == self.env.ref('aspl_hr_employee.appraisal_date') ):
                    action_dt = self._check_delay(action,record_dt)
                    action_actual_dt = get_datetime(record_dt)
                    if action.trg_date_range < 0:
                        if action_dt <= now and now <= action_actual_dt:
                            try:
                                context = dict(context or {}, action=True)
                                self._process(action,record.id,action_actual_dt)
                            except Exception:
                                _logger.error('Something is wrong')

                    elif action.trg_date_range > 0:
                        if action_actual_dt <= now and now <= action_dt:
                            try:
                                context = dict(context or {}, action=True)
                                self._process(action, [record.id],action_actual_dt)
                            except Exception:
                                _logger.error('Something is  wrong')
            action.write({'last_run': now.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
        return True

    # Send mail to records
    def _process(self, action, record_ids , action_actual_dt):
        model = self.env[action.model_id.model]
        # Modify record send mail to user server actions
        try:
            if action.template_id:
                for record in model.browse(record_ids.id):
                    context = {
                        'action_dt': action_actual_dt,
                    }
                    template = self.env['mail.template'].browse(action.template_id.id)
                    # mail_id = template.send_mail(record.id,force_send = True)
                    mail_id = template.with_context(context).send_mail(record.id,force_send = True)
                    # mail_id = self.pool.get('mail.template').send_mail(action.template_id.id, record.id,
                    #                                                    force_send=True)
            else:
                _logger.error('Email templates not set')
        except ValueError:
            pass
        # except Exception, e:
        #     _logger.error('Email Not Send')
        #     _logger.error(str(e))
        return True
