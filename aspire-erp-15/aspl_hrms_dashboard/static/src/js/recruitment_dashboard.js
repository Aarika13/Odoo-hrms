odoo.define(
  "aspl_hrms_dashboard.RecruitmentDashboardRewrite",
  function (require) {
    "use strict";

    var AbstractAction = require("web.AbstractAction");
    var core = require("web.core");
    var web_client = require("web.web_client");
    var rpc = require("web.rpc");
    var _t = core._t;
    var QWeb = core.qweb;

    var RecruitmentDashboard = AbstractAction.extend({
      template: "RecruitmentDashboardMain",

      cssLibs: ["/aspl_hrms_dashboard/static/src/css/lib/nv.d3.css"],
      jsLibs: ["/aspl_hrms_dashboard/static/src/js/lib/d3.min.js"],

      events: {
        "click .table_data_job_applications": "table_data_job_applications",
        "click .table_data_candidates_activity":
          "table_data_candidates_activity",
        "click .first_div_first_section_recruitment_personal_activity_boxes":
          "first_div_first_section_recruitment_personal_activity_boxes",
      },

      init: function (parent, context) {
        this._super(parent, context);
        this.dashboards_templates = ["RecruitmentDashboard"];
        this.login_employee = [];
      },

      willStart: function () {
        var self = this;
        this.login_employee = {};
        return this._super().then(function () {
          var def0 = self
            ._rpc({
              model: "hr.employee",
              method: "check_user_group_recruitment",
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
              method: "get_user_employee_details_recruitment",
            })
            .then(function (result) {
              self.login_employee = result;
            });
          return $.when(def0, def1);
        });
      },

      start: function () {
        var self = this;
        this.set("title", "RecruitmentDashboard");
        return this._super().then(function () {
          self.update_cp();
          self.render_dashboards();
          self.render_graphs();
          self.$el.parent().addClass("oe_background_grey");
        });
      },

      fetch_data: function () {
        var self = this;
        var def0 = self
          ._rpc({
            model: "hr.employee",
            method: "check_user_group_recruitment",
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
          method: "get_user_employee_details_recruitment",
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
            templates = ["RecruitmentDashboard"];
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
            .append(
              QWeb.render("EmployeeWarningRecruitment", { widget: self })
            );
        }
      },

      render_graphs: function () {
        var self = this;
        if (this.login_employee) {
          self.recruitment_cost_bar_chart();
        }
      },

      on_reverse_breadcrumb: function () {
        var self = this;
        web_client.do_push_state({});
        this.update_cp();
        this.fetch_data().then(function () {
          self.$(".o_hr_dashboard").empty();
          self.render_dashboards();
          self.render_graphs();
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
      // table_data_job_applications
      table_data_job_applications: function (e) {
        var self = this;
        var class_name = e.currentTarget.className;
        var split_1 = class_name.split(" ").splice(1).join(" ");
        var split_2 = split_1.split("_");
        e.stopPropagation();
        e.preventDefault();
        var options = {
          on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action(
          {
            name: _t("Applications"),
            type: "ir.actions.act_window",
            res_model: "hr.applicant",
            view_mode: "tree,form,kanban",
            views: [
              [false, "list"],
              [false, "form"],
            ],
            context: {},
            domain: [
              ["stage_id", "=", split_2[1]],
              ["job_opening_id", "=", split_2[0]],
            ],
            target: "current",
          },
          options
        );
      },

      // table_data_candidates_activity
      table_data_candidates_activity: function (e) {
        var self = this;
        var class_name = e.currentTarget.className;
        var split_1 = class_name.split(" ").splice(1).join(" ");
        var split_2 = split_1.split("_");
        var date = new Date().toJSON();
        e.stopPropagation();
        e.preventDefault();
        var options = {
          on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action(
          {
            name: _t("Aspire Candidates Activity"),
            type: "ir.actions.act_window",
            res_model: "mail.activity",
            view_mode: "tree,form,kanban",
            views: [
              [false, "list"],
              [false, "form"],
            ],
            context: {},
            domain: [
              ["res_model", "=", "hr.applicant"],
              ["user_id", "=", split_2[0]],
              ["date_deadline", ">=", date],
              ["activity_type_id", "=", split_2[1]],
            ],
            target: "current",
          },
          options
        );
      },

      // first_div_first_section_recruitment_personal_activity_boxes
      first_div_first_section_recruitment_personal_activity_boxes: function (
        e
      ) {
        var self = this;
        var class_name = e.currentTarget.className;
        var split_1 = class_name.split(
          " first_div_first_section_recruitment_personal_activity_boxes"
        );
        var date = new Date().toJSON();
        e.stopPropagation();
        e.preventDefault();
        var options = {
          on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action(
          {
            name: _t("My Activity"),
            type: "ir.actions.act_window",
            res_model: "mail.activity",
            view_mode: "tree,form,kanban",
            views: [
              [false, "list"],
              [false, "form"],
            ],
            context: {},
            domain: [
              ["res_model", "=", "hr.applicant"],
              ["user_id", "=", this.login_employee.display_name],
              ["activity_type_id", "=", split_1[0]],
              ["date_deadline", ">=", date],
            ],
            target: "current",
          },
          options
        );
      },

      //END EVENTS

      // GRAPHS
      // Recruitment Cost Bar Chart
      recruitment_cost_bar_chart: function () {
        var elem = this.$(".recruitment_cost_graph");
        var colors = ["#71639e"];
        var color = d3.scale.ordinal().range(colors);

        rpc
          .query({
            model: "hr.employee",
            method: "recruitment_cost_bar_chart_method",
          })
          .then(function (data) {
            var margin = { top: 30, right: 30, bottom: 80, left: 45 };
            var width = 550 - margin.left - margin.right;
            var height = 400 - margin.top - margin.bottom;

            if (data.length == 1) {
              var x = d3.scale.ordinal().rangeRoundBands([0, width], 0.849);
            } else if (data.length == 2) {
              var x = d3.scale.ordinal().rangeRoundBands([0, width], 0.76);
            } else if (data.length == 3) {
              var x = d3.scale.ordinal().rangeRoundBands([0, width], 0.681);
            } else if (data.length == 4) {
              var x = d3.scale.ordinal().rangeRoundBands([0, width], 0.502);
            } else if (data.length < 11) {
              var x = d3.scale
                .ordinal()
                .rangeRoundBands([0, width], 1 - 0.1 * data.length);
            } else {
              var x = d3.scale.ordinal().rangeRoundBands([0, width], 0.09);
            }
            var y = d3.scale.linear().range([height, 0]);

            var xAxis = d3.svg.axis().scale(x).orient("bottom");
            var yAxis = d3.svg
              .axis()
              .scale(y)
              .orient("left")
              .ticks(5)
              .tickFormat(function (d) {
                if (d >= 1000 && d < 100000) {
                  return d / 1000 + "k";
                } else if (d >= 100000) {
                  return d / 100000 + "L";
                } else {
                  return d;
                }
              });

            var svg = d3
              .select(elem[0])
              .append("svg")
              .attr("width", width + margin.left + margin.right)
              .attr("height", height + margin.top + margin.bottom)
              .append("g")
              .attr(
                "transform",
                "translate(" + margin.left + "," + margin.top + ")"
              );

            var xNames = data.map(function (d) {
              return d[0];
            });
            var yNames = data.map(function (d) {
              return d[1];
            });

            x.domain(xNames);
            y.domain([0, d3.max(yNames) * 1.2]);

            var barWidth = 40;

            var bars = svg
              .selectAll(".bar")
              .data(data)
              .enter()
              .append("g")
              .attr("class", "bar");

            // Create the tooltip element
            var tooltip = document.createElement("div");
            tooltip.id = "tooltip";
            tooltip.style.position = "absolute";
            tooltip.style.pointerEvents = "none";
            tooltip.style.backgroundColor = "rgba(0, 0, 0, 0.8)";
            tooltip.style.color = "white";
            tooltip.style.padding = "8px";
            tooltip.style.fontSize = "12px";
            tooltip.style.borderRadius = "4px";
            tooltip.style.opacity = 0;
            tooltip.style.textAlign = "center";

            // Append the tooltip to the body element
            document.body.appendChild(tooltip);

            // Function to show/hide the tooltip
            function showTooltip(d) {
              tooltip.style.opacity = 1;
              tooltip.style.left =
                d3.event.pageX - tooltip.offsetWidth / 2 + "px";
              tooltip.style.top =
                d3.event.pageY - tooltip.offsetHeight / 2 + "px";
              tooltip.innerHTML =
                "Cost :- " +
                parseInt(d[1]) +
                "<br/>" +
                "Hire Candidates :- " +
                d[2];
            }

            function hideTooltip() {
              tooltip.style.opacity = 0;
            }

            bars
              .selectAll("rect")
              .data(function (d) {
                return [d];
              })
              .enter()
              .append("rect")
              .attr("x", function (d) {
                return x(d[0]);
              })
              .attr("y", function (d) {
                return y(d[1]);
              })
              .attr("width", barWidth)
              .attr("height", function (d) {
                return height - y(d[1]);
              })
              .style("fill", function (d, i) {
                return color(
                  xNames.indexOf(d3.select(this.parentNode).datum().label)
                );
              })
              .on("mouseover", showTooltip)
              .on("mouseout", hideTooltip);

            svg
              .attr("class", "x axis")
              .append("g")
              .attr("transform", "translate(0," + height + ")")
              .call(xAxis)
              .selectAll("text")
              .style("text-anchor", "end")
              .attr("transform", "rotate(-21)");

            svg.attr("class", "y axis").append("g").call(yAxis);
          });
      },

      //END GRAPHS
    });

    core.action_registry.add("recruitment_dashboard", RecruitmentDashboard);

    return RecruitmentDashboard;
  }
);
