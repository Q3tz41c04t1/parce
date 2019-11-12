# Copyright 2019 Vauxoo

from odoo import fields, models
from odoo.addons import decimal_precision as dp


class CurrencyRate(models.Model):
    _inherit = 'res.currency.rate'

    rate = fields.Float(digits=dp.get_precision('Rate Precision'))
