# Copyright 2026 verdigado eG
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class ResourceCalendarAttendance(models.Model):
    _inherit = "resource.calendar.attendance"

    @api.model
    def read_group(
        self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True
    ):
        """Let callers restrict the grouping to a validity window

        hr_holidays groups attendances by weekday and day period to decide
        when a leave starts and ends, twice over and both times without
        looking at date_from and date_to on the lines. With
        hr_employee_calendar_planning the whole schedule history lives in one
        calendar as dated lines, so an expired one wins.

        Rather than reimplementing either of those groupings, hr.leave puts
        the requested period into the context and the domain is narrowed
        here. See hr_leave.py::_get_attendances.
        """
        window = self.env.context.get("hr_leave_attendances_valid_on")
        if window:
            start, end = window
            domain = list(domain) + [
                "|",
                ("date_from", "=", False),
                ("date_from", "<=", end),
                "|",
                ("date_to", "=", False),
                ("date_to", ">=", start),
            ]
        return super().read_group(
            domain,
            fields,
            groupby,
            offset=offset,
            limit=limit,
            orderby=orderby,
            lazy=lazy,
        )
