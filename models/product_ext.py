from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    aio_tracked_card = fields.Boolean(
        string='محفوظ في بطاقة التتبع المخزني (All In One)',
        default=False,
        help='يحفظ المنتج بشكل دائم في بطاقة المنتجات المتتبعة مخزنياً حتى عند إطفاء is_storable.',
    )
    aio_deduction_priority = fields.Integer(
        string='أولوية الخصم التلقائي (Deduction Priority)',
        default=10,
        help='الرقم الأصغر يعني أولوية أعلى عند توزيع المبيعات في جدول تسوية الباتيسري (مثلاً 1 قبل 2).',
    )
    aio_is_generic_price_btn = fields.Boolean(
        string='زر سعر عام في الكاشير (Generic Price Button)',
        default=False,
        help='حدد هذا الخيار إذا كان هذا المنتج يمثل زر سعر عام في الكاشير (مثل زر 1 درهم أو 2 درهم) ليتم توزيع مبيعاته على المنتجات الفعلية التي تحمل نفس السعر.',
    )
    aio_final_product_id = fields.Many2one(
        'product.product',
        string='منتج البيع النهائي المرتبط (للـسلعة/المواد الأولية)',
        help='يربط المادة الأولية القابلة للشراء بمنتج البيع النهائي (مثلاً: دقيق الشعير -> خبز الشعير).',
    )


class ProductProduct(models.Model):
    _inherit = 'product.product'

    aio_tracked_card = fields.Boolean(related='product_tmpl_id.aio_tracked_card', readonly=False, store=True)
    aio_deduction_priority = fields.Integer(related='product_tmpl_id.aio_deduction_priority', readonly=False, store=True)
    aio_is_generic_price_btn = fields.Boolean(related='product_tmpl_id.aio_is_generic_price_btn', readonly=False, store=True)
    aio_final_product_id = fields.Many2one(related='product_tmpl_id.aio_final_product_id', readonly=False, store=True)