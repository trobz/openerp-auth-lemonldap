#!/usr/bin/env bash

# 
# Setup LemonLDAP to use authDBI authentication, user and password modules.
# Use a MySQL database, better support for the only weak password encryption supported by 
# LemonLDAP::authDBI..
#
# Admin user is set to admin/m1de9ak1Zd by default, please change the password with lemon portal
#

# install prerequisites
sudo apt-get install mysql-server libdbd-mysql-perl

# setup auth database
sudo mysql -u root -p < lemon_user_auth.sql

echo 'mysql lemon_user_auth database created, default user: admin / m1de9ak1Zd'

# set lemonldap configuration
