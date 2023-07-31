# from odoo import models, fields, api


# class verdigado_template_default(models.Model):
#     _name = 'verdigado_template_default.verdigado_template_default'
#     _description = 'verdigado_template_default.verdigado_template_default'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
