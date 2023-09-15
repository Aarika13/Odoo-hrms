# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID, _


def pre_init_hook(cr):
    try:
        sql = "UPDATE ir_module_module SET website = '%s' WHERE license like '%s' and website <> ''" % (
        'https://www.aspiresoftware.in', 'OEEL%')
        cr.execute(sql)
        cr.commit()
    except Exception as e:
        pass


def post_init_hook(cr, registry):
    # a = check_module_installed(cr, ['app_web_superbar','aaaaa'])
    pass
    # cr.execute("")


def uninstall_hook(cr, registry):
    pass


def check_module_installed(cr, modules):
    env = api.Environment(cr, SUPERUSER_ID, {})
    installed = False
    m = env['ir.module.module'].sudo().search(
        [('name', 'in', modules), ('state', 'in', ['installed', 'to install', 'to upgrade'])])
    if len(m) == len(modules):
        installed = True
    return len(m)
