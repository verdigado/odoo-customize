# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import SUPERUSER_ID, api


def migrate(cr, version=None):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["hr.attendance.overtime"].search([]).unlink()
    env["hr.attendance"].search([])._compute_theoretical_hours()
    env["hr.attendance"]._overtime_from_theoretical_time()
