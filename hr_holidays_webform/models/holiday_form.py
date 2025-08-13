from odoo import fields, models


class HolidayRequestForm(models.AbstractModel):
    _name = "cms.form.hr.leave.request"
    _inherit = "cms.form"

    form_model = "hr.leave.request"
    form_model_fields = ("name",)
    form_required_fields = ("name",)

    employee_name = fields.Char()
    employee_surname = fields.Char()
    start_date = fields.Date()
    end_date = fields.Date()
    certificate_file = fields.Binary()
