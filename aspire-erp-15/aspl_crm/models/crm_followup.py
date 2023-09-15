from odoo import models, fields, api, _
from datetime import date
from dateutil.relativedelta import relativedelta
import logging
import html

_logger = logging.getLogger(__name__)

class CrmFollowup(models.Model):
    _name = "crm.followup"
    _description = "Crm Followup"
    _rec_name = "name"

    name = fields.Char(string="Followup Name")
    frequency_days = fields.Integer(string="Frequency Days")
    subject = fields.Text(string="Email Subject")
    add_context = fields.Html(string="Add Context",
          default = '''
                        # Available variables : </br>
                           ******************* </br>
                        # {{name}} : crm.lead Client Name</br>
                        # {{company}} : crm.lead Company Name </br>
                        # {{website}} : crm.lead Website </br>
                        
                        </br></br>
                        # Note: returned value have to be set in the variable From CRM Lead.
                        ''')

    def followup_mail_sender(self):
        crm_lead_ids = self.env['crm.lead'].sudo().search([
            ('followup_id' , '!=' , False) ,
            ('followup_start_date' , '!=' , False),
            ('user_id' , '!=' , False),
            ('followup_replay_date' , '=' , False),
        ])

        for crm_obj in crm_lead_ids:
            if not crm_obj.last_followup_send_date :
                if crm_obj.followup_start_date == date.today():

                    search_words = ["{{name}}", "{{ name }}", "{name}", "{ name }", "{{company}}", "{{ company }}",
                                    "{company}", "{ company }", "{{website}}", "{{ website }}", "{website}",
                                    "{ website }"]
                    body_content = crm_obj.followup_id.add_context
                    for word in search_words:
                        if word == "{{name}}" or word == "{{ name }}" or word == "{name}" or word == "{ name }":
                            if crm_obj.contact_name:
                                body_content = body_content.replace(word, crm_obj.contact_name)
                            else:
                                body_content = body_content.replace(word, '')
                        elif word == "{{company}}" or word == "{{ company }}" or word == "{company}" or word == "{ company }":
                            if crm_obj.partner_name:
                                body_content = body_content.replace(word, crm_obj.partner_name)
                            else:
                                body_content = body_content.replace(word, '')
                        elif word == "{{website}}" or word == "{{ website }}" or word == "{website}" or word == "{ website }":
                            if crm_obj.website:
                                body_content = body_content.replace(word, f'<a href="{crm_obj.website}">{crm_obj.website}</a>')
                            else:
                                body_content = body_content.replace(word, '')
                    body_content = html.unescape(body_content)
                    try:
                        post_params = {
                            'message_type': 'comment',
                            'subtype_id': 1,
                            'email_layout_xmlid': 'mail.mail_notification_paynow',
                            'subject': crm_obj.followup_id.subject,
                            'body': body_content,
                            'partner_ids': [crm_obj.partner_id.id],
                            'author_id': self.env.user.id,
                            'email_from': crm_obj.user_id.login,
                            'email_to': crm_obj.partner_id.email,
                            # 'email_from': '"Purav Gandhi" <pgandhi@aspiresoftserv.com>',
                            # 'reply_to': 'aspiresolutionsodoo@gmail.com',
                        }
                        ctx = dict(self.env.context)
                        ctx.update({'from_lead_followup': True, 'mail_notify_force_send': True})
                        crm_obj.with_context(ctx).message_post(**post_params)

                        crm_obj.write({
                            'last_followup_send_date': date.today(),
                        })
                        _logger.info('Mail Send successfully to Customer :  %s', crm_obj.partner_id.name)
                    except Exception:
                        _logger.error('Something is wrong')
            else :
                if (( crm_obj.last_followup_send_date + relativedelta( days = crm_obj.followup_id.frequency_days ) ) == date.today()):

                    search_words = ["{{name}}", "{{ name }}", "{name}", "{ name }", "{{company}}", "{{ company }}",
                                    "{company}", "{ company }", "{{website}}", "{{ website }}", "{website}",
                                    "{ website }"]
                    body_content = crm_obj.followup_id.add_context
                    for word in search_words:
                        if word == "{{name}}" or word == "{{ name }}" or word == "{name}" or word == "{ name }":
                            if crm_obj.contact_name:
                                body_content = body_content.replace(word, crm_obj.contact_name)
                            else:
                                body_content = body_content.replace(word, '')
                        elif word == "{{company}}" or word == "{{ company }}" or word == "{company}" or word == "{ company }":
                            if crm_obj.partner_name:
                                body_content = body_content.replace(word, crm_obj.partner_name)
                            else:
                                body_content = body_content.replace(word, '')
                        elif word == "{{website}}" or word == "{{ website }}" or word == "{website}" or word == "{ website }":
                            if crm_obj.website:
                                body_content = body_content.replace(word, f'<a href="{crm_obj.website}">{crm_obj.website}</a>')
                            else:
                                body_content = body_content.replace(word, '')
                    body_content = html.unescape(body_content)
                    try:
                        post_params = {
                            'message_type': 'comment',
                            'subtype_id': 1,
                            'email_layout_xmlid': 'mail.mail_notification_paynow',
                            'subject': crm_obj.followup_id.subject,
                            'body': body_content,
                            'partner_ids': [crm_obj.partner_id.id],
                            'author_id': self.env.user.id,
                            'email_from': crm_obj.user_id.login,
                            'email_to': crm_obj.partner_id.email,
                            # 'email_from': '"Purav Gandhi" <pgandhi@aspiresoftserv.com>',
                            # 'reply_to': 'aspiresolutionsodoo@gmail.com',
                        }
                        ctx = dict(self.env.context)
                        ctx.update({'from_lead_followup': True, 'mail_notify_force_send': True})
                        crm_obj.with_context(ctx).message_post(**post_params)

                        last_date = crm_obj.last_followup_send_date + relativedelta( days = crm_obj.followup_id.frequency_days )
                        crm_obj.write({
                            'last_followup_send_date': last_date,
                        })
                        _logger.info('Mail Send successfully to Customer :  %s', crm_obj.partner_id.name)
                    except Exception:
                        _logger.error('Something is wrong')



        # ********** FOR TESTING ********** #
        # for crm_obj in crm_lead_ids:
        #     if crm_obj.followup_start_date == date.today():
        #
        #         search_words = ["{{name}}","{{ name }}","{name}","{ name }","{{company}}","{{ company }}","{company}","{ company }","{{website}}","{{ website }}","{website}","{ website }"]
        #         body_content = crm_obj.followup_id.add_context
        #         for word in search_words:
        #             if word == "{{name}}" or word == "{{ name }}" or word == "{name}" or word == "{ name }" :
        #                 if crm_obj.contact_name:
        #                     body_content = body_content.replace(word, crm_obj.contact_name)
        #                 else:
        #                     body_content = body_content.replace(word, '')
        #             elif word == "{{company}}" or word == "{{ company }}" or word == "{company}" or word == "{ company }" :
        #                 if crm_obj.partner_name:
        #                     body_content = body_content.replace(word, crm_obj.partner_name)
        #                 else:
        #                     body_content = body_content.replace(word, '')
        #             elif word == "{{website}}" or word == "{{ website }}" or word == "{website}" or word == "{ website }" :
        #                 if crm_obj.partner_name:
        #                     body_content = body_content.replace(word, f'<a href="{crm_obj.website}">{crm_obj.website}</a>')
        #                 else:
        #                     body_content = body_content.replace(word, '')
        #         body_content = html.unescape(body_content)
        #         try:
        #             post_params = {
        #                 'message_type': 'comment',
        #                 'subtype_id': 1,
        #                 'email_layout_xmlid': 'mail.mail_notification_paynow',
        #                 'subject': crm_obj.followup_id.subject,
        #                 'body': body_content,
        #                 'partner_ids': [crm_obj.partner_id.id],
        #                 'author_id': self.env.user.id,
        #                 'email_from': crm_obj.user_id.login,
        #                 'email_to': crm_obj.partner_id.email,
        #                 # 'email_from': '"Purav Gandhi" <pgandhi@aspiresoftserv.com>',
        #                 # 'reply_to': 'aspiresolutionsodoo@gmail.com',
        #             }
        #             ctx = dict(self.env.context)
        #             ctx.update({'from_lead_followup': True, 'mail_notify_force_send': True})
        #             crm_obj.with_context(ctx).message_post(**post_params)
        #
        #             crm_obj.write({
        #                 'last_followup_send_date': date.today(),
        #             })
        #             _logger.info('Mail Send successfully to Customer :  %s', crm_obj.partner_id.name)
        #         except Exception:
        #             _logger.error('Something is wrong')
