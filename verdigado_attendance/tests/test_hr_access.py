# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import exceptions
from odoo.tests.common import TransactionCase


class TestOvertimeCalculation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employeeA = cls.env["hr.employee"].create(
            {
                "name": "employeeA",
                "user_id": cls.env["res.users"]
                .create(
                    {
                        "name": "EmployeeA",
                        "login": "employeeA",
                        "groups_id": [
                            (4, cls.env.ref("hr.group_hr_user").id),
                            (
                                4,
                                cls.env.ref(
                                    "hr_attendance.group_hr_attendance_user"
                                ).id,
                            ),
                        ],
                    }
                )
                .id,
            }
        )
        cls.user_employeeA = cls.employeeA.user_id
        cls.attendance_employeeA = cls.env["hr.attendance"].create(
            {
                "employee_id": cls.employeeA.id,
            }
        )
        cls.attendance_overtime_employeeA = cls.env["hr.attendance.overtime"].create(
            {
                "employee_id": cls.employeeA.id,
            }
        )
        cls.employeeB = cls.employeeA.copy(
            {
                "name": "employeeB",
                "parent_id": cls.employeeA.id,
                "user_id": cls.employeeA.user_id.copy(
                    {"name": "EmployeeB", "login": "employeeB"}
                ).id,
            }
        )
        cls.user_employeeB = cls.employeeB.user_id
        cls.attendance_employeeB = cls.env["hr.attendance"].create(
            {
                "employee_id": cls.employeeB.id,
            }
        )
        cls.attendance_overtime_employeeB = cls.env["hr.attendance.overtime"].create(
            {
                "employee_id": cls.employeeB.id,
            }
        )
        cls.employeeC = cls.env["hr.employee"].create(
            {
                "name": "employeeC",
                "parent_id": cls.employeeB.id,
                "user_id": cls.employeeB.user_id.copy(
                    {"name": "EmployeeC", "login": "employeeC"}
                ).id,
            }
        )
        cls.user_employeeC = cls.employeeC.user_id
        cls.attendance_employeeC = cls.env["hr.attendance"].create(
            {
                "employee_id": cls.employeeC.id,
            }
        )
        cls.attendance_overtime_employeeC = cls.env["hr.attendance.overtime"].create(
            {
                "employee_id": cls.employeeC.id,
            }
        )
        cls.employeeD = cls.env["hr.employee"].create(
            {
                "name": "employeeD",
                "user_id": cls.env["res.users"]
                .create(
                    {
                        "name": "EmployeeD",
                        "login": "employeeD",
                        "groups_id": [
                            (4, cls.env.ref("hr.group_hr_user").id),
                            (
                                4,
                                cls.env.ref(
                                    "hr_attendance.group_hr_attendance_user"
                                ).id,
                            ),
                        ],
                    }
                )
                .id,
            }
        )
        cls.user_employeeD = cls.employeeD.user_id
        cls.attendance_employeeD = cls.env["hr.attendance"].create(
            {
                "employee_id": cls.employeeD.id,
            }
        )
        cls.attendance_overtime_employeeD = cls.env["hr.attendance.overtime"].create(
            {
                "employee_id": cls.employeeD.id,
            }
        )

    def test_hr_employee_access(self):
        """
        Test that hr users can only access their employees recursively, but no employees
        not below them in the hierarchy
        """
        self.env.cache.invalidate()
        self.assertEqual(
            self.employeeA.with_user(self.user_employeeA).user_id,
            self.employeeA.user_id,
        )
        self.env.cache.invalidate()
        self.assertEqual(
            self.employeeB.with_user(self.user_employeeA).user_id,
            self.employeeB.user_id,
        )
        self.env.cache.invalidate()
        self.assertEqual(
            self.employeeC.with_user(self.user_employeeA).user_id,
            self.employeeC.user_id,
        )
        self.env.cache.invalidate()
        with self.assertRaises(exceptions.AccessError):
            self.employeeD.with_user(self.user_employeeA).read([])
        self.env.cache.invalidate()
        with self.assertRaises(exceptions.AccessError):
            self.employeeA.with_user(self.user_employeeD).read([])
        self.env.cache.invalidate()
        with self.assertRaises(exceptions.AccessError):
            self.employeeA.with_user(self.user_employeeB).read([])
        self.env.cache.invalidate()
        with self.assertRaises(exceptions.AccessError):
            self.employeeB.with_user(self.user_employeeC).read([])

    def test_hr_attendance_access(self):
        """
        Test that hr attendance users can only access their employees' attendances
        recursively, but not attendances of employees not below them in the hierarchy
        """
        self.assertEqual(
            self.env["hr.attendance"].with_user(self.user_employeeA).search([]),
            self.attendance_employeeA
            + self.attendance_employeeB
            + self.attendance_employeeC,
        )
        self.assertEqual(
            self.env["hr.attendance"].with_user(self.user_employeeB).search([]),
            self.attendance_employeeB + self.attendance_employeeC,
        )
        self.assertEqual(
            self.env["hr.attendance"].with_user(self.user_employeeC).search([]),
            self.attendance_employeeC,
        )
        self.assertEqual(
            self.env["hr.attendance"].with_user(self.user_employeeD).search([]),
            self.attendance_employeeD,
        )
        self.assertEqual(
            self.env["hr.attendance.overtime"]
            .with_user(self.user_employeeA)
            .search([]),
            self.attendance_overtime_employeeA
            + self.attendance_overtime_employeeB
            + self.attendance_overtime_employeeC,
        )
        self.assertEqual(
            self.env["hr.attendance.overtime"]
            .with_user(self.user_employeeB)
            .search([]),
            self.attendance_overtime_employeeB + self.attendance_overtime_employeeC,
        )
        self.assertEqual(
            self.env["hr.attendance.overtime"]
            .with_user(self.user_employeeC)
            .search([]),
            self.attendance_overtime_employeeC,
        )
        self.assertEqual(
            self.env["hr.attendance.overtime"]
            .with_user(self.user_employeeD)
            .search([]),
            self.attendance_overtime_employeeD,
        )
