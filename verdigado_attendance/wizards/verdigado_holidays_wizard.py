# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import math
from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import _, fields, models


class VerdigadoHolidaysWizard(models.TransientModel):
    _name = "verdigado.holidays.wizard"
    _description = "Create holidays allocations"

    full_vacation = fields.Float(
        default=30,
        string="Vacation days (100%)",
        required=True,
        help="Vacation of a FTE in days",
    )
    year = fields.Selection(
        lambda self: [
            (year, year)
            for year in range(fields.Date.today().year, fields.Date.today().year + 3)
        ],
        default=lambda self: fields.Date.today().year + 1,
        required=True,
    )
    date_start = fields.Date(
        required=True,
        string="Validity start",
        default=lambda self: fields.Date.today()
        + relativedelta(month=1, day=1, years=1),
    )
    date_end = fields.Date(
        string="Validity end",
        default=lambda self: fields.Date.today()
        + relativedelta(month=1, day=1, years=1),
    )
    leave_type_id = fields.Many2one(
        "hr.leave.type",
        required=True,
        default=lambda self: self.env.ref("hr_holidays.holiday_status_cl", False),
    )
    employee_ids = fields.Many2many("hr.employee", string="Employees")

    def button_assign_vacation(self):
        interval_start = date(int(self.year), 1, 1)
        interval_end = interval_start.replace(month=12, day=31)
        days = (interval_end - interval_start).days
        allocations = self.env["hr.leave.allocation"].browse([])
        for employee in self.employee_ids or self.env["hr.employee"].browse(
            self.env.context.get("active_ids", [])
        ):
            percentage = 0.0
            for calendar in employee.calendar_ids:
                if (
                    calendar.date_start
                    and calendar.date_start >= interval_end
                    or calendar.date_end
                    and calendar.date_end <= interval_start
                ):
                    continue
                week_days = len(
                    set(calendar.calendar_id.mapped("attendance_ids.dayofweek"))
                )
                # use month precision if calendar starts and ends on a month boundary
                # use day precision otherwise
                if (
                    max(calendar.date_start or interval_start, interval_start).day == 1
                    and (
                        min(calendar.date_end or interval_end, interval_end)
                        + relativedelta(days=1)
                    ).month
                    != min(calendar.date_end or interval_end, interval_end).month
                ):
                    interval_percentage = round(
                        float(
                            min(calendar.date_end or interval_end, interval_end).month
                            - max(
                                calendar.date_start or interval_start, interval_start
                            ).month
                            + 1
                        )
                        / (interval_end.month - interval_start.month + 1),
                        2,
                    )
                else:
                    interval_percentage = round(
                        (
                            min(calendar.date_end or interval_end, interval_end)
                            - max(calendar.date_start or interval_start, interval_start)
                        ).days
                        / days,
                        2,
                    )
                percentage += interval_percentage * round(float(week_days) / 5, 2)

            if percentage:
                allocations += self.env["hr.leave.allocation"].create(
                    {
                        "name": str(self.date_start.year),
                        "employee_id": employee.id,
                        "holiday_status_id": self.leave_type_id.id,
                        "date_from": self.date_start,
                        "date_to": self.date_end,
                        "number_of_days": math.ceil(percentage * self.full_vacation),
                    }
                )
        allocations.filtered(lambda x: x.state == "draft").action_confirm()
        allocations.filtered(
            lambda x: x.state in ("confirm", "validate1")
        ).action_validate()
        return {
            "type": "ir.actions.act_window",
            "res_model": "hr.leave.allocation",
            "views": [(False, "list"), (False, "form")],
            "domain": [("id", "in", allocations.ids)],
            "name": _("Created allocations"),
        }
