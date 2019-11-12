
from odoo import api, SUPERUSER_ID


def change_paperformat_dpi(env):
    formats = env.ref('base.paperformat_us') + env.ref('base.paperformat_euro')
    formats.write({
        'dpi': '100',
    })


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    change_paperformat_dpi(env)
