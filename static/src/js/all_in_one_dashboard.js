/** @odoo-module */

import { registry } from "@web/core/registry";
import { Component, proxy, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class AllInOneDashboard extends Component {
    static template = "all_in_one.Dashboard";

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");

        const today = new Date().toISOString().split("T")[0];

        // OWL 3 in Odoo 20 uses proxy() instead of useState()
        this.state = proxy({
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
            },
            // Forms state
            selectedCandidateId: "",
            newExpense: { name: "", date: today, expense_type: "electricity", department: "shared", periodicity: "monthly", amount: 0 },
            newLoss: { date: today, loss_type: "expired", department: "pastry", product_id: "", note: "", quantity: 1, unit_value: 0 },
            newPurchase: { date: today, raw_product_id: "", department: "pastry", entry_type: "purchased", quantity: 1, unit_cost: 0 },
            aiPrompt: "قم بتحليل الأرباح والخسائر الحالية واقترح 3 خطوات عملية لزيادة صافي الربح وتقليل الهدر.",
            aiResponse: "",
            aiLoading: false,
        });

        onWillStart(async () => {
            await this.loadData();
        });
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

    async onCustomDateChange() {
        this.state.filters.datePreset = "custom";
        await this.loadData();
    }

    async onFilterChange() {
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
                labels: ["المبيعات", "الإنتاج", "المصاريف", "الخسائر", "السلعة", "صافي الربح"],
                datasets: [
                    {
                        label: "الباتيسري (DH)",
                        data: [k.pastry.sales, k.pastry.production_value, k.pastry.expenses, k.pastry.losses, k.pastry.purchases, k.pastry.net_profit],
                        backgroundColor: "#0d6efd",
                    },
                    {
                        label: "القهوة (DH)",
                        data: [k.coffee.sales, 0, k.coffee.expenses, k.coffee.losses, k.coffee.purchases, k.coffee.net_profit],
                        backgroundColor: "#198754",
                    },
                ],
            },
            options: { responsive: true, maintainAspectRatio: false },
        });
    }

    // Settings Multi-select toggle helper
    toggleSettingArrayItem(listName, id) {
        const arr = this.state.data.settings[listName];
        const idx = arr.indexOf(id);
        if (idx >= 0) {
            arr.splice(idx, 1);
        } else {
            arr.push(id);
        }
    }

    onSharedPastryPctChange(ev) {
        const val = Math.min(100, Math.max(0, parseFloat(ev.target.value) || 0));
        this.state.data.settings.shared_pastry_pct = val;
        this.state.data.settings.shared_coffee_pct = Number((100 - val).toFixed(2));
    }

    async saveSettings() {
        await this.orm.call("all_in_one.dashboard", "save_aio_settings", [this.state.data.settings]);
        this.notification.add("تم حفظ الإعدادات بنجاح", { type: "success" });
        await this.loadData();
    }

    // Tab 2: Production & Permanent Storable Card
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
        this.notification.add("تم حفظ الإنتاج وتحديث المخزون بنجاح", { type: "success" });
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
        this.notification.add(
            newState
                ? "تم تفعيل تتبع المخزون (is_storable = True) لجميع منتجات البطاقة"
                : "تم إيقاف تتبع المخزون (is_storable = False) لجميع منتجات البطاقة مع الاحتفاظ بها",
            { type: "info" }
        );
        await this.loadData();
    }

    // Tab 3: Expenses
    async addExpense() {
        await this.orm.call("all_in_one.dashboard", "create_expense_record", [this.state.newExpense]);
        this.state.newExpense.name = "";
        this.state.newExpense.amount = 0;
        await this.loadData();
    }

    // Tab 4: Losses
    async addLoss() {
        await this.orm.call("all_in_one.dashboard", "create_loss_record", [this.state.newLoss]);
        this.state.newLoss.note = "";
        this.state.newLoss.quantity = 1;
        await this.loadData();
    }

    // Tab 5: Purchases
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

    // Tab 6: Pastry Smart Reconciliation
    onAllocationEdit(tierObj, prodObj, ev) {
        let val = parseFloat(ev.target.value) || 0;
        if (prodObj.qty_available <= 0) {
            val = 0;
        } else if (val > prodObj.qty_available) {
            val = prodObj.qty_available;
        }
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
        this.notification.add(`تمت الموافقة وخصم المخزون لفئة ${tierObj.price_tier} DH`, { type: "success" });
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

    // Tab 8: AI Assistant
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