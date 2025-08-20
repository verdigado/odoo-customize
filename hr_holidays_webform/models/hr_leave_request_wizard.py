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
        self.env["hr.leave"].create(
            {
                "employee_id": self.employee_id.id,
                "holiday_status_id": self.leave_type_id.id,
                "date_from": self.start_date,
                "date_to": self.end_date,
                "name": f"Leave from request {self.request_id.id}",
            }
        )
