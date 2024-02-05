# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests.common import TransactionCase


class TestHolidayWizard(TransactionCase):
    def setUp(self):
        super().setUp()
        self.employee = self.env.ref("hr.employee_qdp")
        self.leave_type = self.env.ref("hr_holidays.holiday_status_cl")

    def _test_holidays_wizard(self):
        wizard = (
            self.env["verdigado.holidays.wizard"]
            .with_context(
                active_model="hr.employee",
                active_ids=self.employee.ids,
                active_id=self.employee.id,
            )
            .create({})
        )
        action = wizard.button_assign_vacation()
        return self.env[action["res_model"]].search(action["domain"])

    def test_no_validation(self):
        """Test that the holidays wizard creates allocations with slightly changed defaults"""
        self.leave_type.allocation_validation_type = "no"
        self.employee.calendar_ids.unlink()
        allocation = self._test_holidays_wizard()
        self.assertFalse(allocation)

    def test_25h_week(self):
        """Test an employee with a 2 day week"""
        calendar_25h = self.env["resource.calendar"].create(
            {
                "name": "25h week",
                "attendance_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Monday",
                            "dayofweek": "0",
                            "hour_from": 8,
                            "hour_to": 16,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Tuesday",
                            "dayofweek": "1",
                            "hour_from": 8,
                            "hour_to": 16,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Wednesday",
                            "dayofweek": "2",
                            "hour_from": 8,
                            "hour_to": 17,
                        },
                    ),
                ],
            }
        )
        self.employee.write(
            {
                "calendar_ids": [
                    (6, 0, []),
                    (
                        0,
                        0,
                        {
                            "date_start": fields.Date.today()
                            + relativedelta(month=1, day=1, years=1),
                            "date_end": fields.Date.today()
                            + relativedelta(month=6, day=30, years=1),
                            "calendar_id": calendar_25h.id,
                        },
                    ),
                ],
            }
        )
        allocation = self._test_holidays_wizard()
        self.assertEqual(allocation.employee_id, self.employee)
        self.assertEqual(allocation.number_of_days, 9)

    def test_multi_calendar_2_times5days(self):
        """Two times 5d week"""
        self.employee.write(
            {
                "calendar_ids": [
                    (6, 0, []),
                    (
                        0,
                        0,
                        {
                            "date_start": fields.Date.today()
                            + relativedelta(month=1, day=1, years=1),
                            "date_end": fields.Date.today()
                            + relativedelta(month=6, day=30, years=1),
                            "calendar_id": self.env.ref(
                                "resource.resource_calendar_std"
                            ).id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "date_start": fields.Date.today()
                            + relativedelta(month=7, day=1, years=1),
                            "date_end": fields.Date.today()
                            + relativedelta(month=12, day=31, years=1),
                            "calendar_id": self.env.ref(
                                "resource.resource_calendar_std"
                            ).id,
                        },
                    ),
                ],
            }
        )
        allocation = self._test_holidays_wizard()
        self.assertEqual(allocation.number_of_days, 30)

    def test_multi_calendar_short_4day_long_5day(self):
        """4d week in jan/feb, 5d rest"""
        four_day_week = self.env.ref("resource.resource_calendar_std_38h")
        four_day_week.attendance_ids.filtered(lambda x: x.dayofweek == "4").unlink()
        self.employee.write(
            {
                "calendar_ids": [
                    (6, 0, []),
                    (
                        0,
                        0,
                        {
                            "date_start": fields.Date.today()
                            + relativedelta(month=1, day=1, years=1),
                            "date_end": fields.Date.today()
                            + relativedelta(month=2, day=28, years=1),
                            "calendar_id": four_day_week.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "date_start": fields.Date.today()
                            + relativedelta(month=3, day=1, years=1),
                            "calendar_id": self.env.ref(
                                "resource.resource_calendar_std"
                            ).id,
                        },
                    ),
                ],
            }
        )
        allocation = self._test_holidays_wizard()
        self.assertEqual(allocation.number_of_days, 29)

    def test_multi_calendar_short_4day_long_5day_no_month_boundary(self):
        """4d week in jan/feb, 5d rest without ending at a month end"""
        four_day_week = self.env.ref("resource.resource_calendar_std_38h")
        four_day_week.attendance_ids.filtered(lambda x: x.dayofweek == "4").unlink()
        self.employee.write(
            {
                "calendar_ids": [
                    (6, 0, []),
                    (
                        0,
                        0,
                        {
                            "date_start": fields.Date.today()
                            + relativedelta(month=1, day=1, years=1),
                            "date_end": fields.Date.today()
                            + relativedelta(month=2, day=15, years=1),
                            "calendar_id": four_day_week.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "date_start": fields.Date.today()
                            + relativedelta(month=2, day=16, years=1),
                            "calendar_id": self.env.ref(
                                "resource.resource_calendar_std"
                            ).id,
                        },
                    ),
                ],
            }
        )
        allocation = self._test_holidays_wizard()
        self.assertEqual(allocation.number_of_days, 29)
