import odoorpc

odoo_9 = odoorpc.ODOO('localhost', port=8090)
odoo_9.login('odoo9', 'admin', 'admin')

odoo_15 = odoorpc.ODOO('localhost', port=8069)
odoo_15.login('odoopy', 'admin', 'admin')