# -*- coding: utf-8 -*-

from openerp.osv import osv, fields
from openerp.tools.safe_eval import safe_eval

class base_config_settings(osv.TransientModel):
    _inherit = 'base.config.settings'

    _columns = {
        'auth_lemonldap_enabled': fields.boolean('Enable LemonLDAP authorization',
            help="""
This will disabled the OpenERP authentication module and use LemonLDAP SSO system instead. 
Caution: your have to prevent OpenERP to be accessible without going through LemonLDAP Apache Reverse Proxy.
"""),
        'auth_lemonldap_secret': fields.char('Secret Key shared with LemonLDAP',
            help="The key set on LemonLDAP Virtual Host Header configuration (OpenERP-Secret-Key)."),
        'auth_lemonldap_forwarded': fields.char('LemonLDAP Proxy Hostname, separate by commas',
            help="Proxy Hostname set as LemonLDAP Virtual Host, these values will be compared with 'X-Forwarded-Host' header parameter"),
    }

    def get_default_auth_lemonldap_enabled(self, cr, uid, fields, context=None):
        icp = self.pool.get('ir.config_parameter')
        return {
            'auth_lemonldap_enabled': safe_eval(icp.get_param(cr, uid, 'auth_lemonldap.enabled', 'False')),
            'auth_lemonldap_secret': icp.get_param(cr, uid, 'auth_lemonldap.secret', ''),
            'auth_lemonldap_forwarded': icp.get_param(cr, uid, 'auth_lemonldap.forwarded', 'exemple.com'),
        }

    def set_auth_lemonldap_enabled(self, cr, uid, ids, context=None):
        
        config = self.browse(cr, uid, ids[0], context=context)
        icp = self.pool.get('ir.config_parameter')
        
        icp.set_param(cr, uid, 'auth_lemonldap.enabled', repr(config.auth_lemonldap_enabled))
        icp.set_param(cr, uid, 'auth_lemonldap.secret', config.auth_lemonldap_secret)
        icp.set_param(cr, uid, 'auth_lemonldap.forwarded', config.auth_lemonldap_forwarded)