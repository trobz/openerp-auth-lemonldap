Delegated OpenERP authentication to LemonLDAP
=============================================

# Setup

The setup has been tested with 2 local virtual servers (ubuntu server 12.04) with OpenERP 7.0 and LemonLDAP 1.3.1. 
The LemonLDAP test page has been used as a third party application.

Domain local setup:

- LemonLDAP Handler: auth.lemon.dev (10.0.3.50) 
- LemonLDAP test page: test1.lemon.dev (10.0.3.50)
- OpenERP: protected.openerp.dev (10.0.3.31)

This configuration may reproduce the future production environment.

[Step by step setup documentation.](install/README.md)

# Caution

When the module is enabled, password verification is totally bypassed, because the authentication is delegated to LemonLDAP.

You must secure your OpenERP instance and make it accessible only trough the LemonLDAP Apache Proxy.

Some basic security are implemented on OpenERP side (Secret key and `X-Forwarded-Host` header check) but it's better to
add an IP restriction on OpenERP side too.

# Notes

- because all user are duplicated on LemonLDAP Database, you can't have 2 users with the same login on different OpenERP database
- the synchronization between OpenERP users and LemonLDAP Database is not handled by the `auth_lemonldap` module
- this setup has not been tested in HTTPS
