# Copyright 2021 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import csv
import requests
from odoo import models, fields, api, exceptions, _
import logging

logger = logging.getLogger(__name__)


class ConnectorMirakl(models.Model):
    _name = 'connector.mirakl'

    active = fields.Boolean(string='Active')
    mirakl_api_key = fields.Char('Mirakl API key')
    mirakl_api_export_stock_url = fields.Char(
        'Mirakl API Export Stock URL')
    mirakl_api_export_stock_api_params = fields.Char(
        'Mirakl Export Stock API Parameters')
    product_qty_field = fields.Selection(selection=[
            ('qty_available_not_res', 'Immediately usable qty'),
            ('qty_available', 'Qty available'),
        ],
        string='Product qty',
        help='Select how you want to calculate the qty to push to Mirakl.',
        default='qty_available',
        required=True,
    )

    @api.constrains('product_qty_field')
    def check_product_qty_field_dependencies_installed(self):
        for mirakl in self:
            # we only support stock_available_unreserved module for now.
            # In order to support stock_available_immediately or
            # virtual_available for example, we would need to recompute
            # the mirakl qty at stock move level, it can't work to
            # recompute it only at quant level, like it is done today
            if mirakl.product_qty_field == 'qty_available_not_res':
                module = self.env['ir.module.module'].sudo().search(
                    [('name', '=', 'stock_available_unreserved')], limit=1)
                if not module or module.state != 'installed':
                    raise exceptions.UserError(
                        _('In order to choose this option, you have to '
                          'install the module stock_available_unreserved.'))

    @api.multi
    def cron_export_stock_mirakl(self):
        mirakl_conns = self.search([])
        for mirakl_conn in mirakl_conns:
            mirakl_conn.export_stock_mirakl()
        return True

    def _get_stock_mirakl_file(self):
        product_obj = self.env['product.product']

        filename = '/tmp/mirakl_stock_exportation.csv'

        # search products to export
        products = product_obj.search([
            ('mirakl_export_stock', '=', True),
        ])

        if not products:
            return False

        with open(filename, 'w', encoding='UTF8') as f:
            writer = csv.writer(f)

            # write the header
            writer.writerow(['sku', 'quantity'])

            # write the data
            for product in products:
                product_key = product.default_code or product.barcode
                quantity = product._mirakl_qty(self)

                writer.writerow([product_key, quantity])
        return filename

    @api.multi
    def export_stock_mirakl(self):
        self.ensure_one()

        csv_file = self._get_stock_mirakl_file()
        if not csv_file:
            return False

        try:
            # construct URL:
            url = '%s?api_key=%s' % (
                self.mirakl_api_export_stock_url, self.mirakl_api_key)
            if self.mirakl_api_export_stock_api_params:
                url += '&%s' % self.mirakl_api_export_stock_api_params

            response = requests.post(
                url, files={'file': open(csv_file, 'rb')})
            response.content
        except Exception as e:
            logger.exception(
                _('An error has occurred API Mirakl\n%s') % str(e))
            raise
        return True
