odoo.define("aspl_hrms_dashboard.HrDashboardRewrite", function (require) {
  "use strict";

  var AbstractAction = require("web.AbstractAction");
  var core = require("web.core");
  var web_client = require("web.web_client");
  var _t = core._t;
  var QWeb = core.qweb;

  var HrDashboard = AbstractAction.extend({
    template: "HrDashboardMain",

    cssLibs: ["/aspl_hrms_dashboard/static/src/css/lib/nv.d3.css"],
    jsLibs: ["/aspl_hrms_dashboard/static/src/js/lib/d3.min.js"],

    events: {
      "click .table_data_todays_leave": "table_data_todays_leave",
    },

    init: function (parent, context) {
      this._super(parent, context);
      this.dashboards_templates = ["HrDashboard"];
      this.login_employee = [];
    },

    willStart: function () {
      var self = this;
      this.login_employee = {};
      return this._super().then(function () {
        var def0 = self
          ._rpc({
            model: "hr.employee",
            method: "check_user_group_hr",
          })
          .then(function (result) {
            if (result == "main_hr") {
              self.is_main_hr = true;
            } else if (result == "jr_hr") {
              self.is_jr_hr = true;
            }
          });
        var def1 = self
          ._rpc({
            model: "hr.employee",
            method: "get_user_employee_details_hr",
          })
          .then(function (result) {
            self.login_employee = result;
          });
        return $.when(def0, def1);
      });
    },

    start: function () {
      var self = this;
      this.set("title", "HrDashboard");
      return this._super().then(function () {
        self.update_cp();
        self.render_dashboards();
        self.$el.parent().addClass("oe_background_grey");
      });
    },

    fetch_data: function () {
      var self = this;
      var def0 = self
        ._rpc({
          model: "hr.employee",
          method: "check_user_group_hr",
        })
        .then(function (result) {
          if (result == "main_hr") {
            self.is_main_hr = true;
          } else if (result == "jr_hr") {
            self.is_jr_hr = true;
          }
        });
      var def1 = this._rpc({
        model: "hr.employee",
        method: "get_user_employee_details_hr",
      }).then(function (result) {
        self.login_employee = result;
      });
      return $.when(def0, def1);
    },

    render_dashboards: function () {
      var self = this;
      if (this.login_employee) {
        var templates = [];

        if (self.is_main_hr == true || self.is_jr_hr == true) {
          templates = ["HrDashboard"];
        } else {
          templates = [];
        }
        _.each(templates, function (template) {
          self
            .$(".o_hr_dashboard")
            .append(QWeb.render(template, { widget: self }));
        });
      } else {
        self
          .$(".o_hr_dashboard")
          .append(QWeb.render("EmployeeWarningHr", { widget: self }));
      }
    },

    on_reverse_breadcrumb: function () {
      var self = this;
      web_client.do_push_state({});
      this.update_cp();
      this.fetch_data().then(function () {
        self.$(".o_hr_dashboard").empty();
        self.render_dashboards();
      });
    },

    update_cp: function () {
      var self = this;
    },

    // get_emp_image_url: function (employee) {
    //   return (
    //     window.location.origin +
    //     "/web/image?model=hr.employee&field=image_1920&id=" +
    //     employee
    //   );
    // },

    // EVENTS
    // table_data_todays_leave
    table_data_todays_leave: function (e) {
      var self = this;
      var class_name = e.currentTarget.className;
      var split_1 = class_name.split(" ").splice(1).join(" ");
      var split_2 = split_1.split("_");
      var date = new Date().toJSON().slice(0, 10);
      e.stopPropagation();
      e.preventDefault();
      var options = {
        on_reverse_breadcrumb: this.on_reverse_breadcrumb,
      };
      this.do_action(
        {
          name: _t("Candidates Time Off"),
          type: "ir.actions.act_window",
          res_model: "hr.leave",
          view_mode: "tree,form,kanban",
          views: [
            [false, "list"],
            [false, "form"],
          ],
          context: {},
          domain: [
            ["employee_id", "=", split_2[0]],
            ["holiday_status_id", "=", split_2[1]],
            ["date_from".slice(0, 10), "<=", date],
            ["date_to".slice(0, 10), ">=", date],
          ],
          target: "current",
        },
        options
      );
    },
    //END EVENTS
  });

  core.action_registry.add("hr_dashboard", HrDashboard);

  return HrDashboard;
});
