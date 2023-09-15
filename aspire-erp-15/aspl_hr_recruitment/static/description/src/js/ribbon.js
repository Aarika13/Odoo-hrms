odoo.define('web.ribbonInherit', function (require) {
    'use strict';

    var widgetRegistry = require('web.widget_registry');
    var Widget = require('web.Widget');

    var RibbonWidget = Widget.extend({
        template: 'web.ribbon',
        xmlDependencies: ['/web/static/src/legacy/xml/ribbon.xml'],

        /**
         * @param {Object} options
         * @param {string} options.attrs.title
         * @param {string} options.attrs.text same as title
         * @param {string} options.attrs.tooltip
         * @param {string} options.attrs.bg_color
         */
        init: function (parent, data, options) {
            this._super.apply(this, arguments);
            this.text = options.attrs.title || options.attrs.text;
            this.tooltip = options.attrs.tooltip;
            this.className = options.attrs.bg_color ? options.attrs.bg_color : 'bg-success';
            console.log("this.text.length == ",this.text.length);
            if (this.text.length >= 14 && this.text.length < 16) {
                console.log("False");
                this.className += ' o_small';
            }else if (this.text.length > 10) {
                console.log("True");
                this.className += ' o_medium';
            }
        },
    });

    widgetRegistry.add('web_ribbon', RibbonWidget);

    return RibbonWidget;
});
