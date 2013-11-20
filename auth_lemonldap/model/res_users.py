from openerp import tools
from openerp.tools.safe_eval import safe_eval
from openerp.osv import fields, osv

import logging
log = logging.getLogger(__name__)

class users(osv.osv):
    _inherit = "res.users"

    def check_credentials(self, cr, uid, password):
        """
        If the module is enabled, the authentication is delagated to LemonLDAP, so no security check on OpenERP side anymore...
        """
        icp = self.pool.get('ir.config_parameter')
        enabled = safe_eval(icp.get_param(cr, uid, 'auth_lemonldap.enabled', 'False'))
        
        if not enabled:
            log.info('auth_lemonldap disabled, follow default security check')
            return super(users, self).check_credentials(cr, uid, password)
        
        log.info('auth_lemonldap enabled, no security check') 