# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models

from .hr_attendance_break import DatetimeWithoutSeconds


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    check_in = DatetimeWithoutSeconds()
    check_out = DatetimeWithoutSeconds()
