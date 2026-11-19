/** @odoo-module */

import { Component, onWillStart, proxy, useProps } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

const TRANSLATIONS = {
    en: {
        app_title: "All In One",
        days: "d",
        today: "Today",
        yesterday: "Yesterday",
        this_week: "This Week",
        last_week: "Last Week",
        from: "From",
        to: "To",
        all_pos: "All POS Registers",
        all_categories: "All Categories",
        // Tabs
        tab_analytics: "Overview",
        tab_production: "Production",
        tab_expenses: "Expenses",
        tab_losses: "Losses",
        tab_purchases: "Purchases",
        tab_pastry: "Pastry",
        tab_coffee: "Coffee",
        tab_accounting_ai: "Accounting & AI",
        tab_automations: "Automations",
        tab_settings: "Settings",
        // KPIs
        kpi_sales: "Total Sales",
        kpi_production: "Production Value",
        kpi_expenses: "Period Expenses",
        kpi_losses: "Total Losses",
        kpi_purchases: "Raw Materials",
        kpi_net_profit: "Net Profit",
        chart_title: "Financial Comparison — Pastry vs Coffee",
        pastry: "Pastry",
        coffee: "Coffee",
        shared: "Shared",
        // Production
        daily_production: "Daily Production",
        save_production: "Save Production",
        product: "Product",
        sale_price: "Price",
        stock: "On Hand",
        qty_produced: "Produced Qty",
        tracked_card_title: "Tracked Stock Card",
        tracked_card_desc: "Products stay pinned here. Toggle stock tracking (is_storable) for all of them in one click.",
        disable_all_stock: "Pause All Tracking",
        enable_all_stock: "Enable All Tracking",
        pick_storable: "Add storable product...",
        add: "Add",
        status: "Status",
        active_badge: "Active",
        paused_badge: "Paused",
        // Expenses
        expenses_title: "Expenses & Auto Pro-Rating",
        description: "Description",
        expense_placeholder: "e.g. Electricity bill",
        type: "Type",
        department: "Department",
        periodicity: "Periodicity",
        amount: "Amount (DH)",
        daily_rate: "Daily Rate",
        period_cost: "Period Cost",
        pastry_share: "Pastry Share",
        coffee_share: "Coffee Share",
        exp_internet: "Internet",
        exp_electricity: "Electricity",
        exp_water: "Water",
        exp_salaries: "Salaries",
        exp_monthly_tax: "Monthly Tax",
        exp_annual_tax: "Annual Tax",
        exp_fuel: "Fuel",
        exp_other: "Other",
        per_daily: "Daily",
        per_monthly: "Monthly (÷30)",
        per_annual: "Annual (÷365)",
        // Losses
        manual_losses_title: "Daily Losses & Waste",
        auto_losses_title: "Automatic Inventory Adjustment Shortages",
        date: "Date",
        loss_type: "Loss Type",
        loss_staff_meals: "Staff Meals",
        loss_damaged: "Damaged Goods",
        loss_expired: "Expired (End of Day)",
        select_product: "Select product...",
        qty: "Qty",
        unit_value: "Unit Value",
        total: "Total",
        record: "Record",
        missing_qty: "Missing Qty",
        // Purchases
        purchases_title: "Raw Materials & Purchases",
        raw_material: "Raw Material",
        select_raw: "Select raw material...",
        unit_cost: "Unit Cost",
        total_cost: "Total Cost",
        save: "Save",
        category: "Category",
        final_product: "Linked Final Product",
        // Pastry
        pastry_prod_val: "Pastry Production",
        pastry_sales: "Pastry POS Sales",
        pastry_costs: "Expenses + Losses + Materials",
        pastry_net: "Pastry Net Profit",
        reconcile_title: "End-of-Day Price-Tier Stock Reconciliation",
        col_tier: "Price Tier & POS Sold",
        col_products: "Products & Allocation (Priority → Highest Stock, Never ≤ 0)",
        col_diff: "Variance",
        col_actions: "Actions",
        tier_label: "Tier",
        sold_pos: "POS Sold",
        produced: "Produced",
        priority: "Priority",
        deduct_qty: "Deduct Qty",
        allocated: "Allocated",
        diff: "Diff",
        approved_badge: "Approved",
        approve: "Approve",
        edit: "Edit",
        reject: "Reject",
        // Coffee
        coffee_title: "Coffee Department Summary",
        coffee_sales: "Coffee POS Sales",
        coffee_expenses: "Coffee Expenses (+ Shared)",
        coffee_losses_purch: "Losses + Raw Materials",
        coffee_net: "Coffee Net Profit",
        // Accounting & AI
        equations_title: "Profit Equations",
        pastry_eq: "Pastry Net Profit = Sales − Expenses − Losses − Materials",
        coffee_eq: "Coffee Net Profit = Sales − Expenses − Losses − Materials",
        total_eq: "Total Net Profit (Pastry + Coffee)",
        ai_title: "AI Financial Advisor",
        ai_btn_1: "Analyze Pastry Gaps & Waste",
        ai_btn_2: "Compare Pastry vs Coffee Profit",
        ai_placeholder: "Ask the AI about your current period metrics...",
        ai_send: "Analyze Period Data",
        ai_thinking: "Analyzing...",
        ai_default_prompt: "Analyze current profit and losses and suggest 3 practical steps to boost net profit and reduce waste.",
        ai_prompt_1: "Analyze the gap between pastry production and POS sales and suggest ways to reduce end-of-day waste.",
        ai_prompt_2: "Compare Pastry vs Coffee profitability and propose a plan to increase net profit by 15%.",
        // Automations (n8n-style)
        auto_workflows: "Workflows",
        auto_new: "New Workflow",
        auto_templates: "Quick Templates",
        auto_run_now: "Run Now",
        auto_running: "Running...",
        auto_delete: "Delete",
        auto_workflow_name: "Workflow Name",
        auto_trigger_node: "Trigger",
        auto_action_node: "Action",
        auto_add_node: "Add Action Node",
        auto_select_hint: "Select a workflow on the left or create a new one from a template.",
        auto_logs_title: "Recent Execution Logs",
        auto_no_logs: "No runs yet.",
        trig_manual: "Manual (Run Now only)",
        trig_daily: "Daily Schedule",
        trig_weekly: "Weekly Schedule",
        trig_interval: "Every N Hours",
        run_at: "Run At",
        weekday: "Day",
        every_hours: "Every (Hours)",
        act_reset_qty: "Reset Product Quantities",
        act_expired_loss: "Stock → Expired Loss + Zero",
        act_toggle_storable: "Toggle Tracked Card Stock",
        act_reconcile: "Auto-Approve Pastry Reconciliation",
        act_expense: "Log Scheduled Expense",
        act_prices: "Bulk Adjust Prices",
        act_kpi: "Daily KPI Snapshot",
        act_webhook: "HTTP Webhook (n8n / Telegram)",
        scope: "Target Scope",
        scope_all: "All Storable Products",
        scope_tracked: "Tracked Stock Card Products",
        scope_categ: "Specific POS Category",
        target_qty: "Set Quantity To",
        storable_action: "Set Stock Tracking",
        turn_on: "Turn ON (is_storable = True)",
        turn_off: "Turn OFF (is_storable = False)",
        webhook_url: "Webhook POST URL",
        webhook_msg: "Custom Note",
        price_mode: "Mode",
        percent: "Percent (%)",
        fixed_dh: "Fixed (DH)",
        value: "Value",
        // Settings
        settings_title: "General Configuration",
        save_settings: "Save Settings",
        set_pastry_cat: "Pastry POS Categories",
        set_coffee_cat: "Coffee POS Categories",
        set_prod_cat: "Production POS Categories",
        set_split: "Shared Expense Split (%)",
        set_pastry_pct: "Pastry (%)",
        set_coffee_pct: "Coffee (%)",
        set_ai: "AI Provider (Gemini / OpenRouter)",
        active_provider: "Active Provider",
        // Notifications
        notif_saved: "Saved successfully",
        notif_prod_saved: "Production saved & stock updated",
        notif_wf_saved: "Workflow saved",
        notif_wf_ran: "Workflow executed",
        notif_reconciled: "Approved & stock deducted",
        notif_stock_on: "Stock tracking enabled for all card products",
        notif_stock_off: "Stock tracking paused for all card products",
    },
    ar: {
        app_title: "All In One",
        days: "يوم",
        today: "اليوم",
        yesterday: "البارحة",
        this_week: "هذا الأسبوع",
        last_week: "الأسبوع الماضي",
        from: "من",
        to: "إلى",
        all_pos: "كل نقاط البيع",
        all_categories: "كل التصنيفات",
        // Tabs
        tab_analytics: "التحليلات",
        tab_production: "الإنتاج",
        tab_expenses: "المصاريف",
        tab_losses: "الخسائر",
        tab_purchases: "السلعة",
        tab_pastry: "الباتيسري",
        tab_coffee: "القهوة",
        tab_accounting_ai: "الحساب و AI",
        tab_automations: "الأتمتة",
        tab_settings: "الإعدادات",
        // KPIs
        kpi_sales: "إجمالي المبيعات",
        kpi_production: "قيمة الإنتاج",
        kpi_expenses: "المصاريف للفترة",
        kpi_losses: "إجمالي الخسائر",
        kpi_purchases: "تكلفة السلعة",
        kpi_net_profit: "صافي الربح",
        chart_title: "مقارنة الأداء المالي — الباتيسري مقابل القهوة",
        pastry: "الباتيسري",
        coffee: "القهوة",
        shared: "مشترك",
        // Production
        daily_production: "إدخال الإنتاج اليومي",
        save_production: "حفظ الإنتاج",
        product: "المنتج",
        sale_price: "السعر",
        stock: "المخزون",
        qty_produced: "الكمية المنتجة",
        tracked_card_title: "بطاقة تتبع المخزون",
        tracked_card_desc: "المنتجات تبقى محفوظة هنا بشكل دائم مع إمكانية إيقاف أو تفعيل تتبع المخزون (is_storable) بضغطة واحدة.",
        disable_all_stock: "إيقاف التتبع للكل",
        enable_all_stock: "تفعيل التتبع للكل",
        pick_storable: "إضافة منتج متتبع...",
        add: "إضافة",
        status: "الحالة",
        active_badge: "مفعل",
        paused_badge: "متوقف",
        // Expenses
        expenses_title: "المصاريف والتوزيع التلقائي",
        description: "البيان",
        expense_placeholder: "مثال: فاتورة الكهرباء",
        type: "النوع",
        department: "القسم",
        periodicity: "الدورية",
        amount: "المبلغ (DH)",
        daily_rate: "المعدل اليومي",
        period_cost: "تكلفة الفترة",
        pastry_share: "حصة الباتيسري",
        coffee_share: "حصة القهوة",
        exp_internet: "إنترنت",
        exp_electricity: "كهرباء",
        exp_water: "ماء",
        exp_salaries: "رواتب",
        exp_monthly_tax: "ضريبة شهرية",
        exp_annual_tax: "ضريبة سنوية",
        exp_fuel: "وقود",
        exp_other: "أخرى",
        per_daily: "يومي",
        per_monthly: "شهري (÷30)",
        per_annual: "سنوي (÷365)",
        // Losses
        manual_losses_title: "الخسائر والهدر اليومي",
        auto_losses_title: "نواقص تسويات الجرد التلقائية",
        date: "التاريخ",
        loss_type: "نوع الخسارة",
        loss_staff_meals: "وجبات العمال",
        loss_damaged: "مواد تالفة",
        loss_expired: "منتهية الصلاحية نهاية اليوم",
        select_product: "اختر منتجاً...",
        qty: "الكمية",
        unit_value: "قيمة الوحدة",
        total: "الإجمالي",
        record: "تسجيل",
        missing_qty: "الكمية المفقودة",
        // Purchases
        purchases_title: "السلعة والمواد الأولية",
        raw_material: "المادة الأولية",
        select_raw: "اختر السلعة...",
        unit_cost: "تكلفة الوحدة",
        total_cost: "الإجمالي",
        save: "حفظ",
        category: "التصنيف",
        final_product: "منتج البيع المرتبط",
        // Pastry
        pastry_prod_val: "إنتاج الباتيسري",
        pastry_sales: "مبيعات كاشير الباتيسري",
        pastry_costs: "مصاريف + خسائر + سلعة",
        pastry_net: "صافي ربح الباتيسري",
        reconcile_title: "تسوية المخزون الذكية نهاية اليوم حسب السعر",
        col_tier: "فئة السعر والمبيعات",
        col_products: "المنتجات والتوزيع (الأولوية ثم الأكبر مخزوناً، ممنوع ≤ 0)",
        col_diff: "الفارق",
        col_actions: "الإجراءات",
        tier_label: "فئة",
        sold_pos: "مباع بالكاشير",
        produced: "المنتج",
        priority: "الأولوية",
        deduct_qty: "الخصم",
        allocated: "الموزع",
        diff: "الفارق",
        approved_badge: "تمت الموافقة",
        approve: "موافقة",
        edit: "تعديل",
        reject: "رفض",
        // Coffee
        coffee_title: "ملخص قسم القهوة",
        coffee_sales: "مبيعات كاشير القهوة",
        coffee_expenses: "مصاريف القهوة (+ المشترك)",
        coffee_losses_purch: "الخسائر + تكلفة السلعة",
        coffee_net: "صافي ربح القهوة",
        // Accounting & AI
        equations_title: "معادلات الأرباح",
        pastry_eq: "صافي ربح الباتيسري = المبيعات − المصاريف − الخسائر − السلعة",
        coffee_eq: "صافي ربح القهوة = المبيعات − المصاريف − الخسائر − السلعة",
        total_eq: "صافي الربح الكلي (الباتيسري + القهوة)",
        ai_title: "المساعد المالي الذكي (AI)",
        ai_btn_1: "تحليل فوارق الباتيسري والهدر",
        ai_btn_2: "مقارنة ربحية الباتيسري والقهوة",
        ai_placeholder: "اكتب سؤالك للمساعد الذكي حول أرقام الفترة الحالية...",
        ai_send: "تحليل البيانات الحالية",
        ai_thinking: "جاري التحليل...",
        ai_default_prompt: "قم بتحليل الأرباح والخسائر الحالية واقترح 3 خطوات عملية لزيادة صافي الربح وتقليل الهدر.",
        ai_prompt_1: "حلل أسباب الفارق بين الإنتاج والمبيعات في الباتيسري واقترح حلولاً لتقليل الخسائر.",
        ai_prompt_2: "قارن بين ربحية قسم الباتيسري وقسم القهوة واقترح خطة لرفع صافي الربح بنسبة 15%.",
        // Automations
        auto_workflows: "سير العمل (Workflows)",
        auto_new: "أتمتة جديدة",
        auto_templates: "قوالب جاهزة",
        auto_run_now: "تشغيل الآن",
        auto_running: "جاري التشغيل...",
        auto_delete: "حذف",
        auto_workflow_name: "اسم الأتمتة",
        auto_trigger_node: "المُشغّل (Trigger)",
        auto_action_node: "إجراء (Action)",
        auto_add_node: "إضافة خطوة جديدة",
        auto_select_hint: "اختر أتمتة من القائمة أو أنشئ واحدة جديدة من القوالب الجاهزة.",
        auto_logs_title: "سجل التنفيذ الأخير",
        auto_no_logs: "لا توجد عمليات تنفيذ بعد.",
        trig_manual: "يدوي (تشغيل عند الضغط)",
        trig_daily: "يومي (جدولة يومية)",
        trig_weekly: "أسبوعي",
        trig_interval: "كل عدد ساعات",
        run_at: "وقت التنفيذ",
        weekday: "اليوم",
        every_hours: "كل (ساعة)",
        act_reset_qty: "تصفير / تعديل كميات المنتجات",
        act_expired_loss: "تحويل المتبقي إلى خسارة + تصفير",
        act_toggle_storable: "تفعيل / إيقاف تتبع بطاقة المخزون",
        act_reconcile: "اعتماد تسوية الباتيسري تلقائياً",
        act_expense: "تسجيل مصروف دوري",
        act_prices: "تعديل الأسعار بالجملة",
        act_kpi: "حفظ ملخص الأرباح اليومي",
        act_webhook: "إرسال Webhook (n8n / Telegram)",
        scope: "نطاق المنتجات",
        scope_all: "كل المنتجات المتتبعة مخزنياً",
        scope_tracked: "منتجات بطاقة تتبع المخزون",
        scope_categ: "تصنيف نقطة بيع محدد",
        target_qty: "تعيين الكمية إلى",
        storable_action: "حالة التتبع المخزني",
        turn_on: "تفعيل (is_storable = True)",
        turn_off: "إيقاف (is_storable = False)",
        webhook_url: "رابط Webhook (POST)",
        webhook_msg: "رسالة إضافية",
        price_mode: "الطريقة",
        percent: "نسبة مئوية (%)",
        fixed_dh: "مبلغ ثابت (DH)",
        value: "القيمة",
        // Settings
        settings_title: "الإعدادات العامة",
        save_settings: "حفظ الإعدادات",
        set_pastry_cat: "تصنيفات قسم الباتيسري",
        set_coffee_cat: "تصنيفات قسم القهوة",
        set_prod_cat: "تصنيفات شاشة الإنتاج",
        set_split: "تقسيم المصاريف المشتركة (%)",
        set_pastry_pct: "الباتيسري (%)",
        set_coffee_pct: "القهوة (%)",
        set_ai: "إعدادات الذكاء الاصطناعي",
        active_provider: "المزود النشط",
        // Notifications
        notif_saved: "تم الحفظ بنجاح",
        notif_prod_saved: "تم حفظ الإنتاج وتحديث المخزون",
        notif_wf_saved: "تم حفظ الأتمتة بنجاح",
        notif_wf_ran: "تم تنفيذ الأتمتة",
        notif_reconciled: "تمت الموافقة وخصم المخزون",
        notif_stock_on: "تم تفعيل تتبع المخزون لجميع منتجات البطاقة",
        notif_stock_off: "تم إيقاف تتبع المخزون لجميع منتجات البطاقة",
    },
};

function makeStep(type, config = {}) {
    return {
        id: `step_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
        type,
        config,
    };
}

export class AllInOneDashboard extends Component {
    static template = "all_in_one.Dashboard";
    props = useProps();

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");

        const today = new Date().toISOString().split("T")[0];
        const savedLang = localStorage.getItem("aio_lang") || "en";

        this.state = proxy({
            lang: savedLang === "ar" ? "ar" : "en",
            activeTab: "analytics",
            loading: true,
            filters: {
                datePreset: "today",
                startDate: today,
                endDate: today,
                productionDate: today,
                posConfigId: "",
                posCategId: "",
            },
            data: {
                filter_info: { start_date: today, end_date: today, prod_date: today, num_days: 1 },
                pos_configs: [],
                pos_categories: [],
                all_pos_products: [],
                settings: {
                    pastry_categ_ids: [],
                    coffee_categ_ids: [],
                    production_categ_ids: [],
                    pastry_config_ids: [],
                    coffee_config_ids: [],
                    shared_pastry_pct: 50,
                    shared_coffee_pct: 50,
                    ai_provider: "gemini",
                    gemini_api_key: "",
                    gemini_model: "gemini-2.5-flash",
                    openrouter_api_key: "",
                    openrouter_model: "google/gemini-2.5-flash",
                },
                kpis: {
                    total_sales: 0,
                    total_production_value: 0,
                    total_production_qty: 0,
                    total_expenses: 0,
                    total_losses: 0,
                    total_purchases: 0,
                    total_net_profit: 0,
                    pastry: { sales: 0, production_value: 0, sales_vs_prod_diff: 0, expenses: 0, losses: 0, purchases: 0, net_profit: 0 },
                    coffee: { sales: 0, expenses: 0, losses: 0, purchases: 0, net_profit: 0 },
                },
                daily_sales_chart: [],
                production_groups: [],
                tracked_card: { products: [], candidates: [], all_active: false },
                expenses: [],
                manual_losses: [],
                auto_inv_losses: [],
                raw_materials_catalog: [],
                purchases: [],
                reconciliation_tiers: [],
                automations: [],
                automation_logs: [],
            },
            selectedCandidateId: "",
            newExpense: { name: "", date: today, expense_type: "electricity", department: "shared", periodicity: "monthly", amount: 0 },
            newLoss: { date: today, loss_type: "expired", department: "pastry", product_id: "", note: "", quantity: 1, unit_value: 0 },
            newPurchase: { date: today, raw_product_id: "", department: "pastry", entry_type: "purchased", quantity: 1, unit_cost: 0 },
            aiPrompt: TRANSLATIONS[savedLang === "ar" ? "ar" : "en"].ai_default_prompt,
            aiResponse: "",
            aiLoading: false,
            // n8n-style Automation Editor State
            editingWorkflow: null,
            runningWorkflow: false,
            lastRunOutput: "",
        });

        onWillStart(async () => {
            await this.loadData();
        });
    }

    get dir() {
        return this.state.lang === "ar" ? "rtl" : "ltr";
    }

    t(key) {
        return TRANSLATIONS[this.state.lang]?.[key] || TRANSLATIONS.en[key] || key;
    }

    setLang(lang) {
        this.state.lang = lang;
        localStorage.setItem("aio_lang", lang);
        this.state.aiPrompt = this.t("ai_default_prompt");
        if (this.state.activeTab === "analytics") {
            setTimeout(() => this.renderAnalyticsChart(), 60);
        }
    }

    updateField(targetObj, fieldName, ev, isNumber = false) {
        const raw = ev.target.value;
        targetObj[fieldName] = isNumber ? parseFloat(raw) || 0 : raw;
    }

    async loadData() {
        this.state.loading = true;
        try {
            const res = await this.orm.call("all_in_one.dashboard", "get_all_in_one_data", [
                this.state.filters,
            ]);
            this.state.data = res;
            this.state.filters.startDate = res.filter_info.start_date;
            this.state.filters.endDate = res.filter_info.end_date;

            // Keep selected workflow synced if editing
            if (this.state.editingWorkflow?.id) {
                const updated = (res.automations || []).find((w) => w.id === this.state.editingWorkflow.id);
                if (updated) {
                    this.state.editingWorkflow = JSON.parse(JSON.stringify(updated));
                }
            } else if (!this.state.editingWorkflow && res.automations?.length) {
                this.state.editingWorkflow = JSON.parse(JSON.stringify(res.automations[0]));
            }

            if (this.state.activeTab === "analytics") {
                setTimeout(() => this.renderAnalyticsChart(), 80);
            }
        } catch (e) {
            console.error("All In One load error:", e);
        } finally {
            this.state.loading = false;
        }
    }

    setTab(tab) {
        this.state.activeTab = tab;
        if (tab === "analytics") {
            setTimeout(() => this.renderAnalyticsChart(), 80);
        }
    }

    async setDatePreset(preset) {
        this.state.filters.datePreset = preset;
        await this.loadData();
    }

    async onStartDateChange(ev) {
        this.state.filters.startDate = ev.target.value;
        this.state.filters.datePreset = "custom";
        await this.loadData();
    }

    async onEndDateChange(ev) {
        this.state.filters.endDate = ev.target.value;
        this.state.filters.datePreset = "custom";
        await this.loadData();
    }

    async onPosConfigFilterChange(ev) {
        this.state.filters.posConfigId = ev.target.value;
        await this.loadData();
    }

    async onPosCategFilterChange(ev) {
        this.state.filters.posCategId = ev.target.value;
        await this.loadData();
    }

    async onProductionDateChange(ev) {
        this.state.filters.productionDate = ev.target.value;
        await this.loadData();
    }

    // Chart.js Overview
    renderAnalyticsChart() {
        const canvas = document.getElementById("aioOverviewChart");
        if (!canvas || typeof Chart === "undefined") return;
        if (this._chart) this._chart.destroy();

        const k = this.state.data.kpis;
        this._chart = new Chart(canvas.getContext("2d"), {
            type: "bar",
            data: {
                labels: [
                    this.t("kpi_sales"),
                    this.t("kpi_production"),
                    this.t("kpi_expenses"),
                    this.t("kpi_losses"),
                    this.t("kpi_purchases"),
                    this.t("kpi_net_profit"),
                ],
                datasets: [
                    {
                        label: `${this.t("pastry")} (DH)`,
                        data: [k.pastry.sales, k.pastry.production_value, k.pastry.expenses, k.pastry.losses, k.pastry.purchases, k.pastry.net_profit],
                        backgroundColor: "#4f46e5",
                        borderRadius: 6,
                    },
                    {
                        label: `${this.t("coffee")} (DH)`,
                        data: [k.coffee.sales, 0, k.coffee.expenses, k.coffee.losses, k.coffee.purchases, k.coffee.net_profit],
                        backgroundColor: "#10b981",
                        borderRadius: 6,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: "bottom" } },
                scales: { y: { grid: { color: "#f1f5f9" } }, x: { grid: { display: false } } },
            },
        });
    }

    // Settings
    toggleSettingArrayItem(listName, id) {
        const arr = this.state.data.settings[listName];
        const idx = arr.indexOf(id);
        if (idx >= 0) arr.splice(idx, 1);
        else arr.push(id);
    }

    onSharedPastryPctChange(ev) {
        const val = Math.min(100, Math.max(0, parseFloat(ev.target.value) || 0));
        this.state.data.settings.shared_pastry_pct = val;
        this.state.data.settings.shared_coffee_pct = Number((100 - val).toFixed(2));
    }

    async saveSettings() {
        await this.orm.call("all_in_one.dashboard", "save_aio_settings", [this.state.data.settings]);
        this.notification.add(this.t("notif_saved"), { type: "success" });
        await this.loadData();
    }

    // Production
    async saveProduction() {
        const items = [];
        for (const grp of this.state.data.production_groups) {
            for (const p of grp.products) {
                items.push({ product_id: p.product_id, quantity: parseFloat(p.today_qty) || 0 });
            }
        }
        await this.orm.call("all_in_one.dashboard", "save_production_batch", [
            this.state.filters.productionDate,
            items,
        ]);
        this.notification.add(this.t("notif_prod_saved"), { type: "success" });
        await this.loadData();
    }

    async addTrackedProduct() {
        if (!this.state.selectedCandidateId) return;
        await this.orm.call("all_in_one.dashboard", "add_product_to_tracked_card", [
            this.state.selectedCandidateId,
        ]);
        this.state.selectedCandidateId = "";
        await this.loadData();
    }

    async removeTrackedProduct(productId) {
        await this.orm.call("all_in_one.dashboard", "remove_product_from_tracked_card", [productId]);
        await this.loadData();
    }

    async toggleAllTrackedStorable() {
        const newState = !this.state.data.tracked_card.all_active;
        await this.orm.call("all_in_one.dashboard", "toggle_tracked_card_storable", [newState]);
        this.notification.add(newState ? this.t("notif_stock_on") : this.t("notif_stock_off"), {
            type: "info",
        });
        await this.loadData();
    }

    // Expenses, Losses, Purchases
    async addExpense() {
        await this.orm.call("all_in_one.dashboard", "create_expense_record", [this.state.newExpense]);
        this.state.newExpense.name = "";
        this.state.newExpense.amount = 0;
        await this.loadData();
    }

    async addLoss() {
        await this.orm.call("all_in_one.dashboard", "create_loss_record", [this.state.newLoss]);
        this.state.newLoss.note = "";
        this.state.newLoss.quantity = 1;
        await this.loadData();
    }

    async addPurchase() {
        if (!this.state.newPurchase.raw_product_id) return;
        await this.orm.call("all_in_one.dashboard", "create_purchase_record", [this.state.newPurchase]);
        this.state.newPurchase.quantity = 1;
        await this.loadData();
    }

    async deleteRecord(modelName, id) {
        await this.orm.call("all_in_one.dashboard", "delete_record", [modelName, id]);
        await this.loadData();
    }

    // Pastry Reconciliation
    onAllocationEdit(tierObj, prodObj, ev) {
        let val = parseFloat(ev.target.value) || 0;
        if (prodObj.qty_available <= 0) val = 0;
        else if (val > prodObj.qty_available) val = prodObj.qty_available;
        prodObj.allocated_qty = val;
        tierObj.allocated_total = Number(
            tierObj.products.reduce((acc, p) => acc + (parseFloat(p.allocated_qty) || 0), 0).toFixed(2)
        );
        tierObj.difference = Number((tierObj.sold_qty - tierObj.allocated_total).toFixed(2));
    }

    async approveReconcileTier(tierObj) {
        await this.orm.call("all_in_one.dashboard", "approve_pastry_tier_reconciliation", [
            this.state.filters.endDate,
            tierObj.price_tier,
            tierObj.sold_qty,
            tierObj.products,
        ]);
        tierObj.state = "approved";
        tierObj.editing = false;
        this.notification.add(`${this.t("notif_reconciled")} (${tierObj.price_tier} DH)`, { type: "success" });
        await this.loadData();
    }

    async rejectReconcileTier(tierObj) {
        await this.orm.call("all_in_one.dashboard", "reject_pastry_tier_reconciliation", [
            this.state.filters.endDate,
            tierObj.price_tier,
        ]);
        tierObj.state = "rejected";
        await this.loadData();
    }

    enableEditReconcileTier(tierObj) {
        tierObj.editing = true;
    }

    // =========================================================================
    // AUTOMATIONS (n8n-Style Visual Workflow Builder)
    // =========================================================================
    selectWorkflow(wf) {
        this.state.editingWorkflow = JSON.parse(JSON.stringify(wf));
        this.state.lastRunOutput = wf.last_message || "";
    }

    createNewWorkflow(templateKey = "blank") {
        let wf = {
            id: false,
            name: this.state.lang === "ar" ? "أتمتة جديدة" : "New Automation",
            active: true,
            trigger_type: "daily",
            schedule_time: "23:00",
            schedule_weekday: "6",
            interval_hours: 24,
            steps: [],
            last_status: "never",
            last_run: "",
            run_count: 0,
        };

        if (templateKey === "reset_stock") {
            wf.name = this.state.lang === "ar" ? "تصفير مخزون المنتجات نهاية اليوم" : "EOD: Reset Product Quantities to 0";
            wf.steps = [makeStep("reset_product_qty", { scope: "tracked_card", target_qty: 0, pos_categ_id: "" })];
        } else if (templateKey === "expired_eod") {
            wf.name = this.state.lang === "ar" ? "تحويل المتبقي إلى خسارة + تصفير" : "EOD: Unsold Stock → Expired Loss";
            wf.steps = [makeStep("record_expired_loss", { scope: "tracked_card", department: "pastry", pos_categ_id: "" })];
        } else if (templateKey === "reconcile_close") {
            wf.name = this.state.lang === "ar" ? "تسوية الباتيسري + ملخص الأرباح" : "EOD: Reconcile Pastry + KPI Snapshot";
            wf.steps = [
                makeStep("auto_approve_reconcile", { date_preset: "today" }),
                makeStep("kpi_snapshot", { date_preset: "today" }),
            ];
        } else if (templateKey === "morning_stock") {
            wf.name = this.state.lang === "ar" ? "تفعيل تتبع المخزون صباحاً" : "Morning: Enable Stock Tracking";
            wf.schedule_time = "06:00";
            wf.steps = [makeStep("toggle_tracked_storable", { enable: "true" })];
        } else {
            wf.steps = [makeStep("reset_product_qty", { scope: "all_storable", target_qty: 0, pos_categ_id: "" })];
        }

        this.state.editingWorkflow = wf;
        this.state.lastRunOutput = "";
    }

    addActionNode(type = "reset_product_qty") {
        if (!this.state.editingWorkflow) return;
        const defaults = {
            reset_product_qty: { scope: "all_storable", target_qty: 0, pos_categ_id: "" },
            record_expired_loss: { scope: "tracked_card", department: "pastry", pos_categ_id: "" },
            toggle_tracked_storable: { enable: "false" },
            auto_approve_reconcile: { date_preset: "today" },
            create_expense: { expense_name: "", expense_type: "other", department: "shared", periodicity: "daily", amount: 0 },
            adjust_prices: { mode: "percent", value: 0, pos_categ_id: "" },
            kpi_snapshot: { date_preset: "today" },
            webhook_http: { url: "", custom_message: "" },
        };
        this.state.editingWorkflow.steps.push(makeStep(type, defaults[type] || {}));
    }

    changeStepType(step, ev) {
        const newType = ev.target.value;
        step.type = newType;
        const defaults = {
            reset_product_qty: { scope: "all_storable", target_qty: 0, pos_categ_id: "" },
            record_expired_loss: { scope: "tracked_card", department: "pastry", pos_categ_id: "" },
            toggle_tracked_storable: { enable: "false" },
            auto_approve_reconcile: { date_preset: "today" },
            create_expense: { expense_name: "", expense_type: "other", department: "shared", periodicity: "daily", amount: 0 },
            adjust_prices: { mode: "percent", value: 0, pos_categ_id: "" },
            kpi_snapshot: { date_preset: "today" },
            webhook_http: { url: "", custom_message: "" },
        };
        step.config = defaults[newType] || {};
    }

    removeActionNode(index) {
        if (!this.state.editingWorkflow) return;
        this.state.editingWorkflow.steps.splice(index, 1);
    }

    moveActionNode(index, direction) {
        const steps = this.state.editingWorkflow?.steps;
        if (!steps) return;
        const target = index + direction;
        if (target < 0 || target >= steps.length) return;
        const [item] = steps.splice(index, 1);
        steps.splice(target, 0, item);
    }

    async saveWorkflow() {
        const wf = this.state.editingWorkflow;
        if (!wf) return;
        const wfId = await this.orm.call("all_in_one.dashboard", "save_automation_workflow", [wf]);
        wf.id = wfId;
        this.notification.add(this.t("notif_wf_saved"), { type: "success" });
        await this.loadData();
    }

    async toggleWorkflowActive(wf) {
        const nextVal = !wf.active;
        await this.orm.call("all_in_one.dashboard", "toggle_automation_active", [wf.id, nextVal]);
        wf.active = nextVal;
        if (this.state.editingWorkflow?.id === wf.id) {
            this.state.editingWorkflow.active = nextVal;
        }
    }

    async runWorkflowNow(wf = null) {
        const target = wf || this.state.editingWorkflow;
        if (!target) return;
        this.state.runningWorkflow = true;
        try {
            // Save first if editing current workflow
            if (!wf || target.id === this.state.editingWorkflow?.id) {
                const wfId = await this.orm.call("all_in_one.dashboard", "save_automation_workflow", [target]);
                target.id = wfId;
            }
            const res = await this.orm.call("all_in_one.dashboard", "run_automation_now", [target.id]);
            this.state.lastRunOutput = res.summary || "";
            this.notification.add(this.t("notif_wf_ran"), {
                type: res.status === "error" ? "danger" : "success",
            });
            await this.loadData();
        } finally {
            this.state.runningWorkflow = false;
        }
    }

    async deleteWorkflow(wfId) {
        await this.orm.call("all_in_one.dashboard", "delete_automation_workflow", [wfId]);
        if (this.state.editingWorkflow?.id === wfId) {
            this.state.editingWorkflow = null;
            this.state.lastRunOutput = "";
        }
        await this.loadData();
    }

    getStepIcon(type) {
        const icons = {
            reset_product_qty: "restart_alt",
            record_expired_loss: "delete_sweep",
            toggle_tracked_storable: "inventory_2",
            auto_approve_reconcile: "fact_check",
            create_expense: "payments",
            adjust_prices: "sell",
            kpi_snapshot: "insights",
            webhook_http: "webhook",
        };
        return icons[type] || "bolt";
    }

    // AI Assistant
    async askAi(customPrompt = null) {
        if (customPrompt) {
            this.state.aiPrompt = customPrompt;
        }
        if (!this.state.aiPrompt.trim()) return;
        this.state.aiLoading = true;
        try {
            const answer = await this.orm.call("all_in_one.dashboard", "ask_ai_assistant", [
                this.state.aiPrompt,
                {
                    period: this.state.data.filter_info,
                    kpis: this.state.data.kpis,
                    reconciliation_tiers: this.state.data.reconciliation_tiers,
                },
                this.state.lang,
            ]);
            this.state.aiResponse = answer;
        } finally {
            this.state.aiLoading = false;
        }
    }

    formatDH(val) {
        return Number(val || 0).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + " DH";
    }
}

registry.category("actions").add("all_in_one.dashboard", AllInOneDashboard);
