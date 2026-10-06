# Copyright 2026 verdigado eG
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo import fields, models


class HrLeaveAllocation(models.Model):
    _inherit = "hr.leave.allocation"

    overlap_sick_leave_id = fields.Many2one(
        "hr.leave",
        string="Overlapping leave",
        ondelete="cascade",
        index=True,
        copy=False,
        help="Leave of an overlapping type that consumed the credited days",
    )
    overlap_leave_id = fields.Many2one(
        "hr.leave",
        string="Credited leave",
        ondelete="cascade",
        index=True,
        copy=False,
        help="Leave whose days were lost to the overlap",
    )
