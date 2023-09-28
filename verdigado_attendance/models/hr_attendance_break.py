# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class DatetimeWithoutSeconds(fields.Datetime):
    def convert_to_column(self, value, record, values=None, validate=True):
        return super().convert_to_column(
            value and self.to_datetime(value).replace(second=0) or value,
            record,
            values=values,
            validate=validate,
        )


class HrAttendanceBreak(models.Model):
    _inherit = "hr.attendance.break"

    begin = DatetimeWithoutSeconds()
    end = DatetimeWithoutSeconds()
