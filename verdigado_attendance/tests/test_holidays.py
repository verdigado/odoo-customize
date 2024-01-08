# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date

from odoo import exceptions

from .hr_case import HrCase


class TestHolidays(HrCase):
    def _at_date(self, status, date, field):
        """Return value of some holiday status field at a time"""
        return status.get_employees_days(
            self.verdigado_user.employee_id.ids, date=date
        )[self.verdigado_user.employee_id.id][status.id][field]

    def test_standard_flow_past(self):
        """Test that employees can request holidays for the past"""
        holiday = (
            self.env["hr.leave"]
            .with_user(self.verdigado_user)
            .create(
                {
                    "employee_id": self.verdigado_user.employee_id.id,
                    "holiday_status_id": self.env.ref(
                        "hr_holidays.holiday_status_cl"
                    ).id,
                    "date_from": "2023-12-11 07:00:00",
                    "date_to": "2023-12-13 16:00:00",
                }
            )
        )
        holiday_status = holiday.holiday_status_id
        with self.assertRaisesRegex(
            exceptions.UserError,
            "manager rights to modify/validate a time off that already begun",
        ):
            holiday.action_approve()
        holiday_as_officer = holiday.with_user(self.verdigado_officer)
        holiday_as_officer.action_validate()
        self.assertEqual(holiday.number_of_days, 3)
        self.assertEqual(
            self._at_date(holiday_status, date(2023, 12, 31), "remaining_leaves"), 27
        )
        resource_leave = self.env["resource.calendar.leaves"].search(
            [("holiday_id", "in", holiday.ids)]
        )
        self.assertTrue(resource_leave)
        with self.assertRaisesRegex(
            exceptions.UserError,
            "manager rights to modify/validate a time off that already begun",
        ):
            holiday.unlink()
        holiday_as_officer.unlink()
        self.assertFalse(resource_leave.exists())
        self.assertEqual(
            self._at_date(holiday_status, date(2023, 12, 31), "remaining_leaves"), 30
        )

    def test_standard_flow_future(self):
        """Test that employees can request holidays for the future"""
        holiday = (
            self.env["hr.leave"]
            .with_user(self.verdigado_user)
            .create(
                {
                    "employee_id": self.verdigado_user.employee_id.id,
                    "holiday_status_id": self.env.ref(
                        "hr_holidays.holiday_status_cl"
                    ).id,
                    "date_from": "2042-12-15 07:00:00",
                    "date_to": "2042-12-17 16:00:00",
                }
            )
        )
        holiday_status = holiday.holiday_status_id
        with self.assertRaisesRegex(
            exceptions.UserError, "approve/refuse its own requests"
        ):
            holiday.action_approve()
        holiday_as_officer = holiday.with_user(self.verdigado_officer)
        holiday_as_officer.action_validate()
        resource_leave = self.env["resource.calendar.leaves"].search(
            [("holiday_id", "in", holiday.ids)]
        )
        self.assertTrue(resource_leave)
        self.assertEqual(
            self._at_date(holiday_status, date(2042, 12, 31), "remaining_leaves"), 27
        )
        holiday.unlink()
        self.assertEqual(
            self._at_date(holiday_status, date(2042, 12, 31), "remaining_leaves"), 30
        )
