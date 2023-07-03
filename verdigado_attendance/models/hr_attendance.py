# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

#
# dummy model to allow verdigado_hr_attendance_rule_attendance_manager rule
#

from odoo import models


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    def _update_overtime(self, employee_attendance_dates=None):
        """Compute overtime from theoretical time"""
        report = self.env["hr.attendance.theoretical.time.report"]
        for this in self:
            day_start_utc, date = self._get_day_start_and_day(
                this.employee_id, this.check_in
            )
            overtime = (
                self.env["hr.attendance.overtime"]
                .search(
                    [
                        ("employee_id", "=", this.employee_id.id),
                        ("date", "=", date),
                        ("adjustment", "=", False),
                    ]
                )
                .sudo()
            )
            if not overtime:
                duration = this.worked_hours - report._theoretical_hours(
                    this.employee_id, date
                )
                self.env["hr.attendance.overtime"].create(
                    {
                        "employee_id": this.employee_id.id,
                        "date": date,
                        "duration": duration,
                        "duration_real": duration,
                    }
                )
            else:
                overtime.write(
                    {
                        "duration": overtime.duration + this.worked_hours,
                        "duration_real": overtime.duration + this.worked_hours,
                    }
                )

    def _overtime_from_theoretical_time(self):
        """
        Write missing overtime records based on hr_attendance_theoretical_time_report
        Generate records up until yesterday to avoid interfering with today's time recording
        """
        self.env.cr.execute(
            """
            select
                r.employee_id, r.date, sum(coalesce(r.theoretical_hours, 0)),
                sum(r.worked_hours), sum(r.difference)
            from hr_attendance_theoretical_time_report r
            left join hr_attendance_overtime o
                on r.employee_id=o.employee_id and r.date=o.date and not o.adjustment
            where o.id is null and r.date < now()::date
            group by r.employee_id, r.date
            """
        )
        create_list = []
        report = self.env["hr.attendance.theoretical.time.report"]
        for (
            employee_id,
            date,
            theoretical_hours,
            worked_hours,
            difference,
        ) in self.env.cr.fetchall():
            employee = self.env["hr.employee"].browse(employee_id)
            duration = (
                difference
                if theoretical_hours > 0
                else ((worked_hours or 0) - report._theoretical_hours(employee, date))
            )
            create_list.append(
                {
                    "employee_id": employee_id,
                    "date": date,
                    "duration": duration,
                    "duration_real": duration,
                }
            )
        return self.env["hr.attendance.overtime"].create(create_list)
