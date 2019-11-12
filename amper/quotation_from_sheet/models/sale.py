import tempfile
import binascii
import logging
import time
from odoo.exceptions import UserError
from odoo.tools import ustr
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)

try:
    import xlrd
except ImportError as err:
    _logger.debug(err)


class ImportOrder(models.TransientModel):
    _name = "import.order"
    _description = """Wizard to import XLS files as Sale Orders"""

    file = fields.Binary()
    date = fields.Date(
        default=lambda *a: time.strftime('%Y-%m-%d'),
        help="The date that the order will have", required=True)
    order = fields.Char(
        default=lambda s: _('New'),
        help="The number of the new order", required=True)
    partner_id = fields.Many2one('res.partner', required=True)
    user_id = fields.Many2one(
        'res.users', 'Salesman', required=True,
        default=lambda s: s.env.context.get('default_user_id'))
    order_id = fields.Many2one(
        'sale.order',
        help="Order that will be updated. This field is filled automatically "
        "when the Order name already exists on the database."
    )
    pricelist_id = fields.Many2one('product.pricelist')
    template_id = fields.Char(
        'Quotation Template',
        help="Put the name of the template here hand writing")
    opportunity_id = fields.Many2one(
        'crm.lead', required=True,
        default=lambda o: o.env.context.get('default_id'),
        readonly=True,
    )

    @api.onchange('partner_id')
    def onchange_pricelist(self):
        for wizard in self:
            wizard.pricelist_id = wizard.partner_id.property_product_pricelist

    @api.onchange('order')
    def onchange_order(self):
        sale = self.env['sale.order'].search(
            [('name', '=', self.order)], limit=1)
        self.update(dict(order_id=sale, partner_id=sale.partner_id or
                         self.env.context.get('default_partner_id')))

    @api.onchange('order_id')
    def onchange_order_id(self):
        for wizard in self:
            wizard.pricelist_id = wizard.order_id.pricelist_id

    @api.multi
    def get_template(self, name):
        template = self.env['sale.order.template'].search(
            [('name', '=', name)], limit=1)
        if not template:
            raise UserError(_('Template "%s" does not exist') % name)
        return template

    @api.multi
    def do_sale(self):
        if self.order_id:
            return self.order_id
        sale = self.order_id
        values = {
            'name': self.order,
            'partner_id': self.partner_id.id,
            'user_id': self.user_id.id,
            'date_order': self.date,
            'pricelist_id': self.pricelist_id.id,
            'opportunity_id': self.opportunity_id.id,
        }
        try:
            # Just checking if the field exists that why I am entering if it
            # exists or not, but checking if I am explicitly asking to be
            # changed.
            if (sale.sale_order_template_id
                    or not sale.sale_order_template_id) and self.template_id:
                values.update(
                    {'sale_order_template_id':
                     self.get_template(self.template_id).id})
        except AttributeError as err:
            _logger.debug(err)
        sale = self.env['sale.order'].create(values)
        self.order_id = sale
        return sale

    def _prepare_lines(self, sale, sale_lines):
        messages = []
        for values in sale_lines:
            values.update(order_id=sale.id, product_id=False, price_unit=0,
                          product_uom_qty=0, product_uom=False,
                          customer_lead=0)

            if values.get('display_type') == 'line_section':
                continue

            product = self.env['product.product'].search([
                '|', ('default_code', '=ilike', values.get('product')),
                ('name', '=ilike', values.get('product'))], limit=1)
            if not product:
                messages.append(
                    _('Not product found with %s') % values.get('product'))

            product_uom = self.env['uom.uom'].search(
                [('name', '=ilike', values.get('uom'))], limit=1)
            if not product_uom:
                messages.append(
                    _('Not product UOM found with %s') % values.get('uom'))

            if messages:
                continue

            values.update({
                'product_id': product.id,
                'product_uom_qty': values.get('quantity'),
                'price_unit': values.get('price'),
                'name': values.get('name'),
                'product_uom': product_uom.id,
                'order_id': sale.id,
                'customer_lead': values.get('customer_lead'),
                'sequence': values.get('sequence'),
            })

            # Clean no more necessary keys coming from the Excel file
            for key in ['price', 'product', 'quantity', 'uom']:
                if key in values:
                    del values[key]

        if messages:
            raise UserError('\n'.join(messages))

    @api.multi
    def make_order_line(self, values):
        line = self.env['sale.order.line'].create(values)
        line._compute_tax_id()
        if not values.get('price_unit'):
            line.product_uom_change()
        return line

    @api.multi
    def do_import(self):
        if not self.file:
            raise UserError(_("Please upload your file first"))
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as fp:
            fp.write(binascii.a2b_base64(self.file))
            fp.seek(0)
            workbook = xlrd.open_workbook(fp.name)
        sheet = workbook.sheet_by_index(0)
        sale = self.do_sale()
        sale_lines = []
        for num, row in enumerate(sheet.get_rows()):
            if not num:
                continue
            values = {}
            line = [isinstance(c.value, bytes) and ustr(c.value).strip() or
                    str(c.value).strip() for c in row]

            # If only the first row is filled, is a section
            if line[0] and not any(line[1:]):
                values.update(name=line[0],
                              display_type='line_section',
                              sequence=int(num * 10))
                sale_lines.append(values)
                continue

            values.update({
                'product': line[0],
                'name': line[1],
                'quantity': line[2],
                'uom': line[3],
                'sequence': int(num * 10),
                'display_type': False,
            })
            try:
                # Omit price when 0.0 or cell is Empty
                if float(line[4]):
                    values.update({'price': line[4]})
            except (IndexError, ValueError) as err:
                _logger.debug(err)
            try:
                values.update({'customer_lead': line[5]})
            except IndexError:
                values.update({'customer_lead': 0.00})
            sale_lines.append(values)

        self._prepare_lines(sale, sale_lines)
        for values in sale_lines:
            self.make_order_line(values)

        sale._compute_tax_id()
        action = self.env.ref('sale.action_quotations').read()[0]
        action['domain'] = [('id', '=', sale.id)]
        return action
