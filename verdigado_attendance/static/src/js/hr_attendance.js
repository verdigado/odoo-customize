/* Copyright 2023 Hunki Enterprises BV
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("verdigado_attendance.hr_attendance", function (require) {
    "use strict";

    var myAttendances = require("hr_attendance.my_attendances");
    var core = require("web.core");

    myAttendances.include({
        events: _.extend(myAttendances.prototype.events, {
            "click a.add_to_dashboard": "_add_to_dashboard",
        }),

        willStart: function () {
            var self = this;
            var promise = this._rpc({
                model: "res.users",
                method: "get_effective_holiday_overtime_factor",
            }).then(function (data) {
                self.effective_holiday_overtime_factor = data;
            });
            return Promise.all([this._super.apply(this, arguments), promise]);
        },

        _rpc: function (params) {
            if (
                params &&
                params.model === "hr.employee" &&
                params.method === "attendance_manual"
            ) {
                params.context.default_apply_holiday_overtime_factor = this.$(
                    "#apply_holiday_overtime"
                ).is(":checked");
            }
            return this._super.apply(this, arguments);
        },

        _add_to_dashboard: function () {
            return this._rpc({
                route: "/board/add_to_dashboard",
                params: {
                    action_id: -1,
                    context_to_save: {},
                    domain: [],
                    view_mode: "hr_attendance_my_attendances",
                    name: core._t("Check In / Check Out"),
                },
            });
        },
    });
});
