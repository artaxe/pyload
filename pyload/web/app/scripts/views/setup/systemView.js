define(['jquery', 'backbone', 'underscore', 'app', 'hbs!tpl/setup/system'],
    function($, Backbone, _, App, template) {
        'use strict';

        return Backbone.Marionette.ItemView.extend({

            name: 'System',
            template: template,

            events: {
            },

            ui: {
            },

            onRender: function() {
            }

        });
    });