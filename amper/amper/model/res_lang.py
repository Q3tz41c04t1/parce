
from odoo import api, models


class LangConfigSetting(models.TransientModel):
    _name = 'lang.config.settings'
    _description = """Wizard to load a language at install/update time"""

    @api.model
    def load_lang(self, code='es_MX'):
        if not self.env.ref('base.lang_%s' % code).active:
            language = self.env['base.language.install']
            language.create({'lang': code}).lang_install()
