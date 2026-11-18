{
    'name': 'All In One - Bakery, Pastry & Coffee ERP',
    'version': '20.0.1.0.0',
    'category': 'Sales/Point of Sale',
    'summary': 'Unified OWL 3 Dashboard for Analytics, Production, Expenses, Losses, Purchases, Pastry Reconciliation, Coffee & AI',
    'description': """
All In One Management Suite (Odoo 20)
=====================================
- Unified Global Filters: Date Presets (Today, Yesterday, This Week, Last Week, Custom), POS Register, POS Category.
- Configuration: Pastry/Coffee/Production categories, Shared Expense split %, Google Gemini & OpenRouter API integration.
- Tab 1 (Analytics): Comprehensive KPIs & Chart.js visualizations.
- Tab 2 (Production): Daily production entry by POS Category + Permanent Storable Products Card with 1-click `is_storable` toggle.
- Tab 3 (Expenses): Daily/Monthly/Annual expenses with automatic pro-rating and Pastry/Coffee/Shared allocation.
- Tab 4 (Losses & Waste): Manual losses (Staff meals, Damaged, Expired) + Automatic negative Inventory Adjustment detection.
- Tab 5 (Raw Materials & Purchases): Purchasable items linked to final POS products with purchase/consumption cost tracking.
- Tab 6 (Pastry POS & Reconciliation): Price-tier grouping (0.5 DH, 1 DH, 2 DH...), Net Profit, and Smart End-of-Day Stock Deduction Table.
- Tab 7 (Coffee POS): Coffee POS revenue, expense/loss/purchase deductions, and Net Profit.
- Tab 8 (Accounting & AI Insights): Detailed profit equations + Interactive AI Assistant powered by Gemini & OpenRouter.
    """,
    'author': 'Custom',
    'depends': ['base', 'point_of_sale', 'stock', 'mrp', 'purchase', 'web'],
    'data': [
        'security/all_in_one_security.xml',
        'security/ir.access.csv',
        'views/aio_menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'https://cdn.jsdelivr.net/npm/chart.js',
            'all_in_one/static/src/scss/all_in_one.scss',
            'all_in_one/static/src/xml/all_in_one_dashboard.xml',
            'all_in_one/static/src/js/all_in_one_dashboard.js',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}