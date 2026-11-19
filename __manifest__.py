{
    'name': 'All In One - Bakery, Pastry & Coffee ERP',
    'version': '20.0.2.0.0',
    'category': 'Sales/Point of Sale',
    'summary': 'Bilingual (EN/AR) OWL 3 ERP Dashboard with n8n-style Automations, Analytics, Production, Expenses, Losses, Purchases, Pastry, Coffee & AI',
    'description': """
All In One Management Suite (Odoo 20)
=====================================
- Bilingual EN / AR interface with automatic LTR / RTL layout switching.
- Simplified, modern minimalist UI with Global Filters.
- Tab 1 (Analytics): KPIs & Chart.js comparison.
- Tab 2 (Production): Daily production entry + Permanent Storable Products Card.
- Tab 3 (Expenses): Pro-rated Daily/Monthly/Annual expenses & Shared split.
- Tab 4 (Losses & Waste): Manual losses + Automatic negative Inventory Adjustments.
- Tab 5 (Purchases): Raw materials linked to final POS products.
- Tab 6 (Pastry & Reconciliation): Price-tier grouping + Smart End-of-Day Stock Deduction.
- Tab 7 (Coffee): Coffee POS revenue, deductions & Net Profit.
- Tab 8 (Accounting & AI): Profit equations + Gemini / OpenRouter Assistant.
- Tab 9 (Automations): Visual n8n-style workflow builder (Reset Stock Qty, Expired Loss, Toggle Storable, Auto-Reconcile, Webhooks, Cron Scheduler).
    """,
    'author': 'Custom',
    'depends': ['base', 'point_of_sale', 'stock', 'mrp', 'purchase', 'web'],
    'data': [
        'security/all_in_one_security.xml',
        'security/ir.access.csv',
        'data/aio_cron.xml',
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
