# Copyright 2021 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Connector Mirakl',
    'version': '12.0.1.0.0',
    'category': 'Connector',
    'summary': "Connector Mirakl",
    'author': 'PlanetaTIC',
    'website': 'https://www.planetatic.com',
    'license': 'AGPL-3',
    'depends': [
        'stock',
        'sale',
        'sales_team',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/mirakl_cron_data.xml',
        'views/connector_mirakl_views.xml',
        'views/product_product_views.xml',
    ],
    'installable': True,
    'auto_install': False
}
