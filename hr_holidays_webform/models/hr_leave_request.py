from odoo import fields, models


class HrLeaveRequest(models.Model):
    _name = "hr.leave.request"

    employee_name = fields.Char()
    employee_surname = fields.Char()
    start_date = fields.Date()
    end_date = fields.Date()
    certificate_file = fields.Binary()
    leave_id = fields.Many2one("hr.leave")

    def action_open_wizard(self):
        return {
            "name": "Create HR Leaves",
            "type": "ir.actions.act_window",
            "res_model": "hr.leave.request.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_request_id": self.id},
        }
