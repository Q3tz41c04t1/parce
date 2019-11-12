{
    'name': 'Quotations from Sheet',
    'version': '12.0.0.0.2',
    'summary': 'Import Quotations from an Excel Sheet',
    'category': 'Sales',
    'author': 'Vauxoo',
    'website': 'http://www.vauxoo.com',
    'license': 'LGPL-3',
    'live_test_url': 'https://www.vauxoo.com/r/quotation_from_sheet',
    'depends': ['base', 'sale', 'crm'],
    'data': ["view/sale.xml"],
    'external_dependencies': {
        'python': ['xlrd'],
    },
    'installable': True,
}
