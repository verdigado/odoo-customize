odoo.define("verdigado_attendance.BoadRenderer", function (require) {
    "use strict";
    var BoardView = require("board.BoardView");
    var core = require("web.core");

    BoardView.prototype.config.Renderer.include({
        _createController: function (params) {
            if (params.viewType === "hr_attendance_my_attendances") {
                var client_action = core.action_registry.get(
                    "hr_attendance_my_attendances"
                );
                var attendances = new client_action(this, {}, {});
                attendances.do_action = function () {
                    params.$node.empty();
                    return attendances.appendTo(params.$node).then(function () {
                        return attendances.willStart();
                    });
                };
                return attendances.appendTo(params.$node);
            }
            return this._super.apply(this, arguments);
        },
    });
});
