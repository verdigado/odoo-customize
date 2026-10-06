# Copyright 2026 verdigado eG
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase

# 2024-06-03 is a Monday, so this is one full working week. The timestamps are
# UTC and given directly: hr.leave only derives date_from and date_to from the
# request_date fields through an onchange, a plain create would leave them at
# their default of "now".
WEEK_FROM = "2024-06-03 00:00:00"
WEEK_TO = "2024-06-07 23:59:59"
# Wednesday and Thursday of the same week
MIDWEEK_FROM = "2024-06-05 00:00:00"
MIDWEEK_TO = "2024-06-06 23:59:59"


class TestDaysPerYear(TransactionCase):
    """Cover the year breakdown behind the dashboard.

    Everything is built from scratch rather than from demo data, which is
    dated relative to today and does not install reliably.

    The scenario is one allocation year with an overlap in it: 20 days valid
    throughout 2024, a week of leave, and two of those days lost to a leave
    whose type allows overlapping. That leaves a credit allocation without an
    end date next to a regular one that expired at the end of 2024.
    """

    def setUp(self):
        super().setUp()
        self.calendar = self.env["resource.calendar"].create(
            {
                "name": "Days per year test calendar",
                "tz": "Europe/Berlin",
                "attendance_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "%s %s" % (day, period),
                            "dayofweek": str(index),
                            "hour_from": hour_from,
                            "hour_to": hour_to,
                            "day_period": period,
                        },
                    )
                    for index, day in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri"])
                    for period, hour_from, hour_to in (
                        ("morning", 8.0, 12.0),
                        ("afternoon", 13.0, 17.0),
                    )
                ],
            }
        )
        self.employee = self.env["hr.employee"].create(
            {
                "name": "Breakdown Tester",
                "resource_calendar_id": self.calendar.id,
            }
        )
        self.vacation_type = self.env["hr.leave.type"].create(
            {
                "name": "Test vacation",
                "requires_allocation": "yes",
                "allocation_validation_type": "no",
                "leave_validation_type": "hr",
                "request_unit": "day",
                "can_overlap": False,
                "exclude_public_holidays": True,
            }
        )
        self.sick_type = self.env["hr.leave.type"].create(
            {
                "name": "Test sickness",
                "requires_allocation": "no",
                "leave_validation_type": "hr",
                "request_unit": "day",
                "can_overlap": True,
            }
        )
        self.allocation = self.env["hr.leave.allocation"].create(
            {
                "name": "Test allocation 2024",
                "holiday_status_id": self.vacation_type.id,
                "employee_id": self.employee.id,
                "holiday_type": "employee",
                "allocation_type": "regular",
                "number_of_days": 20.0,
                "date_from": "2024-01-01",
                "date_to": "2024-12-31",
                "state": "validate",
            }
        )
        self._create_leave(self.vacation_type, WEEK_FROM, WEEK_TO)
        self._create_leave(self.sick_type, MIDWEEK_FROM, MIDWEEK_TO)

    def _create_leave(self, leave_type, date_from, date_to):
        leave = self.env["hr.leave"].create(
            {
                "name": "%s %s" % (leave_type.name, date_from),
                "employee_id": self.employee.id,
                "holiday_status_id": leave_type.id,
                "date_from": date_from,
                "date_to": date_to,
            }
        )
        leave.action_validate()
        return leave

    def _single_year(self):
        per_year = self.vacation_type.with_context(
            employee_id=self.employee.id
        )._get_days_per_year()
        self.assertEqual(len(per_year), 1)
        self.assertEqual(per_year[0]["year"], 2024)
        return per_year[0]

    def test_entitlement_includes_the_overlap_credit(self):
        """The credit is entitlement of the year the days were lost in"""
        self.assertEqual(self._single_year()["max_leaves"], 22)

    def test_leaves_taken_is_gross(self):
        """The credit must not be deducted from what was taken.

        It used to be booked as negative consumption, so the credit had to be
        added back here to keep a year without any leave from reading as
        "taken -2". Now that it is a real allocation, adding anything would
        overstate what was used.
        """
        self.assertEqual(self._single_year()["leaves_taken"], 5)

    def test_open_ended_credit_does_not_widen_the_window(self):
        """Credits carry no end date and must not drop the upper bound.

        The leaves listed for a year are looked up between the first start and
        the last end of that year's allocations. Letting a credit take part
        would leave the range open and list every later leave as well.
        """
        upper = [
            leaf
            for leaf in self._single_year()["domain"]
            if leaf[0] == "date_from" and leaf[1] == "<="
        ]
        self.assertEqual(len(upper), 1)
        self.assertTrue(upper[0][2].startswith("2024-12-31"))
