odoo.define("verdigado_attendance.time_off_calendar", function (require) {
    "use strict";

    var viewRegistry = require("web.view_registry");
    // Even though core doesn't return anything here, we need the require for correct dependencies
    require("hr_holidays.dashboard.view_custo");

    viewRegistry.get("time_off_calendar_all").prototype.config.Renderer.include({
        _render: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                return self
                    ._rpc({
                        model: "base.ical",
                        method: "search_read",
                        args: [
                            [["show_on_holiday_calendar", "=", true]],
                            ["user_active", "user_url", "name"],
                        ],
                        context: self.state.context,
                    })
                    .then(function (ical_calendars) {
                        var $links = self.$(".ical_links");
                        if (ical_calendars.length === 0) {
                            $links.hide();
                        } else {
                            $links.children("a").remove();
                            $links.children("br").remove();
                            _.chain(ical_calendars)
                                .filter("user_active")
                                .each(function (ical) {
                                    var $a = jQuery(
                                        '<a href="' + ical.user_url + '"/>'
                                    );
                                    $a.text(ical.name);
                                    $links.append($a);
                                    $links.append("<br/>");
                                });
                        }
                    });
            });
        },
    });
});
