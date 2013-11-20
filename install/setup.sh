#!/usr/bin/env bash

# 
# Setup LemonLDAP to use authDBI authentication, user and password modules.
# Use a MySQL database, better support for the only weak password encryption supported by 
# LemonLDAP::authDBI..
#


echo ""
echo "========================"
echo "  Install dependancies"
echo "========================"
echo ""

# install prerequisites
sudo apt-get install mysql-server libdbd-mysql-perl python-mysqldb

echo ""
echo "========================"
echo "  Setup Auth Database"
echo "========================"
echo ""

echo "Enter MySQL root password:"
read root_pass

# setup auth database
mysql -u root -p$root_pass < lemon_user_auth.sql

# import users

echo ""
echo "========================"
echo "Import user from OpenERP"
echo "========================"
echo ""

echo "Enter the OpenERP XML-RPC Host:"
read host

echo "Enter the OpenERP XML-RPC Port:"
read port

echo "Enter the OpenERP database name:"
read database

echo "Enter the OpenERP username:"
read username

echo "Enter the OpenERP password:"
read password

python sync-user.py $host $port $database $username $password
