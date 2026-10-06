# Copyright 2026 verdigado eG
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Turn the existing overlaps into credit allocations.

    Until this version the overlap was credited by patching the balance after
    hr_holidays had computed it. That correction is gone, so without this
    migration every historical overlap would silently stop being credited.

    The sync reconciles instead of appending, so running it again is harmless.
    """
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    Leave = env["hr.leave"]
    Allocation = env["hr.leave.allocation"]

    employees = Leave.search(
        [
            ("state", "=", "validate"),
            ("holiday_status_id.can_overlap", "=", True),
        ]
    ).mapped("employee_id")
    if not employees:
        _logger.info("No leaves of an overlapping type, nothing to credit")
        return

    before = Allocation.search_count([("overlap_sick_leave_id", "!=", False)])
    total = len(employees)
    # one employee at a time, so a failure names the record it choked on
    for index, employee in enumerate(employees, start=1):
        _logger.info(
            "Creating overlap credits for %s (%s/%s)",
            employee.display_name,
            index,
            total,
        )
        Leave._sync_overlap_credits_for_employees(employee)

    after = Allocation.search_count([("overlap_sick_leave_id", "!=", False)])
    _logger.info(
        "Overlap credit allocations: %s before, %s after, %s employees checked",
        before,
        after,
        total,
    )
