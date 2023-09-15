import logging
from odoo import models, fields, api, _
# from datetime import datetime, timedelta
# from dateutil.relativedelta import relativedelta

class SlideChannel(models.Model):
    
    _inherit = 'slide.channel'


    def action_publish_all_content(self):
        if self.slide_ids:
            for content in self.slide_ids:
                if not content.is_published:
                    content.write({
                        'is_published':True,
                        'is_preview':True
                        })
