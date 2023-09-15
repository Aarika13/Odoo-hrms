# -*- coding: utf-8 -*-
from odoo import models, fields


class ResCompany(models.Model):
    _name = 'res.company'
    _inherit = 'res.company'

    w1mon = fields.Boolean()
    w2mon = fields.Boolean()
    w3mon = fields.Boolean()
    w4mon = fields.Boolean()
    w5mon = fields.Boolean()
    w6mon = fields.Boolean()

    w1tue = fields.Boolean()
    w2tue = fields.Boolean()
    w3tue = fields.Boolean()
    w4tue = fields.Boolean()
    w5tue = fields.Boolean()
    w6tue = fields.Boolean()

    w1wed = fields.Boolean()
    w2wed = fields.Boolean()
    w3wed = fields.Boolean()
    w4wed = fields.Boolean()
    w5wed = fields.Boolean()
    w6wed = fields.Boolean()

    w1thu = fields.Boolean()
    w2thu = fields.Boolean()
    w3thu = fields.Boolean()
    w4thu = fields.Boolean()
    w5thu = fields.Boolean()
    w6thu = fields.Boolean()

    w1fri = fields.Boolean()
    w2fri = fields.Boolean()
    w3fri = fields.Boolean()
    w4fri = fields.Boolean()
    w5fri = fields.Boolean()
    w6fri = fields.Boolean()

    w1sat = fields.Boolean()
    w2sat = fields.Boolean()
    w3sat = fields.Boolean()
    w4sat = fields.Boolean()
    w5sat = fields.Boolean()
    w6sat = fields.Boolean()

    w1sun = fields.Boolean()
    w2sun = fields.Boolean()
    w3sun = fields.Boolean()
    w4sun = fields.Boolean()
    w5sun = fields.Boolean()
    w6sun = fields.Boolean()
