from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AllInOneSettings(models.Model):
    _name = 'all_in_one.settings'
    _description = 'All In One Global Configuration'

    name = fields.Char(default='All In One Configuration', required=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    # POS Categories Mapping
    pastry_categ_ids = fields.Many2many(
        'pos.category',
        'aio_settings_pastry_categ_rel',
        'setting_id',
        'categ_id',
        string='تصنيفات الباتيسري (Pastry Categories)',
    )
    coffee_categ_ids = fields.Many2many(
        'pos.category',
        'aio_settings_coffee_categ_rel',
        'setting_id',
        'categ_id',
        string='تصنيفات القهوة (Coffee Categories)',
    )
    production_categ_ids = fields.Many2many(
        'pos.category',
        'aio_settings_prod_categ_rel',
        'setting_id',
        'categ_id',
        string='تصنيفات شاشة الإنتاج (Production Categories)',
    )

    # POS Registers Mapping
    pastry_config_ids = fields.Many2many(
        'pos.config',
        'aio_settings_pastry_pos_rel',
        'setting_id',
        'config_id',
        string='كاشير الباتيسري (Pastry POS Registers)',
    )
    coffee_config_ids = fields.Many2many(
        'pos.config',
        'aio_settings_coffee_pos_rel',
        'setting_id',
        'config_id',
        string='كاشير القهوة (Coffee POS Registers)',
    )

    # Shared Expense Split %
    shared_pastry_pct = fields.Float(string='نسبة الباتيسري من المصاريف المشتركة (%)', default=50.0)
    shared_coffee_pct = fields.Float(string='نسبة القهوة من المصاريف المشتركة (%)', default=50.0)

    # AI Integration (Gemini & OpenRouter)
    ai_provider = fields.Selection(
        [('gemini', 'Google Gemini'), ('openrouter', 'OpenRouter')],
        string='مزود الذكاء الاصطناعي الافتراضي',
        default='gemini',
    )
    gemini_api_key = fields.Char(string='Google Gemini API Key')
    gemini_model = fields.Char(string='Gemini Model', default='gemini-2.5-flash')
    openrouter_api_key = fields.Char(string='OpenRouter API Key')
    openrouter_model = fields.Char(string='OpenRouter Model', default='google/gemini-2.5-flash')

    @api.constrains('shared_pastry_pct', 'shared_coffee_pct')
    def _check_shared_percentages(self):
        for rec in self:
            if round(rec.shared_pastry_pct + rec.shared_coffee_pct, 2) != 100.0:
                raise ValidationError(_("مجموع نسب توزيع المصاريف المشتركة بين الباتيسري والقهوة يجب أن يساوي 100%."))

    @api.model
    def get_singleton(self):
        rec = self.sudo().search([('company_id', '=', self.env.company.id)], limit=1)
        if not rec:
            rec = self.sudo().create({'name': 'All In One Configuration'})
        return rec