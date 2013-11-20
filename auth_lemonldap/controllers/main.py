# -*- encoding: utf-8 -*-

from openerp.addons.web import http
from openerp.addons.web.controllers.main import Home, db_monodb, login_and_redirect

from openerp.modules.registry import RegistryManager
from openerp import SUPERUSER_ID

from werkzeug.wrappers import Response
import re

import logging
log = logging.getLogger(__name__)

class SSO(Home):
    
    def get_sso_config(self, req, dbname):
        """ 
        Retrieve the module config (which features are enabled) for the SSO LemonLDAP auto connection
        """
        registry = RegistryManager.get(dbname)
        
        config = {
            'enabled': False
        }
        
        with registry.cursor() as cr:
            icp = registry.get('ir.config_parameter')
            
            forwarded = icp.get_param(cr, SUPERUSER_ID, 'auth_lemonldap.forwarded')
            log.debug('icp forwarded: %s, type: %s', forwarded, type(forwarded))
            forwarded = re.split(r" *, *", forwarded) if type(forwarded) == unicode else []
            
            config = {
                'enabled': icp.get_param(cr, SUPERUSER_ID, 'auth_lemonldap.enabled') == 'True',
                'lemon_secret': icp.get_param(cr, SUPERUSER_ID, 'auth_lemonldap.secret'),
                'forwarded': forwarded,
            }
        
        return config
    
    def get_lemon_params(self, req):
        """
        Retrieve lemon header parameters
        """
        headers = req.httprequest.headers
        return {
            'forwarded': headers.get('X-Forwarded-Host'),
            'db': headers.get('OpenERP-Database') if type(headers.get('OpenERP-Database')) == str else None,
            'user_id': headers.get('OpenERP-User-Id'),
            'username': headers.get('OpenERP-User-Login'),
            'secret': headers.get('OpenERP-Secret-Key')
        }
    
    def get_current_db(self, req, db):
        """
        Retrieve the database to use, from Lemon header, URI parameter or the default one
        """
        db = db if db and len(db) > 0 else db_monodb(req)
        if not db:
            raise Exception('Can not found a database to use...')
        return db
    
    def get_current_session(self, req):
        """
        Get the current session if any
        """
        # FIXME: don't ask me why, but the req.session is not correct, and to get the real one, we have to check in the cookie and clean up 
        #        the dirty key, thanks OpenERP... 
        cookie = req.httprequest.cookies.get("instance0|session_id") or None
        session_id = cookie.replace("%22","") if cookie else None
        return req.httprequest.session.get(session_id) if session_id else None

    
    @http.httprequest
    def index(self, req, s_action=None, db=None, **kw):
        """
        If LemonLDAP module is activated, auto login the user and keep him connected automatically
        Warning: Security is not managed on OpenERP anymore, OpenERP has to be behind a proxy and not
        accessible from outside !
        """
        
        # handle 500 error manually, to retrieve error as a string, not a json object
        try:
            lemon_params = self.get_lemon_params(req)
            
            log.debug('Lemon > db: %s, user_id: %s, username: %s, secret: %s', lemon_params['db'], lemon_params['user_id'], lemon_params['username'], lemon_params['secret'])
                
            db = self.get_current_db(req, lemon_params['db'] or db)
            config = self.get_sso_config(req, db) 
            
            # only process if the module is activated
            if config['enabled']:
                
                log.debug('forwarded > header: %s, config: %s', lemon_params['forwarded'], config['forwarded'])
                
                # some basic security check to identify LemonLDAP and the proxy
                if lemon_params['forwarded'] not in config['forwarded']:
                    raise Exception('OpenERP is not behind a proxy or the forwarded domain is wrong') 
                
                if config['lemon_secret'] != lemon_params['secret']:
                    raise Exception('LemonLDAP secret is not the same than secret configured on OpenERP !') 
                
                log.debug("db_monodb(req): %s, db: %s", db_monodb(req), db)
                
                session = self.get_current_session(req)
                
                if db_monodb(req) != db:
                    log.info('force re authenticate user %s', lemon_params['username'])
                    
                    # force the db retrieved from request header
                    req.params.update({'db': db })
                    url = '/?db=%s' % db
                    
                    # login with a fake password, the security check has been disabled on res.users model
                    return login_and_redirect(req, db, lemon_params['username'], 'nopassword', redirect_url=url)
                 
                if not session or str(session._uid) != lemon_params['user_id']:
                    log.info('auto-authenticate user %s', lemon_params['username'])
                    # login with a fake password, the security check has been disabled on res.users model
                    return login_and_redirect(req, db, lemon_params['username'], 'nopassword')
                
                log.info('user %s already authenticated', lemon_params['username'])
        except Exception as e:
            body = "<h1>OpenERP - LemonLDAP Authorization Error</h1><p>%s</p>" % str(e)
            return Response(body, status=500, headers=[('Content-Type', 'text/html'), ('Content-Length', len(body))])
            
        return super(SSO, self).index(req, s_action, db, **kw)
 
 
    @http.httprequest
    def lemonldap_logout(self, req, s_action=None, db=None, **kw):
        """
        Custom page used to logout user from lemonldap
        """
        body = "<h1>OpenERP - LemonLDAP Logout Page</h1><p>You will be redirected to LemonLDAP portail...</p>"
        return Response(body, status=200, headers=[('Content-Type', 'text/html'), ('Content-Length', len(body))])
        
 
    @http.httprequest
    def login(self, req, db, login, key):
        """
        If LemonLDAP module is activated, this method should never be called, so raise an exception in this case
        """
        # handle 500 error manually, to retrieve error as a string, not a json object
        try:
            lemon_params = self.get_lemon_params(req)
            db = self.get_current_db(req, lemon_params['db'] or db)
            config = self.get_sso_config(req, db) 
            
            # only process if the module is activated
            if config['enabled']:
                raise Exception('Login is managed automatically with LemonLDAP, this method should never be called !')
        
        except Exception as e:
            body = "<h1>OpenERP - LemonLDAP Authorization Error</h1><p>%s</p>" % str(e)
            return Response(body, status=500, headers=[('Content-Type', 'text/html'), ('Content-Length', len(body))])
            
        return super(SSO, self).login(req, db, login, key)
