# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class Lead(models.Model):
    _inherit = "crm.lead"

    number = fields.Char(
        store=True,
        readonly=True,
        copy=False,
        help="Lead Sequence Number",
    )

    @api.model
    def create(self, vals):
        context = dict(self._context or {})
        vals['number'] = self.env.ref('amper.lead_sequence')._next_do()
        res = super(Lead, self.with_context(
            context, mail_create_nolog=True)).create(vals)
        return res
