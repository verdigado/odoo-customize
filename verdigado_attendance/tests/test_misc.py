# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo.tests.common import TransactionCase


class TestMisc(TransactionCase):
    def test_update_overtime_date(self):
        """Test that we keep adjustments when changing overtime"""
        company = self.env.ref("base.main_company")
        overtime = self.env["hr.attendance.overtime"].create(
            {
                "employee_id": self.env.ref("hr.employee_qdp").id,
                "date": company.overtime_start_date,
                "adjustment": True,
            }
        )
        company.write(
            {
                "overtime_company_threshold": company.overtime_company_threshold,
                "overtime_employee_threshold": company.overtime_employee_threshold,
                "hr_attendance_overtime": True,
                "overtime_start_date": company.overtime_start_date + timedelta(days=1),
            }
        )
        self.assertTrue(overtime.exists())
