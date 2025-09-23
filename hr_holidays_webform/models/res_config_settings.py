from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    requests_default_leave_type_id = fields.Many2one(
        "hr.leave.type",
        string="Default Leave Type for Leave Requests",
        config_parameter="hr_leave_request.default_leave_type",
    )

    manager_email = fields.Char(
        string="Default Manager Email",
        config_parameter="hr_leave_request.manager_email",
    )
