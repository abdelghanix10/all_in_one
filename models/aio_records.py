from odoo import models, fields, api


class AioProductionEntry(models.Model):
    _name = 'all_in_one.production.entry'
    _description = 'All In One Daily Production Entry'
    _order = 'date desc, id desc'

    date = fields.Date(string='تاريخ الإنتاج', required=True, default=fields.Date.context_today, index=True)
    product_id = fields.Many2one('product.product', string='المنتج', required=True, ondelete='cascade')
    pos_categ_id = fields.Many2one('pos.category', string='تصنيف نقطة البيع', index=True)
    quantity = fields.Float(string='الكمية المنتجة', required=True, default=0.0)
    unit_price = fields.Float(string='سعر البيع للوحدة', required=True, default=0.0)
    total_sale_value = fields.Float(string='القيمة الإجمالية (بسعر البيع)', compute='_compute_total', store=True)
    stock_move_id = fields.Many2one('stock.move', string='حركة المخزون', ondelete='set null')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    @api.depends('quantity', 'unit_price')
    def _compute_total(self):
        for rec in self:
            rec.total_sale_value = rec.quantity * rec.unit_price


class AioExpense(models.Model):
    _name = 'all_in_one.expense'
    _description = 'All In One Expense'
    _order = 'date desc, id desc'

    name = fields.Char(string='البيان / الوصف', required=True)
    date = fields.Date(string='التاريخ', required=True, default=fields.Date.context_today, index=True)
    expense_type = fields.Selection(
        [
            ('internet', 'إنترنت (Internet)'),
            ('electricity', 'كهرباء (Electricity)'),
            ('water', 'ماء (Water)'),
            ('salaries', 'رواتب العمال (Salaries)'),
            ('monthly_tax', 'ضريبة شهرية (Monthly Tax)'),
            ('annual_tax', 'ضريبة سنوية (Annual Tax)'),
            ('fuel', 'وقود (Fuel)'),
            ('other', 'مصاريف أخرى (Other)'),
        ],
        string='نوع المصروف',
        required=True,
        default='other',
    )
    department = fields.Selection(
        [
            ('pastry', 'باتيسري (Pastry)'),
            ('coffee', 'قهوة (Coffee)'),
            ('shared', 'مشترك (Shared)'),
        ],
        string='القسم',
        required=True,
        default='shared',
    )
    periodicity = fields.Selection(
        [
            ('daily', 'يومي (Daily)'),
            ('monthly', 'شهري (Monthly ÷ 30)'),
            ('annual', 'سنوي (Annual ÷ 365)'),
        ],
        string='دورية المصروف',
        required=True,
        default='daily',
    )
    amount = fields.Float(string='المبلغ (DH)', required=True, default=0.0)
    daily_rate = fields.Float(string='المعدل اليومي (DH/Day)', compute='_compute_daily_rate', store=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    @api.depends('amount', 'periodicity')
    def _compute_daily_rate(self):
        for rec in self:
            if rec.periodicity == 'monthly':
                rec.daily_rate = rec.amount / 30.0
            elif rec.periodicity == 'annual':
                rec.daily_rate = rec.amount / 365.0
            else:
                rec.daily_rate = rec.amount


class AioLoss(models.Model):
    _name = 'all_in_one.loss'
    _description = 'All In One Daily Loss & Waste'
    _order = 'date desc, id desc'

    date = fields.Date(string='التاريخ', required=True, default=fields.Date.context_today, index=True)
    loss_type = fields.Selection(
        [
            ('staff_meals', 'وجبات وفطور العمال'),
            ('damaged', 'مواد تالفة'),
            ('expired', 'منتجات منتهية الصلاحية نهاية اليوم (مثل الخبز)'),
        ],
        string='تصنيف الخسارة',
        required=True,
        default='expired',
    )
    department = fields.Selection(
        [
            ('pastry', 'باتيسري (Pastry)'),
            ('coffee', 'قهوة (Coffee)'),
        ],
        string='القسم',
        required=True,
        default='pastry',
    )
    product_id = fields.Many2one('product.product', string='المنتج (اختياري)')
    pos_categ_id = fields.Many2one('pos.category', string='تصنيف نقطة البيع')
    note = fields.Char(string='ملاحظة / تفاصيل')
    quantity = fields.Float(string='الكمية', required=True, default=1.0)
    unit_value = fields.Float(string='قيمة الوحدة (DH)', required=True, default=0.0)
    total_value = fields.Float(string='إجمالي الخسارة (DH)', compute='_compute_total', store=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    @api.depends('quantity', 'unit_value')
    def _compute_total(self):
        for rec in self:
            rec.total_value = rec.quantity * rec.unit_value


class AioPurchaseEntry(models.Model):
    _name = 'all_in_one.purchase.entry'
    _description = 'All In One Raw Material Purchase / Consumption'
    _order = 'date desc, id desc'

    date = fields.Date(string='التاريخ', required=True, default=fields.Date.context_today, index=True)
    raw_product_id = fields.Many2one(
        'product.product',
        string='السلعة / المادة الأولية',
        domain=[('purchase_ok', '=', True)],
        required=True,
    )
    final_product_id = fields.Many2one('product.product', string='منتج البيع النهائي المرتبط')
    pos_categ_id = fields.Many2one('pos.category', string='تصنيف نقطة البيع')
    department = fields.Selection(
        [
            ('pastry', 'باتيسري (Pastry)'),
            ('coffee', 'قهوة (Coffee)'),
        ],
        string='القسم',
        required=True,
        default='pastry',
    )
    entry_type = fields.Selection(
        [('purchased', 'كمية مشتراة'), ('consumed', 'كمية مستهلكة')],
        string='نوع الحركة',
        default='purchased',
        required=True,
    )
    quantity = fields.Float(string='الكمية', required=True, default=1.0)
    unit_cost = fields.Float(string='تكلفة الوحدة (DH)', required=True, default=0.0)
    total_cost = fields.Float(string='التكلفة الإجمالية (DH)', compute='_compute_total', store=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    @api.depends('quantity', 'unit_cost')
    def _compute_total(self):
        for rec in self:
            rec.total_cost = rec.quantity * rec.unit_cost


class AioPastryReconcile(models.Model):
    _name = 'all_in_one.pastry.reconcile'
    _description = 'Pastry End-of-Day Price Tier Reconciliation'
    _order = 'date desc, price_tier asc'

    date = fields.Date(string='التاريخ', required=True, default=fields.Date.context_today, index=True)
    price_tier = fields.Float(string='فئة السعر (DH)', required=True)
    sold_qty = fields.Float(string='الكمية المباعة في الكاشير', default=0.0)
    state = fields.Selection(
        [('draft', 'مسودة'), ('approved', 'تمت الموافقة'), ('rejected', 'مرفوض')],
        string='الحالة',
        default='draft',
    )
    line_ids = fields.One2many('all_in_one.pastry.reconcile.line', 'reconcile_id', string='التوزيع على المنتجات')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)


class AioPastryReconcileLine(models.Model):
    _name = 'all_in_one.pastry.reconcile.line'
    _description = 'Pastry Reconciliation Product Allocation Line'

    reconcile_id = fields.Many2one('all_in_one.pastry.reconcile', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='المنتج', required=True)
    allocated_qty = fields.Float(string='الكمية المخصومة', default=0.0)
    stock_move_id = fields.Many2one('stock.move', string='حركة خصم المخزون', ondelete='set null')