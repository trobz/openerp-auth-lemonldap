#!/usr/bin/env bash

# 
# Setup LemonLDAP to use authDBI authentication, user and password modules.
# Use a MySQL database, better support for the only weak password encryption supported by 
# LemonLDAP::authDBI..
#

echo "
=========================
  Install dependancies 
=========================
"

# install prerequisites
sudo apt-get install mysql-server libdbd-mysql-perl python-mysqldb


echo "
=========================
   Setup Auth Database 
=========================
"

echo "Enter MySQL root password:"
read root_pass

echo "Define a MySQL lemonldap password:"
read lemonldap_pass


# setup auth database
sed="s/LEMONLDAP_PASSWORD/$lemonldap_pass/g"
sql=`cat lemon_user_auth.sql | sed $sed`

echo "$sql" | mysql -u root -p$root_pass

echo "> LemonLDAP Database created, accessible with lemonldap/$lemonldap_pass"

# import users

echo "
=========================
Import user from OpenERP 
=========================
"

echo "Enter the OpenERP XML-RPC Host:"
read host

echo "Enter the OpenERP XML-RPC Port (ig. 8069):"
read port

echo "Enter an OpenERP database name:"
read database

echo "Enter an OpenERP username:"
read username

echo "Enter an OpenERP password:"
read password

python sync-user.py $host $port $database $username $password --mysql-password $lemonldap_pass

echo "> all user sync between OpenERP and LemonLDAP Database"

echo "
=========================
 LemonLDAP Configuration 
=========================
"

function lemonldap_conf {
    sudo /usr/share/lemonldap-ng/bin/lemonldap-ng-cli $@ > /dev/null
} 

lemonldap_conf set authentication "DBI"
lemonldap_conf set userDB "DBI"
lemonldap_conf set passwordDB "DBI"

lemonldap_conf set dbiAuthChain "dbi:mysql:database=lemon_user_auth;host=localhost"
lemonldap_conf set dbiAuthLoginCol "username"
lemonldap_conf set dbiAuthPassword "$lemonldap_pass"
lemonldap_conf set dbiAuthPasswordCol "password"
lemonldap_conf set dbiAuthPasswordHash "SHA1"
lemonldap_conf set dbiAuthTable "lemon_auth"
lemonldap_conf set dbiAuthUser "lemonldap"
lemonldap_conf set dbiAuthnLevel 2
lemonldap_conf set dbiPasswordMailCol "email"
lemonldap_conf set dbiUserChain "dbi:mysql:database=lemon_user_auth;host=localhost"
lemonldap_conf set dbiUserPassword "$lemonldap_pass"
lemonldap_conf set dbiUserTable "lemon_user"
lemonldap_conf set dbiUserUser "lemonldap"

echo '> LemonLDAP Authentication modules configured to DBI'

lemonldap_conf export-var oe_database "oe_database"
lemonldap_conf export-var oe_id "oe_id"
lemonldap_conf export-var username "username"

echo '> LemonLDAP exported vars configured'


echo "Enter the URL to LemonLDAP portal (ig. http://auth.lemon.com/):"
read lemon_portal

echo "Enter the Secret Key shared between LemonLDAP and OpenERP:"
read lemon_secret

echo "Enter OpenERP vhost domain to protect, separated by commas (ig. inst1.openerp.com,inst2.openerp.com):"
read vhosts

while IFS=';' read -ra ARR; do
    for vhost in "${ARR[@]}"; do
        lemonldap_conf vhost-add $vhost       

        lemonldap_conf rules-set $vhost "^/lemonldap_logout" "logout_app_sso $lemon_portal"
        lemonldap_conf rules-set $vhost "default" "accept"
    
        lemonldap_conf export-header $vhost "OpenERP-Database" '$oe_database'
        lemonldap_conf export-header $vhost "OpenERP-Secret-Key" '"'"$lemon_secret"'"'
        lemonldap_conf export-header $vhost "OpenERP-User-Id" '$oe_id'
        lemonldap_conf export-header $vhost "OpenERP-User-Login" '$username'
    
        echo "$vhost configured" 
    done
done <<< "$vhosts"

echo "
> Setup finished ! 

You can now install and configure 'auth_lemonldap' OpenERP module with these parameters:
- secret key: $lemon_secret
- forwarded host: $vhosts

Please double check your LemonLDAP configuration in LemonLDAP Manager"
