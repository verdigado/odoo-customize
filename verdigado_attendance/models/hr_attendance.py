# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

#
# dummy model to allow verdigado_hr_attendance_rule_attendance_manager rule
#

from odoo import _, api, fields, models
from odoo.exceptions import UserError

class HrAttendance(models.Model):
    _inherit = "hr.attendance"
