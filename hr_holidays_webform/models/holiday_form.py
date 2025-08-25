from odoo import fields, models


class HolidayRequestForm(models.AbstractModel):
    _name = "cms.form.hr.leave.request"
    _inherit = "cms.form"

    form_model = "hr.leave.request"
    form_model_fields = ("name",)
    form_required_fields = ("name",)

    employee_name = fields.Char(required=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    certificate_type = fields.Selection(
        selection=[
            ("none", "No Certificate"),
            ("cert", "Certificate"),
            ("e-cert", "E-Certificate"),
            ("child", "Child Sick Leave"),
        ],
        default="cert",
        required=True,
    )
    certificate_file = fields.Binary()
