odoo.define('amper.FormController', function (require) {
    "use strict";

    var FormController = require('web.FormController');
    var Sidebar = require('web.Sidebar');
    var core = require('web.core');
    var _t = core._t;

    FormController.include({
        renderSidebar: function ($node) {
        if (this.hasSidebar) {
            var otherItems = [];
            if (this.is_action_enabled('delete')) {
                otherItems.push({
                    label: _t('Delete'),
                    callback: this._onDeleteRecord.bind(this),
                });
            }
            if ((this.is_action_enabled('create') && this.is_action_enabled('duplicate')) || this.modelName === 'sale.order') {
                otherItems.push({
                    label: _t('Duplicate'),
                    callback: this._onDuplicateRecord.bind(this),
                });
            }
            this.sidebar = new Sidebar(this, {
                editable: this.is_action_enabled('edit'),
                viewType: 'form',
                env: {
                    context: this.model.get(this.handle).getContext(),
                    activeIds: this.getSelectedIds(),
                    model: this.modelName,
                },
                actions: _.extend(this.toolbarActions, {other: otherItems}),
            });
            this.sidebar.appendTo($node);

            // Show or hide the sidebar according to the view mode
            this._updateSidebar();
        }
      },
  });
});
