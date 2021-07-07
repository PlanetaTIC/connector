# Copyright 2021 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    mirakl_export_stock = fields.Boolean('Mirakl Export Stock', default=False)

    def _mirakl_qty(self, conn_mirakl):
        qty = self[conn_mirakl.product_qty_field]
        if qty < 0:
            # make sure we never send negative qty to Mirakl
            qty = 0.0
        return qty
