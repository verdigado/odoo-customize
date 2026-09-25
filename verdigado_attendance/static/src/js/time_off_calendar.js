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
    // The dashboard cards show up in several view types that do not share a
    // controller: time_off_calendar and time_off_calendar_all both use
    // TimeOffCalendarController, while the employee view an administrator opens
    // uses TimeOffCalendarEmployeeController. Registering on only one of them
    // leaves the links dead in the other, which is what happened to .overlap.
    function includeCardHandlers(TargetController) {
        TargetController.include({
            events: _.extend({}, TargetController.prototype.events, {
                "click .overlap": "_onOverlap",
                "click .per_year": "_onPerYear",
            }),
            // The cards are inserted outside the renderer element, so setting
            // the popover up while rendering does not reach them. Delegate the
            // click instead and initialise on first use.
            _onPerYear: function (e) {
                e.preventDefault();
                var $toggle = jQuery(e.currentTarget);
                if (!$toggle.data("bs.popover")) {
                    $toggle.popover({
                        html: true,
                        placement: "bottom",
                        trigger: "focus",
                        content: $toggle.siblings(".per_year_content").html(),
                    });
                    $toggle.popover("show");
                }
            },
            _onOverlap: function (e) {
                return this.do_action({
                    type: "ir.actions.act_window",
                    res_model: "hr.leave",
                    views: [
                        [false, "list"],
                        [false, "form"],
                    ],
                    target: "current",
                    domain: [["id", "in", jQuery(e.currentTarget).data("ids")]],
                });
            },
        });
    }

    // Time_off_calendar and time_off_calendar_all share one controller class,
    // so keep track of what was patched already instead of including twice
    var patchedControllers = [];
    _.each(
        ["time_off_calendar", "time_off_calendar_all", "time_off_employee_calendar"],
        function (viewName) {
            var view = viewRegistry.get(viewName);
            // Guard: a view type we do not have is not an error here
            if (!view || !view.prototype.config.Controller) {
                return;
            }
            var TargetController = view.prototype.config.Controller;
            if (patchedControllers.indexOf(TargetController) === -1) {
                patchedControllers.push(TargetController);
                includeCardHandlers(TargetController);
            }
        }
    );
});
