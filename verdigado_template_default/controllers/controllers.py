# -*- coding: utf-8 -*-
# from odoo import http


# class VerdigadoTemplateDefault(http.Controller):
#     @http.route('/verdigado_template_default/verdigado_template_default/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/verdigado_template_default/verdigado_template_default/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('verdigado_template_default.listing', {
#             'root': '/verdigado_template_default/verdigado_template_default',
#             'objects': http.request.env['verdigado_template_default.verdigado_template_default'].search([]),
#         })

#     @http.route('/verdigado_template_default/verdigado_template_default/objects/<model("verdigado_template_default.verdigado_template_default"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('verdigado_template_default.object', {
#             'object': obj
#         })
