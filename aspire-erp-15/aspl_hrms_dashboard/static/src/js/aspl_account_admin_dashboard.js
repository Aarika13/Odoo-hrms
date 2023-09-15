odoo.define("aspl_hrms_dashboard.AccountDashboardRewrite", function (require) {
  "use strict";

  var AbstractAction = require("web.AbstractAction");
  var core = require("web.core");
  var rpc = require("web.rpc");
  var _t = core._t;
  var QWeb = core.qweb;

  var AccountDashboard = AbstractAction.extend({
    template: "AccountDashboardMain",

    cssLibs: ["/aspl_hrms_dashboard/static/src/css/lib/nv.d3.css"],
    jsLibs: ["/aspl_hrms_dashboard/static/src/js/lib/d3.min.js"],

    events: {
      "click .hr_employee_payroll": "employee_payroll",
    },

    init: function (parent, context) {
      this._super(parent, context);
      this.dashboards_templates = [
        "LoginEmployeeDetails",
        "ManagerDashboard",
        "EmployeeDashboard",
      ];
      this.login_employee = [];
    },

    willStart: function () {
      var self = this;
      this.login_employee = {};
      return this._super().then(function () {
        var def0 = self
          ._rpc({
            model: "hr.employee",
            method: "check_user_group_manager",
          })
          .then(function (result) {
            if (result == true) {
              self.is_manager = true;
            } else {
              self.is_manager = false;
            }
          });
        return $.when(def0);
      });
    },

    start: function () {
      var self = this;
      this.set("title", "AccountDashboard");
      return this._super().then(function () {
        self.render_dashboards();
        self.render_graphs();
        self.$el.parent().addClass("oe_background_grey");
      });
    },

    render_dashboards: function () {
      var self = this;
      if (this.login_employee) {
        var templates = [];
        if (self.is_manager == true) {
          templates = [
            "LoginEmployeeDetails",
            "ManagerDashboard",
            "EmployeeDashboard",
          ];
        } else {
          templates = ["LoginEmployeeDetails", "EmployeeDashboard"];
        }
        _.each(templates, function (template) {
          self
            .$(".o_hr_dashboard")
            .append(QWeb.render(template, { widget: self }));
        });
      } else {
        self
          .$(".o_hr_dashboard")
          .append(QWeb.render("EmployeeWarningAccount", { widget: self }));
      }
    },

    render_graphs: function () {
      var self = this;
      if (this.login_employee) {
        self.render_salary_graph();
        self.render_exp_salary_graph();
        self.render_invoices();
        self.render_bills();
        self.updateEarningExpenseChart();
      }
    },

    render_salary_graph: function () {
      var self = this;
      var w = 150;
      var h = 150;
      var r = h / 2;
      var elem = this.$(".emp_graph");
      var colors = ["#F4B400", "#DB4437", "#AB47BC", "#0F9D58", "#4285F4"];
      var color = d3.scale.ordinal().range(colors);
      rpc
        .query({
          model: "hr.contract",
          method: "salary_range",
        })
        .then(function (data) {
          var segColor = {};
          var vis = d3
            .select(elem[0])
            .append("svg:svg")
            .data([data])
            .attr("width", w)
            .attr("height", h)
            .append("svg:g")
            .attr("transform", "translate(" + r + "," + r + ")");
          var pie = d3.layout.pie().value(function (d) {
            return d.value;
          });
          var arc = d3.svg
            .arc()
            .outerRadius(r)
            .innerRadius(r / 2);
          var arcs = vis
            .selectAll("g.slice")
            .data(pie)
            .enter()
            .append("svg:g")
            .attr("class", "slice");

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
            tooltip.innerHTML = d.data.label + "<br/>" + d.data.value;
          }

          function hideTooltip() {
            tooltip.style.opacity = 0;
          }

          arcs
            .append("svg:path")
            .attr("fill", function (d, i) {
              return color(i);
            })
            .attr("d", function (d) {
              return arc(d);
            })
            .attr("class", function (d, i) {
              return "arc-" + i; // Assign a unique class to each arc
            })
            .on("click", function (d, i) {
              var domain = [];
              tooltip.style.opacity = 0;
              //                        console.log(d);

              if (i === 0) {
                domain = [
                  ["wage", "<", 25000],
                  ["state", "=", "open"],
                ];
              } else if (i === 1) {
                domain = [
                  ["wage", ">=", 25000],
                  ["wage", "<", 50000],
                  ["state", "=", "open"],
                ];
              } else if (i === 2) {
                domain = [
                  ["wage", ">=", 50000],
                  ["wage", "<", 75000],
                  ["state", "=", "open"],
                ];
              } else if (i === 3) {
                domain = [
                  ["wage", ">=", 75000],
                  ["wage", "<", 100000],
                  ["state", "=", "open"],
                ];
              } else if (i === 4) {
                domain = [
                  ["wage", ">=", 100000],
                  ["state", "=", "open"],
                ];
              }

              var context = {
                search_default_domain: domain, // Set the domain in the context for the action
              };

              self.do_action({
                name: _t("Employee Salary"),
                type: "ir.actions.act_window",
                res_model: "hr.contract",
                view_mode: "tree,kanban,form",
                views: [
                  [false, "list"],
                  [false, "kanban"],
                  [false, "form"],
                ],
                context: context,
                target: "current",
                domain: domain, // Pass the domain as a separate property in the action
                search_view_id: d.data.search_id, // Replace with the ID of your desired search view
              });
            })
            .on("mouseover", showTooltip)
            .on("mouseout", hideTooltip);

          arcs
            .append("text")
            .attr("transform", function (d) {
              var c = arc.centroid(d);
              return "translate(" + c[0] + "," + c[1] + ")";
            })
            .attr("dy", ".35em")
            .style("text-anchor", "middle")
            .style("font-size", "12px")
            .text(function (d) {
              var percentage =
                (d.value /
                  d3.sum(data, function (e) {
                    return e.value;
                  })) *
                100;
              if (percentage != 0) {
                return percentage.toFixed(1) + "%";
              }
            });

          var legend = d3
            .select(elem[0])
            .append("table")
            .attr("class", "legend")
            .style("font-size", "12px");

          // create one row per segment.
          var tr = legend
            .append("tbody")
            .selectAll("tr")
            .data(data)
            .enter()
            .append("tr");

          // create the first column for each segment.
          tr.append("td")
            .append("svg")
            .attr("width", "15")
            .attr("height", "15")
            .append("rect")
            .attr("width", "15")
            .attr("height", "15")
            .attr("fill", function (d, i) {
              return color(i);
            });

          // create the second column for each segment.
          tr.append("td").text(function (d) {
            return d.label;
          });

          // create the third column for each segment.
          tr.append("td")
            .attr("class", "legendFreq")
            .text(function (d) {
              return d.value;
            });
        });
    },

    render_exp_salary_graph: function () {
      var self = this;
      var w = 150;
      var h = 150;
      var r = h / 2;
      var elem = this.$(".exp_salary_graph");
      var colors = ["#F4B400", "#DB4437", "#AB47BC", "#0F9D58", "#4285F4"];
      var color = d3.scale.ordinal().range(colors);
      rpc
        .query({
          model: "hr.employee",
          method: "experience_salary_graph",
        })
        .then(function (data) {
          var segColor = {};
          var vis = d3
            .select(elem[0])
            .append("svg:svg")
            .data([data])
            .attr("width", w)
            .attr("height", h)
            .append("svg:g")
            .attr("transform", "translate(" + r + "," + r + ")");
          var pie = d3.layout.pie().value(function (d) {
            return d.value;
          });
          var arc = d3.svg
            .arc()
            .outerRadius(r)
            .innerRadius(r / 2);
          var arcs = vis
            .selectAll("g.slice")
            .data(pie)
            .enter()
            .append("svg:g")
            .attr("class", "slice");

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
            tooltip.innerHTML = d.data.label + "<br/>" + d.data.value;
          }

          function hideTooltip() {
            tooltip.style.opacity = 0;
          }

          arcs
            .append("svg:path")
            .attr("fill", function (d, i) {
              return color(i);
            })
            .attr("d", function (d) {
              return arc(d);
            })
            .attr("class", function (d, i) {
              return "arc-" + i; // Assign a unique class to each arc
            })
            .on("mouseover", showTooltip)
            .on("mouseout", hideTooltip);

          arcs
            .append("text")
            .attr("transform", function (d) {
              var c = arc.centroid(d);
              return "translate(" + c[0] + "," + c[1] + ")";
            })
            .attr("dy", ".35em")
            .style("text-anchor", "middle")
            .style("font-size", "12px")
            .text(function (d) {
              var percentage =
                (d.value /
                  d3.sum(data, function (e) {
                    return e.value;
                  })) *
                100;
              if (percentage != 0) {
                return percentage.toFixed(1) + "%";
              }
            });

          var legend = d3
            .select(elem[0])
            .append("table")
            .attr("class", "legend")
            .style("font-size", "12px");

          // create one row per segment.
          var tr = legend
            .append("tbody")
            .selectAll("tr")
            .data(data)
            .enter()
            .append("tr");

          // create the first column for each segment.
          tr.append("td")
            .append("svg")
            .attr("width", "15")
            .attr("height", "15")
            .append("rect")
            .attr("width", "15")
            .attr("height", "15")
            .attr("fill", function (d, i) {
              return color(i);
            });

          // create the second column for each segment.
          tr.append("td").text(function (d) {
            return d.label;
          });

          // create the third column for each segment.
          tr.append("td")
            .attr("class", "legendFreq")
            .text(function (d) {
              return d.value;
            });
        });
    },

    render_invoices: function () {
      var self = this;
      var w = 150;
      var h = 150;
      var r = h / 2;
      var elem = this.$(".account_invoices");
      var colors = [
        "#93288F",
        "#2C3791",
        "#22A9E2",
        "#1CB572",
        "#059047",
        "#8DC641",
        "#FAB319",
        "#EC2127",
        "#335E90",
        "#1172B9",
        "#0D499C",
        "#056836",
        "#3AB54A",
        "#FBED23",
        "#EE5A25",
        "#C3272C",
      ];
      var color = d3.scale.ordinal().range(colors);
      rpc
        .query({
          model: "account.move",
          method: "invoices",
        })
        .then(function (data) {
          //            console.log(data)
          if (data.length > 0) {
            var emptyGraphDataInvoice = document.getElementsByClassName(
              "empty_graph_data_invoice"
            );
            if (emptyGraphDataInvoice.length > 0) {
              emptyGraphDataInvoice[0].style.display = "none";
            }
            var segColor = {};
            var vis = d3
              .select(elem[0])
              .append("svg:svg")
              .data([data])
              .attr("width", w)
              .attr("height", h)
              .append("svg:g")
              .attr("transform", "translate(" + r + "," + r + ")");
            var pie = d3.layout.pie().value(function (d) {
              return d.value;
            });
            var arc = d3.svg
              .arc()
              .outerRadius(r)
              .innerRadius(r / 2);
            var arcs = vis
              .selectAll("g.slice")
              .data(pie)
              .enter()
              .append("svg:g")
              .attr("class", "slice");

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
              tooltip.innerHTML = d.data.label + "<br/>" + d.data.value;
            }

            function hideTooltip() {
              tooltip.style.opacity = 0;
            }

            arcs
              .append("svg:path")
              .attr("fill", function (d, i) {
                return color(i);
              })
              .attr("d", function (d) {
                return arc(d);
              })
              .attr("class", function (d, i) {
                return "arc-" + i; // Assign a unique class to each arc
              })
              .on("click", function (d, i) {
                var domain = [];
                tooltip.style.opacity = 0;
                domain = [
                  ["invoice_partner_display_name", "=", d.data.label],
                  ["move_type", "=", "out_invoice"],
                  ["amount_residual_signed", "!=", "0"],
                ];

                var context = {
                  search_default_domain: domain,
                };

                self.do_action({
                  name: _t("Invoices"),
                  type: "ir.actions.act_window",
                  res_model: "account.move",
                  view_mode: "tree,kanban,form",
                  views: [
                    [false, "list"],
                    [false, "kanban"],
                    [false, "form"],
                  ],
                  context: context,
                  target: "current",
                  domain: domain,
                  search_view_id: d.data.search_id, // Replace with the ID of your desired search view
                });
              })
              .on("mouseover", showTooltip)
              .on("mouseout", hideTooltip);

            arcs
              .append("text")
              .attr("transform", function (d) {
                var c = arc.centroid(d);
                return "translate(" + c[0] + "," + c[1] + ")";
              })
              .attr("dy", ".35em")
              .style("text-anchor", "middle")
              .style("font-size", "12px")
              .text(function (d) {
                var percentage =
                  (d.value /
                    d3.sum(data, function (e) {
                      return e.value;
                    })) *
                  100;
                return percentage.toFixed(1) + "%";
              });

            var legend = d3
              .select(elem[0])
              .append("table")
              .attr("class", "legend")
              .style("font-size", "12px");

            // create one row per segment.
            var tr = legend
              .append("tbody")
              .selectAll("tr")
              .data(data)
              .enter()
              .append("tr");

            // create the first column for each segment.
            tr.append("td")
              .append("svg")
              .attr("width", "15")
              .attr("height", "15")
              .append("rect")
              .attr("width", "15")
              .attr("height", "15")
              .attr("fill", function (d, i) {
                return color(i);
              });

            // create the second column for each segment.
            tr.append("td").text(function (d) {
              return d.label;
            });

            // create the third column for each segment.
            tr.append("td")
              .attr("class", "legendFreq")
              .text(function (d) {
                return d.value;
              });
          } else {
            var span = document.querySelector(".empty_graph_data_invoice");
            span.appendChild(document.createTextNode("No pending invoices"));
          }
        });
    },

    render_bills: function () {
      var self = this;
      var w = 150;
      var h = 150;
      var r = h / 2;
      var elem = this.$(".account_bills");
      var colors = [
        "#93288F",
        "#2C3791",
        "#22A9E2",
        "#1CB572",
        "#059047",
        "#8DC641",
        "#FAB319",
        "#EC2127",
        "#335E90",
        "#1172B9",
        "#0D499C",
        "#056836",
        "#3AB54A",
        "#FBED23",
        "#EE5A25",
        "#C3272C",
      ];
      var color = d3.scale.ordinal().range(colors);
      rpc
        .query({
          model: "account.move",
          method: "bills",
        })
        .then(function (data) {
          if (data.length > 0) {
            var emptyGraphDataBill = document.getElementsByClassName(
              "empty_graph_data_bill"
            );
            if (emptyGraphDataBill.length > 0) {
              emptyGraphDataBill[0].style.display = "none";
            }

            var segColor = {};
            var vis = d3
              .select(elem[0])
              .append("svg:svg")
              .data([data])
              .attr("width", w)
              .attr("height", h)
              .append("svg:g")
              .attr("transform", "translate(" + r + "," + r + ")");
            var pie = d3.layout.pie().value(function (d) {
              return d.value;
            });
            var arc = d3.svg
              .arc()
              .outerRadius(r)
              .innerRadius(r / 2);
            var arcs = vis
              .selectAll("g.slice")
              .data(pie)
              .enter()
              .append("svg:g")
              .attr("class", "slice");

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
              tooltip.innerHTML = d.data.label + "<br/>" + d.data.value;
            }

            function hideTooltip() {
              tooltip.style.opacity = 0;
            }

            arcs
              .append("svg:path")
              .attr("fill", function (d, i) {
                return color(i);
              })
              .attr("d", function (d) {
                return arc(d);
              })
              .attr("class", function (d, i) {
                return "arc-" + i; // Assign a unique class to each arc
              })
              .on("click", function (d, i) {
                var domain = [];
                tooltip.style.opacity = 0;
                //                        console.log(d)
                domain = [
                  ["invoice_partner_display_name", "=", d.data.label],
                  ["move_type", "=", "in_invoice"],
                  ["amount_residual_signed", "!=", "0"],
                ];

                var context = {
                  search_default_domain: domain,
                };

                self.do_action({
                  name: _t("Bills"),
                  type: "ir.actions.act_window",
                  res_model: "account.move",
                  view_mode: "tree,kanban,form",
                  views: [
                    [false, "list"],
                    [false, "kanban"],
                    [false, "form"],
                  ],
                  context: context,
                  target: "current",
                  domain: domain,
                  search_view_id: d.data.search_id,
                });
              })
              .on("mouseover", showTooltip)
              .on("mouseout", hideTooltip);

            arcs
              .append("text")
              .attr("transform", function (d) {
                var c = arc.centroid(d);
                return "translate(" + c[0] + "," + c[1] + ")";
              })
              .attr("dy", ".35em")
              .style("text-anchor", "middle")
              .style("font-size", "12px")
              .text(function (d) {
                var percentage =
                  (d.value /
                    d3.sum(data, function (e) {
                      return e.value;
                    })) *
                  100;
                return percentage.toFixed(1) + "%";
              });

            var legend = d3
              .select(elem[0])
              .append("table")
              .attr("class", "legend")
              .style("font-size", "12px");

            // create one row per segment.
            var tr = legend
              .append("tbody")
              .selectAll("tr")
              .data(data)
              .enter()
              .append("tr");

            // create the first column for each segment.
            tr.append("td")
              .append("svg")
              .attr("width", "15")
              .attr("height", "15")
              .append("rect")
              .attr("width", "15")
              .attr("height", "15")
              .attr("fill", function (d, i) {
                return color(i);
              });

            // create the second column for each segment.
            tr.append("td").text(function (d) {
              return d.label;
            });

            // create the third column for each segment.
            tr.append("td")
              .attr("class", "legendFreq")
              .text(function (d) {
                return d.value;
              });
          } else {
            var span = document.querySelector(".empty_graph_data_bill");
            span.appendChild(document.createTextNode("No pending bills"));
          }
        });
    },

    updateEarningExpenseChart: function () {
      var elem = this.$(".earning_expense_chart");
      var colors = ["#659d4e", "#DB4437"];
      var color = d3.scale.ordinal().range(colors);

      rpc
        .query({
          model: "hr.employee",
          method: "earning_expense_graph",
        })
        .then(function (data) {
          var margin = { top: 30, right: 10, bottom: 30, left: 30 };
          var width = 550 - margin.left - margin.right;
          var height = 300 - margin.top - margin.bottom;

          // Set the ranges
          var x = d3.scale.ordinal().rangeRoundBands([0, width], 0.35);

          var y = d3.scale.linear().range([height, 0]);

          // Define the axes
          var xAxis = d3.svg.axis().scale(x).orient("bottom");

          var yAxis = d3.svg
            .axis()
            .scale(y)
            .orient("left")
            .ticks(5)
            .tickFormat(function (d) {
              if (d >= 1000 && d < 100000) {
                return d / 1000 + "k";
              } else if (d >= 100000 && d < 10000000) {
                return d / 100000 + "L";
              } else if (d >= 10000000) {
                return d / 10000000 + "cr";
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

          var categoryNames = data.map(function (d) {
            return d.label;
          });
          var monthNames = data[0].value.map(function (d) {
            return d.label;
          });

          x.domain(monthNames);
          y.domain([
            0,
            d3.max(data, function (d) {
              return d3.max(d.value, function (v) {
                return v.value;
              });
            }) * 1.1,
          ]);

          var barWidth = x.rangeBand() / categoryNames.length;

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
            //    tooltip.innerHTML = d.data.label + "<br/>" + d.data.value;
            tooltip.innerHTML = d.value;
          }

          function hideTooltip() {
            tooltip.style.opacity = 0;
          }

          bars
            .selectAll("rect")
            .data(function (d) {
              return d.value;
            })
            .enter()
            .append("rect")
            .attr("x", function (d) {
              return (
                x(d.label) +
                barWidth *
                  categoryNames.indexOf(
                    d3.select(this.parentNode).datum().label
                  )
              );
            })
            .attr("y", function (d) {
              return y(d.value);
            })
            .attr("width", barWidth)
            .attr("height", function (d) {
              return height - y(d.value);
            })
            .style("fill", function (d, i) {
              return color(
                categoryNames.indexOf(d3.select(this.parentNode).datum().label)
              );
            })
            .on("mouseover", showTooltip)
            .on("mouseout", hideTooltip);

          // Add the X Axis
          svg
            .append("g")
            .attr("class", "X axis")
            .attr("transform", "translate(0," + height + ")")
            .call(xAxis);

          // Add the Y Axis
          svg.append("g").attr("class", "Y axis").call(yAxis);

          var legend = d3
            .select(elem[0])
            .append("table")
            .attr("class", "legend")
            .style("font-size", "12px");

          // create one row per segment.
          var tr = legend
            .append("tbody")
            .selectAll("tr")
            .data(data)
            .enter()
            .append("tr");

          // create the first column for each segment.
          tr.append("td")
            .append("svg")
            .attr("width", "15")
            .attr("height", "15")
            .append("rect")
            .attr("width", "15")
            .attr("height", "15")
            .attr("fill", function (d, i) {
              return color(i);
            });

          // create the second column for each segment.
          tr.append("td").text(function (d) {
            return d.label;
          });
        });
    },
  });

  core.action_registry.add("account_dashboard", AccountDashboard);

  return AccountDashboard;
});
