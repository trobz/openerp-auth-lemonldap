# -*- coding: utf-8 -*-
{
    'name': 'LemonLDAP SSO Auth',
    'version': '1.0',
    'category': 'Authentication',
    'description': """
Authentication support for LemonLDAP
    """,
    'author': 'Trobz',
    'website': 'http://trobz.github.io/openerp-auth-lemonldap/',
    
    'depends': [
        'base_setup'
    ],
    
    'data': [
        # default configuration
        'config/ir_config_parameter_default.xml',
        
        # extend general settings
        'config/res_config.xml',
         
    ],
    
    'js': [
         'static/src/session.js'
    ],
    
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
