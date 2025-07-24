from odoo import http

from odoo.addons.cms_form.controllers import main as cms_form_main


class CmsFormPublicController(cms_form_main.CMSFormController):
    @http.route(
        ["/cms/create/<string:model>", "/cms/edit/<string:model>/<int:model_id>"],
        type="http",
        auth="public",
        website=True,
    )
    def cms_form(self, model, model_id=None, **kw):
        return super().cms_form(model, model_id, **kw)
