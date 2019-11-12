# Copyright 2018 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Instance Creator',
    'summary': '''
    Instance creator for amper. This is the app.
    ''',
    'author': 'Vauxoo',
    'website': 'https://www.vauxoo.com',
    'license': 'AGPL-3',
    'category': 'Installer',
    'version': '12.0.1.0.3',
    'depends': [
        'base_automation',
        'company_country',
        'crm',
        'l10n_mx_edi',
        'l10n_mx_edi_customer_bills',
        'l10n_mx_edi_landing',
        'l10n_mx_edi_vendor_bills',
        'l10n_mx_reports',
        'purchase',
        'project',
        'quotation_from_sheet',
        'sale',
        'stock',
    ],
    'test': [
    ],
    'data': [
        'security/res_groups.xml',
        'data/ir_actions_server.xml',
        'data/res_company.xml',
        'data/res_lang.xml',
        'data/report_paperformat.xml',
        'data/res_currency.xml',
        'data/crm_stage_data.xml',
        'data/ir_sequence.xml',
        'report/sale_report_templates.xml',
        'report/purchase_order_templates.xml',
        'report/external_layout_standard.xml',
        'report/purchase_quotation_templates.xml',
        'views/template.xml',
        'views/account_move.xml',
        'views/sale_quotation_view.xml',
        'views/crm_lead.xml',
        'wizard/change_purchase_lines_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
}
