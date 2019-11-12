# coding: utf-8
#
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#
#    Coded by: Luis Ernesto García Medina (ernesto_gm@vauxoo.com)
from odoo.exceptions import UserError
from odoo import models, fields, api, _


class ChangePurchaseLines(models.TransientModel):

    _name = 'change.purchase.line'

    line_ids = fields.Many2many(
        'purchase.order.line',
        string='Lines')
    new_purchase = fields.Boolean(
        'New Order',
        help='Used to create a new purchase '
        'order instead of use an existing')
    purchase_id = fields.Many2one('purchase.order', 'Purchase')
    used_purchase_id = fields.Many2one(
        'purchase.order', 'Purchase', help='Current purchase order')

    @api.model
    def default_get(self, nfields):
        """Added the target ticket"""
        res = super(ChangePurchaseLines, self).default_get(nfields)
        if self.env.context.get('active_id'):
            purchase_id = self.env.context['active_id']
            purchase = self.env['purchase.order'].browse(purchase_id)
            if purchase.state != 'draft':
                raise UserError(
                    _('You can only use this with orders in RFG state'))
            res.update(
                {'used_purchase_id': purchase.id,
                 'line_ids': [(6, 0, purchase.order_line.ids)]}
            )
        return res

    @api.multi
    def apply(self):
        """Changing the lines to a different order"""
        self.ensure_one()
        purchase = self.purchase_id
        if self.new_purchase:
            purchase_id = self.env.context['active_id']
            purchase = self.env['purchase.order'].browse(purchase_id)
            purchase = purchase.copy(
                {'order_line': [],
                 'origin': purchase.origin})
        self.line_ids.write({'order_id': purchase.id})
        action = self.env.ref('purchase.purchase_rfq').read()[0]
        action['views'] = [
            (self.env.ref('purchase.purchase_order_form').id, 'form')]
        action['res_id'] = purchase.id
        return action
