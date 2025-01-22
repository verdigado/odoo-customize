import logging

from odoo import models, api

_logger = logging.getLogger(__name__)

class ResUsers(models.Model):
    _inherit = 'res.users'

    # Overwrite _auth_oauth_signin() to add oauth_uid et.a. to existing user accounts on successful login via keycloak.
    # inspired by https://github.com/diegonaranjo/odoo-addons-auth_oauth/blob/main/models/res_users.py
    # based on https://github.com/OCA/OCB/blob/16.0/addons/auth_oauth/models/res_users.py
    @api.model
    def _auth_oauth_signin(self, provider, validation, params):
        """ retrieve and sign in the user corresponding to provider and validated access token
            :param provider: oauth provider id (int)
            :param validation: result of validation of access token (dict)
            :param params: oauth parameters (dict)
            :return: user login (str)
            :raise: AccessDenied if signin failed

            This method can be overridden to add alternative signin methods.
        """
        oauth_uid = validation['user_id']
        email = validation.get('email')
        try:
            oauth_user = self.search([("oauth_uid", "=", oauth_uid), ('oauth_provider_id', '=', provider)])
            if not oauth_user and email:
                # If not found, search by email.
                oauth_user = self.search([("login", "=", email)])
                if oauth_user:
                    _logger.info("User with email %s found and will add oauth settings.", email)
                    # If the user with that email exists, we update their OAuth data
                    oauth_user.write({
                        'oauth_provider_id': provider,
                        'oauth_uid': oauth_uid,
                        'oauth_access_token': params['access_token']
                    })
            if not oauth_user:
                raise AccessDenied()
            assert len(oauth_user) == 1
            oauth_user.write({'oauth_access_token': params['access_token']})
            return oauth_user.login
        except AccessDenied as access_denied_exception:
            if self.env.context.get('no_user_creation'):
                return None
            state = json.loads(params['state'])
            token = state.get('t')
            values = self._generate_signup_values(provider, validation, params)
            try:
                login, _ = self.signup(values, token)
                return login
            except (SignupError, UserError):
                raise access_denied_exception
