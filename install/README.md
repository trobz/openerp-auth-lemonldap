LemonLDAP - OpenERP Setup
=========================

## LemonLDAP server

### Setup (see http://lemonldap-ng.org/documentation/1.3/installdeb)

- download and extract http://forge.ow2.org/project/download.php?group_id=274&file_id=19536 (tested with lemonLDAP 1.3.1)
- execute `sudo dpkg -i *`
- if there's missing dependencies, execute `sudo apt-get -f install` and redo the previous step
- change the default LemonLDAP 'example.com' domain by your own, with this command:   

`sed -i 's/example\.com/YOUR-DOMAIN.HERE/g' /etc/lemonldap-ng/* /var/lib/lemonldap-ng/conf/lmConf-1 /var/lib/lemonldap-ng/test/index.pl`

- enable LemonLDAP virtual host configuration:

```
a2ensite handler-apache2.conf
a2ensite portal-apache2.conf
a2ensite manager-apache2.conf
a2ensite test-apache2.conf
```

- enable Apache `mod_perl`
- restart Apache server

### Configuration

#### Auto installation

Use the interactive script `./install/setup.sh` to:
- install all dependencies
- setup the LemonLDAP Database
- sync OpenERP user with LemonLDAP Database
- configure LemonLDAP (same as described in [LemonLDAP Manager web interface](#lemonldap-manager-web-interface) section)

#### Command line

- setup the authentication database by executing `./install/setup.sh`  
- enable apache `mod_proxy` and `mod_proxy_http`
- add a virtual host configuration for your OpenERP application to Apache:

```
<VirtualHost *:80>
    ServerName protected.openerp.com
    ServerAlias protected2.openerp.com
     	
	# SSO protection
    PerlHeaderParserHandler My::Package
 
 	# Proxy to your openerp application
	ProxyPass / http://openerp.domain/
</VirtualHost>
```

- restart Apache server

#### LemonLDAP Manager web interface

Note: If you used `./install/setup.sh`, follow these steps only to check if the configuration is ok.

- configure the authentication, users and password modules to "Database"
- in each Database settings section, set:

```
dbiAuthChain:        dbi:mysql:database=lemon_user_auth;host=localhost
dbiAuthLoginCol:     username
dbiAuthPassword:     <mysql_lemonldap_password>
dbiAuthPasswordCol:  password
dbiAuthPasswordHash: SHA1
dbiAuthTable:        lemon_auth
dbiAuthUser:         lemonldap
dbiAuthnLevel:       2
dbiPasswordMailCol:  email
dbiUserChain:        dbi:mysql:database=lemon_user_auth;host=localhost
dbiUserPassword:     <mysql_lemonldap_password>
dbiUserTable:        lemon_user
dbiUserUser:         lemonldap
```

- in `Cookies` section, enable `Multiple domains` support
- in `Variables > Exported Variables` section, add:   

```
oe_database: oe_database
oe_id:       oe_id
username:    username
```

- in `Virtual Host` section, add your virtual hosts (ie: protected.openerp.com)
- in `Virtual Host > Rules`, for each OpenERP virtual hosts, add 2 rules:
  
```
comment:    logout
expression: ^/lemonldap_logout
rule:       logout_app_sso http://<lemonldap.portal.url>
   
comment:    default
rule:       accept
```

- in `Virtual Host > HTTP Headers`, for each OpenERP virtual hosts, add:   

```
OpenERP-Database:   $oe_database
OpenERP-Secret-Key: "<your_secret_key>" // don't forget the double quotes
OpenERP-User-Id:    $oe_id
OpenERP-User-Login: $username
```


## OpenERP server

### Configure

- install `auth_lemonldap` module
- go to `Settings > Configuration > General Settings` to configure the module:
  - enable the module   
  - set the secret key shared with LemonLDAP Header Parameters (`OpenERP-Secret-Key`)
  - list of Virtual Hosts Proxy, separated by commas (ie. protected.openerp.com),   
    these values are compared with `X-Forwarded-Host` header parameter.

### Notes

- you can disable the module in OpenERP database directly, by changing `auth_lemonldap.enabled` key to `False` in `ir_config_parameter`