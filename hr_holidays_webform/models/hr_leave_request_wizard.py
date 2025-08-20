from odoo import fields, models


class HrLeaveRequestWizard(models.TransientModel):
    _name = "hr.leave.request.wizard"
    _description = "Wizard to manually create leaves from leave requests"

    request_id = fields.Many2one(
        "hr.leave.request", string="Leave Request", required=True, readonly=True
    )
    employee_id = fields.Many2one("hr.employee", string="Employees", required=True)
    leave_type_id = fields.Many2one("hr.leave.type", string="Leave Type", required=True)

    def action_create_leave(self):
        self.env["hr.leave"].create(
            {
                "employee_id": self.employee.id,
                "holiday_status_id": self.leave_type_id.id,
                "request_date_from": self.request_id.start_date,
                "request_date_to": self.request_id.end_date,
                "name": f"Leave from request {self.request_id.id}",
            }
        )
