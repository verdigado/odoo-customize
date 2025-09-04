from datetime import datetime

from odoo import fields, models


class HrLeaveRequestWizard(models.TransientModel):
    _name = "hr.leave.request.wizard"
    _description = "Wizard to manually create leaves from leave requests"

    request_id = fields.Many2one(
        "hr.leave.request", string="Leave Request", required=True, readonly=True
    )
    employee_id = fields.Many2one("hr.employee", string="Employee", required=True)
    leave_type_id = fields.Many2one("hr.leave.type", string="Leave Type", required=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)

    def action_create_leave(self):
        date_from = datetime.combine(self.start_date, datetime.min.time())
        date_to = datetime.combine(self.end_date, datetime.max.time())
        self.request_id.create_leave_from_leave_request(
            employee_id=self.employee_id.id,
            date_from=date_from,
            date_to=date_to,
            leave_type_id=self.leave_type_id,
        )
        return {"type": "ir.actions.client", "tag": "reload"}
