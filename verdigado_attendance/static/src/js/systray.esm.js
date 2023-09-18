/** @odoo-module **/

import SystrayMenu from "web.SystrayMenu";
import Widget from "web.Widget";
import session from "web.session";

var OvertimeSystray = Widget.extend({
    template: "verdigado_attendance.OvertimeSystray",
    events: {
        "click a": "_onOvertimeClick",
    },
    start: function () {
        return this._super().then(this._onOvertimeUpdate.bind(this));
    },
    _onOvertimeClick: function () {
        return this.do_action("hr_attendance.hr_attendance_action");
    },
    _onOvertimeUpdate: function () {
        var self = this;
        return this._rpc({
            model: "hr.leave.type",
            method: "get_systray_data",
            args: [],
            kwargs: {context: session.user_context},
        }).then(function (data) {
            self.$("a").text(data[1].virtual_remaining_leaves_formatted);
        });
    },
});

SystrayMenu.Items.push(OvertimeSystray);
export default OvertimeSystray;
