# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class HrCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.verdigado_user = cls.env.ref("verdigado_attendance.verdigado_user")
        cls.verdigado_officer = cls.env.ref("verdigado_attendance.verdigado_officer")
        cls.verdigado_manager = cls.env.ref("verdigado_attendance.verdigado_manager")
