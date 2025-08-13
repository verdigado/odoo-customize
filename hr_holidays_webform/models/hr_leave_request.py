from odoo import fields, models


class HrLeaveRequest(models.Model):
    _name = "hr.leave.request"

    employee_name = fields.Char()
    employee_surname = fields.Char()
    start_date = fields.Date()
    end_date = fields.Date()
    certificate_file = fields.Binary()
