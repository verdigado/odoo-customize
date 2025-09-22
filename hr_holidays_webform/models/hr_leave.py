from odoo import fields, models


class HrLeave(models.Model):
    _inherit = "hr.leave"

    leave_request_id = fields.Many2one("hr.leave.request", string="Leave Request")
