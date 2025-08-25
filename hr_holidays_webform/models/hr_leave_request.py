from odoo import api, fields, models


class HrLeaveRequest(models.Model):
    _name = "hr.leave.request"

    name = fields.Char(
        string="Request Name",
        compute="_compute_name",
        store=True,
    )
    employee_name = fields.Char(required=True)
    employee_surname = fields.Char(required=True)
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
    leave_id = fields.Many2one("hr.leave")
    leave_type_id = fields.Many2one(
        "hr.leave.type",
        default=lambda self: self.env["ir.config_parameter"]
        .sudo()
        .get_param("hr_leave_request.default_leave_type"),
    )

    @api.depends("employee_surname", "employee_name", "start_date", "end_date")
    def _compute_name(self):
        for record in self:
            parts = []
            if record.employee_surname or record.employee_name:
                parts.append(
                    f"{record.employee_surname or ''} {record.employee_name or ''}".strip()
                )
            if record.start_date and record.end_date:
                parts.append(f"from {record.start_date} to {record.end_date}")
            record.name = (
                "Leave Request: " + " ".join(parts) if parts else "Leave Request"
            )

    def action_open_wizard(self):
        return {
            "name": "Create HR Leaves",
            "type": "ir.actions.act_window",
            "res_model": "hr.leave.request.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_request_id": self.id,
                "default_start_date": self.start_date,
                "default_end_date": self.end_date,
                "default_leave_type_id": self.leave_type_id.id,
            },
        }
