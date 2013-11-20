/*
 * Override Session.session_logout method when auth_lemonldap is enabled to call a specific url instead of doing a RPC call
 */
openerp.auth_lemonldap = function(instance){
    
    
    instance.session.on('module_loaded', this, function(){
        var icp = new instance.web.Model('ir.config_parameter');
        
        icp.query().filter([['key', '=', 'auth_lemonldap.enabled']]).first().done(function(data){
            if(/true/i.test(data.value)){
                // auth_lemonldap enabled 
                instance.web.Session.prototype.session_logout = function(){
                    document.location = '/lemonldap_logout';
                    return $.Deferred();
                };
            }
        });
    });
    
};
