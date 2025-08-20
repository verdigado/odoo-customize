from odoo import api, fields, models


class HrLeaveRequest(models.Model):
    _name = "hr.leave.request"

    name = fields.Char(
        string="Request Name",
        compute="_compute_name",
        store=True,
    )
    employee_name = fields.Char()
    employee_surname = fields.Char()
    start_date = fields.Date()
    end_date = fields.Date()
    certificate_file = fields.Binary()
    leave_id = fields.Many2one("hr.leave")

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
            },
        }
