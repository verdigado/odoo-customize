# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo import fields, models


class HrLeaveType(models.Model):
    _inherit = "hr.leave.type"

    can_overlap = fields.Boolean("Allow overlap with other leaves")

    # The balance used to be patched here after hr_holidays had computed it:
    # the overlap was credited onto whichever allocation happened to be valid
    # today, and the "error" bucket was cancelled out by the same amount. That
    # only ever worked when the credit matched the shortfall to the day, which
    # is a coincidence, and it could not cover leaves predating today's
    # allocation. The overlap is now mirrored by a real hr.leave.allocation
    # (see hr_leave.py), so the core charges the days at the time they were
    # lost and no correction is needed afterwards.

    def _get_overlap(self, employee_id, leave_type):
        """Return overlapping leaves and the working time of the overlap"""
        HrLeave = self.env["hr.leave"]

        # Make sure, employee_id is int, not list
        if type(employee_id) is list:
            employee_id = employee_id[0]

        for possible_overlap in HrLeave.search(
            [
                ("employee_id", "=", employee_id),
                ("state", "=", "validate"),
                ("holiday_status_id.can_overlap", "=", True),
            ]
        ):
            for overlap in HrLeave.search(
                [
                    ("employee_id", "=", employee_id),
                    ("state", "in", ("confirm", "validate1", "validate")),
                    ("id", "not in", possible_overlap.ids),
                    ("date_from", "<=", possible_overlap.date_to),
                    ("date_to", ">=", possible_overlap.date_from),
                    ("holiday_status_id", "=", leave_type),
                ]
            ):
                # Whether public holidays count is driven by the context only,
                # not by compute_leaves. Take it from the overlapped leave type
                # instead of inheriting it from the caller, otherwise the same
                # overlap is worth 8 days in the dashboard and 7 on approval.
                employee = overlap.employee_id.with_context(
                    employee_id=employee_id,
                    exclude_public_holidays=bool(
                        overlap.holiday_status_id.exclude_public_holidays
                    ),
                )
                number_of_days = employee._get_work_days_data_batch(
                    possible_overlap.date_from
                    if possible_overlap.date_from >= overlap.date_from
                    else overlap.date_from,
                    possible_overlap.date_to
                    if possible_overlap.date_to <= overlap.date_to
                    else overlap.date_to,
                    compute_leaves=False,
                )[employee_id]["days"]
                yield possible_overlap, overlap, number_of_days
