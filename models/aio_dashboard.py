from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo
import json
import logging
import urllib.request
import urllib.error

from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AllInOneDashboard(models.TransientModel):
    _name = 'all_in_one.dashboard'
    _description = 'All In One Unified Controller & AI Engine'

    def _resolve_dates(self, date_preset, start_date_str, end_date_str):
        today = fields.Date.context_today(self)
        if date_preset == 'today':
            return today, today
        elif date_preset == 'yesterday':
            yest = today - timedelta(days=1)
            return yest, yest
        elif date_preset == 'this_week':
            start = today - timedelta(days=today.weekday())
            return start, today
        elif date_preset == 'last_week':
            end = today - timedelta(days=today.weekday() + 1)
            start = end - timedelta(days=6)
            return start, end
        else:
            s_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else today
            e_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else today
            if e_date < s_date:
                e_date = s_date
            return s_date, e_date

    def _get_utc_bounds(self, start_date, end_date):
        user_tz = self.env.tz or ZoneInfo(self.env.user.tz or 'UTC')
        if isinstance(user_tz, str):
            user_tz = ZoneInfo(user_tz)
        utc_tz = ZoneInfo('UTC')
        dt_start = datetime.combine(start_date, time.min, tzinfo=user_tz).astimezone(utc_tz).replace(tzinfo=None)
        dt_end = datetime.combine(end_date, time.max, tzinfo=user_tz).astimezone(utc_tz).replace(tzinfo=None)
        return dt_start, dt_end

    def _get_primary_pos_categ(self, product):
        tmpl = product.product_tmpl_id
        if 'pos_categ_ids' in tmpl._fields and tmpl.pos_categ_ids:
            return tmpl.pos_categ_ids[0]
        if 'pos_categ_id' in tmpl._fields and tmpl.pos_categ_id:
            return tmpl.pos_categ_id
        return self.env['pos.category']

    def _create_stock_adjustment_move(self, product, qty_delta, reason_name):
        """Creates and validates a stock move to add (production) or deduct (reconciliation) inventory."""
        if not qty_delta or not product.is_storable:
            return self.env['stock.move']

        warehouse = self.env['stock.warehouse'].sudo().search([('company_id', '=', self.env.company.id)], limit=1)
        internal_loc = warehouse.lot_stock_id
        inventory_loc = product.property_stock_inventory or self.env['stock.location'].sudo().search(
            [('usage', '=', 'inventory')], limit=1
        )
        if not internal_loc or not inventory_loc:
            return self.env['stock.move']

        if qty_delta > 0:
            src_loc, dest_loc = inventory_loc, internal_loc
        else:
            src_loc, dest_loc = internal_loc, inventory_loc

        abs_qty = abs(qty_delta)
        move_vals = {
            'location_id': src_loc.id,
            'location_dest_id': dest_loc.id,
            'product_id': product.id,
            'product_uom': product.uom_id.id,
            'product_uom_qty': abs_qty,
            'quantity': abs_qty,
            'picked': True,
            'state': 'draft',
        }
        if 'name' in self.env['stock.move']._fields:
            move_vals['name'] = reason_name

        move = self.env['stock.move'].sudo().create(move_vals)
        move._action_confirm()
        move.quantity = abs_qty
        move.picked = True
        move._action_done()
        return move

    @api.model
    def get_all_in_one_data(self, filters):
        settings = self.env['all_in_one.settings'].get_singleton()
        date_preset = filters.get('datePreset', 'today')
        start_date, end_date = self._resolve_dates(
            date_preset, filters.get('startDate'), filters.get('endDate')
        )
        prod_date_str = filters.get('productionDate') or end_date.strftime('%Y-%m-%d')
        prod_date = datetime.strptime(prod_date_str, '%Y-%m-%d').date()

        pos_config_id = int(filters['posConfigId']) if filters.get('posConfigId') else False
        pos_categ_id = int(filters['posCategId']) if filters.get('posCategId') else False

        num_days = max(1, (end_date - start_date).days + 1)
        dt_start_utc, dt_end_utc = self._get_utc_bounds(start_date, end_date)

        # All POS Configs & Categories for Dropdowns & Settings
        all_pos_configs = self.env['pos.config'].sudo().search_read([], ['id', 'name'])
        all_pos_categs = self.env['pos.category'].sudo().search_read([], ['id', 'name'])

        pastry_categ_ids = set(settings.pastry_categ_ids.ids)
        coffee_categ_ids = set(settings.coffee_categ_ids.ids)
        prod_categ_ids = set(settings.production_categ_ids.ids)
        pastry_pos_ids = set(settings.pastry_config_ids.ids)
        coffee_pos_ids = set(settings.coffee_config_ids.ids)

        # -------------------------------------------------------------------------
        # 1. POS ORDERS & SALES (Filtered by Date, POS Register, and POS Category)
        # -------------------------------------------------------------------------
        order_domain = [
            ('date_order', '>=', dt_start_utc),
            ('date_order', '<=', dt_end_utc),
            ('state', 'in', ['paid', 'done', 'invoiced']),
        ]
        if pos_config_id:
            order_domain.append(('config_id', '=', pos_config_id))

        orders = self.env['pos.order'].sudo().search(order_domain)

        total_pos_sales = 0.0
        pastry_pos_sales = 0.0
        coffee_pos_sales = 0.0
        generic_btn_sales_by_price = {}
        sales_by_product = {}
        daily_sales_map = {}

        for order in orders:
            ord_cfg_id = order.config_id.id
            ord_day = order.date_order.strftime('%Y-%m-%d')
            for line in order.lines:
                product = line.product_id
                prod_categs = set(product.product_tmpl_id.pos_categ_ids.ids)
                if pos_categ_id and pos_categ_id not in prod_categs:
                    continue

                amt = line.price_subtotal_incl
                qty = line.qty
                total_pos_sales += amt
                daily_sales_map[ord_day] = daily_sales_map.get(ord_day, 0.0) + amt

                sales_by_product[product.id] = sales_by_product.get(product.id, 0.0) + qty

                is_pastry = bool(prod_categs & pastry_categ_ids) or (ord_cfg_id in pastry_pos_ids and not (prod_categs & coffee_categ_ids))
                is_coffee = bool(prod_categs & coffee_categ_ids) or (ord_cfg_id in coffee_pos_ids and not (prod_categs & pastry_categ_ids))

                if is_pastry:
                    pastry_pos_sales += amt
                    price_tier = round(product.lst_price or line.price_unit, 2)
                    if product.aio_is_generic_price_btn:
                        generic_btn_sales_by_price[price_tier] = generic_btn_sales_by_price.get(price_tier, 0.0) + qty
                elif is_coffee:
                    coffee_pos_sales += amt

        # -------------------------------------------------------------------------
        # 2. PRODUCTION TAB DATA & PERMANENT STORABLE CARD
        # -------------------------------------------------------------------------
        # Production entries for the selected date range (for Analytics & Pastry)
        prod_range_domain = [('date', '>=', start_date), ('date', '<=', end_date)]
        if pos_categ_id:
            prod_range_domain.append(('pos_categ_id', '=', pos_categ_id))
        prod_entries_range = self.env['all_in_one.production.entry'].sudo().search(prod_range_domain)
        total_production_value = sum(prod_entries_range.mapped('total_sale_value'))
        total_production_qty = sum(prod_entries_range.mapped('quantity'))

        prod_qty_by_product = {}
        for pe in prod_entries_range:
            prod_qty_by_product[pe.product_id.id] = prod_qty_by_product.get(pe.product_id.id, 0.0) + pe.quantity

        # Production entry screen for `prod_date` grouped by `production_categ_ids`
        day_entries = {
            e.product_id.id: e.quantity
            for e in self.env['all_in_one.production.entry'].sudo().search([('date', '=', prod_date)])
        }
        target_prod_categs = settings.production_categ_ids or self.env['pos.category'].sudo().search([])
        if pos_categ_id:
            target_prod_categs = target_prod_categs.filtered(lambda c: c.id == pos_categ_id)

        production_groups = []
        for categ in target_prod_categs:
            c_prods = self.env['product.product'].sudo().search([
                ('available_in_pos', '=', True),
                ('product_tmpl_id.pos_categ_ids', 'in', [categ.id]),
                ('aio_is_generic_price_btn', '=', False),
            ])
            prod_rows = [{
                'product_id': p.id,
                'name': p.display_name,
                'list_price': p.lst_price,
                'qty_available': p.qty_available,
                'today_qty': day_entries.get(p.id, 0.0),
                'is_storable': p.is_storable,
            } for p in c_prods]
            if prod_rows:
                production_groups.append({
                    'categ_id': categ.id,
                    'categ_name': categ.name,
                    'products': prod_rows,
                })

        # Permanent Storable Products Card
        tracked_card_products = self.env['product.product'].sudo().search([('aio_tracked_card', '=', True)])
        storable_candidates = self.env['product.product'].sudo().search([
            ('is_storable', '=', True),
            ('aio_tracked_card', '=', False),
        ], limit=200)

        tracked_card_list = [{
            'id': p.id,
            'name': p.display_name,
            'is_storable': p.is_storable,
            'qty_available': p.qty_available,
        } for p in tracked_card_products]

        all_tracked_active = bool(tracked_card_products) and all(p.is_storable for p in tracked_card_products)

        # -------------------------------------------------------------------------
        # 3. EXPENSES TAB (Pro-rated by Periodicity × Filter Days & Shared Split)
        # -------------------------------------------------------------------------
        expenses = self.env['all_in_one.expense'].sudo().search([('active', '=', True)])
        expenses_list = []
        pastry_expenses_total = 0.0
        coffee_expenses_total = 0.0
        shared_pastry_ratio = (settings.shared_pastry_pct or 50.0) / 100.0
        shared_coffee_ratio = (settings.shared_coffee_pct or 50.0) / 100.0

        for exp in expenses:
            # If daily expense, only count if within range or recurring; monthly/annual pro-rate by num_days
            period_amount = exp.daily_rate * num_days
            if exp.department == 'pastry':
                p_share, c_share = period_amount, 0.0
            elif exp.department == 'coffee':
                p_share, c_share = 0.0, period_amount
            else:
                p_share = period_amount * shared_pastry_ratio
                c_share = period_amount * shared_coffee_ratio

            pastry_expenses_total += p_share
            coffee_expenses_total += c_share

            expenses_list.append({
                'id': exp.id,
                'name': exp.name,
                'date': exp.date.strftime('%Y-%m-%d'),
                'expense_type': exp.expense_type,
                'department': exp.department,
                'periodicity': exp.periodicity,
                'amount': exp.amount,
                'daily_rate': round(exp.daily_rate, 2),
                'period_cost': round(period_amount, 2),
                'pastry_share': round(p_share, 2),
                'coffee_share': round(c_share, 2),
            })

        total_expenses = pastry_expenses_total + coffee_expenses_total

        # -------------------------------------------------------------------------
        # 4. LOSSES & WASTE TAB (Manual + Automatic Negative Inventory Adjustments)
        # -------------------------------------------------------------------------
        loss_domain = [('date', '>=', start_date), ('date', '<=', end_date)]
        if pos_categ_id:
            loss_domain.append(('pos_categ_id', '=', pos_categ_id))
        manual_losses = self.env['all_in_one.loss'].sudo().search(loss_domain)

        manual_losses_list = []
        pastry_losses_total = 0.0
        coffee_losses_total = 0.0

        for l in manual_losses:
            if l.department == 'coffee':
                coffee_losses_total += l.total_value
            else:
                pastry_losses_total += l.total_value
            manual_losses_list.append({
                'id': l.id,
                'date': l.date.strftime('%Y-%m-%d'),
                'loss_type': l.loss_type,
                'department': l.department,
                'product_name': l.product_id.display_name or l.note or '-',
                'quantity': l.quantity,
                'unit_value': l.unit_value,
                'total_value': round(l.total_value, 2),
            })

        # Automatic Inventory Adjustment Losses (Actual < Theoretical => Internal -> Inventory location)
        inv_loss_moves = self.env['stock.move'].sudo().search([
            ('state', '=', 'done'),
            ('location_id.usage', '=', 'internal'),
            ('location_dest_id.usage', '=', 'inventory'),
            ('date', '>=', dt_start_utc),
            ('date', '<=', dt_end_utc),
        ])
        auto_inv_losses = []
        for mv in inv_loss_moves:
            prod = mv.product_id
            p_categs = set(prod.product_tmpl_id.pos_categ_ids.ids)
            if pos_categ_id and pos_categ_id not in p_categs:
                continue
            val = mv.quantity * (prod.lst_price or prod.standard_price or 0.0)
            dept = 'coffee' if (p_categs & coffee_categ_ids) else 'pastry'
            if dept == 'coffee':
                coffee_losses_total += val
            else:
                pastry_losses_total += val
            auto_inv_losses.append({
                'id': mv.id,
                'date': mv.date.strftime('%Y-%m-%d %H:%M'),
                'product_name': prod.display_name,
                'quantity': mv.quantity,
                'unit_price': prod.lst_price or prod.standard_price or 0.0,
                'total_value': round(val, 2),
                'department': dept,
            })

        total_losses = pastry_losses_total + coffee_losses_total

        # -------------------------------------------------------------------------
        # 5. RAW MATERIALS & PURCHASES TAB
        # -------------------------------------------------------------------------
        raw_products = self.env['product.product'].sudo().search([('purchase_ok', '=', True)])
        raw_materials_catalog = []
        for rp in raw_products:
            final_prod = rp.aio_final_product_id
            cat = self._get_primary_pos_categ(final_prod or rp)
            if pos_categ_id and cat.id != pos_categ_id:
                continue
            dept = 'coffee' if (cat.id in coffee_categ_ids) else 'pastry'
            raw_materials_catalog.append({
                'id': rp.id,
                'name': rp.display_name,
                'standard_price': rp.standard_price,
                'final_product_id': final_prod.id if final_prod else False,
                'final_product_name': final_prod.display_name if final_prod else 'عام / غير مرتبط',
                'categ_id': cat.id if cat else False,
                'categ_name': cat.name if cat else 'بدون تصنيف',
                'department': dept,
            })

        purch_domain = [('date', '>=', start_date), ('date', '<=', end_date)]
        if pos_categ_id:
            purch_domain.append(('pos_categ_id', '=', pos_categ_id))
        purchases = self.env['all_in_one.purchase.entry'].sudo().search(purch_domain)

        purchases_list = []
        pastry_purchases_total = 0.0
        coffee_purchases_total = 0.0
        for pe in purchases:
            if pe.department == 'coffee':
                coffee_purchases_total += pe.total_cost
            else:
                pastry_purchases_total += pe.total_cost
            purchases_list.append({
                'id': pe.id,
                'date': pe.date.strftime('%Y-%m-%d'),
                'raw_product_name': pe.raw_product_id.display_name,
                'final_product_name': pe.final_product_id.display_name or '-',
                'categ_name': pe.pos_categ_id.name or '-',
                'department': pe.department,
                'entry_type': pe.entry_type,
                'quantity': pe.quantity,
                'unit_cost': pe.unit_cost,
                'total_cost': round(pe.total_cost, 2),
            })

        total_purchases = pastry_purchases_total + coffee_purchases_total

        # -------------------------------------------------------------------------
        # 6. PASTRY TAB: PRICE-TIER GROUPING & SMART STOCK RECONCILIATION TABLE
        # -------------------------------------------------------------------------
        pastry_domain = [('available_in_pos', '=', True)]
        if pastry_categ_ids:
            pastry_domain.append(('product_tmpl_id.pos_categ_ids', 'in', list(pastry_categ_ids)))
        if pos_categ_id:
            pastry_domain.append(('product_tmpl_id.pos_categ_ids', 'in', [pos_categ_id]))

        pastry_products = self.env['product.product'].sudo().search(pastry_domain)
        price_tiers_map = {}
        pastry_production_total_value = 0.0

        for pp in pastry_products:
            tier = round(pp.lst_price or 0.0, 2)
            if tier <= 0:
                continue
            if tier not in price_tiers_map:
                price_tiers_map[tier] = {
                    'price_tier': tier,
                    'generic_sold_qty': generic_btn_sales_by_price.get(tier, 0.0),
                    'direct_sold_qty': 0.0,
                    'produced_qty': 0.0,
                    'produced_value': 0.0,
                    'products': [],
                }
            if pp.aio_is_generic_price_btn:
                continue

            p_prod_qty = prod_qty_by_product.get(pp.id, 0.0)
            p_sold_qty = sales_by_product.get(pp.id, 0.0)
            p_prod_val = p_prod_qty * tier
            pastry_production_total_value += p_prod_val

            price_tiers_map[tier]['direct_sold_qty'] += p_sold_qty
            price_tiers_map[tier]['produced_qty'] += p_prod_qty
            price_tiers_map[tier]['produced_value'] += p_prod_val
            price_tiers_map[tier]['products'].append({
                'product_id': pp.id,
                'name': pp.display_name,
                'priority': pp.aio_deduction_priority or 10,
                'qty_available': pp.qty_available,
                'produced_qty': p_prod_qty,
                'direct_sold_qty': p_sold_qty,
            })

        # Build Smart End-of-Day Reconciliation Rows per Price Tier (for `end_date`)
        reconciliation_tiers = []
        for tier in sorted(price_tiers_map.keys()):
            t_data = price_tiers_map[tier]
            sold_to_allocate = t_data['generic_sold_qty'] or t_data['direct_sold_qty']

            existing_rec = self.env['all_in_one.pastry.reconcile'].sudo().search([
                ('date', '=', end_date),
                ('price_tier', '=', tier),
            ], limit=1)

            saved_alloc_map = {}
            rec_state = 'draft'
            if existing_rec:
                rec_state = existing_rec.state
                saved_alloc_map = {ln.product_id.id: ln.allocated_qty for ln in existing_rec.line_ids}

            # Sort products by Rule 2: Priority ASC, then Stock Available DESC
            sorted_prods = sorted(
                t_data['products'],
                key=lambda x: (x['priority'], -x['qty_available']),
            )

            remaining = sold_to_allocate
            alloc_products = []
            total_allocated = 0.0

            for prod_info in sorted_prods:
                pid = prod_info['product_id']
                avail = prod_info['qty_available']
                if existing_rec and rec_state == 'approved':
                    alloc = saved_alloc_map.get(pid, 0.0)
                else:
                    # Rule 1: Strictly forbid deduction if qty_available <= 0
                    if avail <= 0 or remaining <= 0:
                        alloc = 0.0
                    else:
                        alloc = min(remaining, avail)
                        remaining -= alloc

                alloc = round(alloc, 2)
                total_allocated += alloc
                alloc_products.append({
                    **prod_info,
                    'allocated_qty': alloc,
                    'can_deduct': avail > 0,
                })

            reconciliation_tiers.append({
                'price_tier': tier,
                'sold_qty': round(sold_to_allocate, 2),
                'produced_qty': round(t_data['produced_qty'], 2),
                'produced_value': round(t_data['produced_value'], 2),
                'allocated_total': round(total_allocated, 2),
                'difference': round(sold_to_allocate - total_allocated, 2),
                'state': rec_state,
                'editing': False,
                'products': alloc_products,
            })

        # -------------------------------------------------------------------------
        # 7. NET PROFIT CALCULATIONS (Pastry, Coffee, Total)
        # -------------------------------------------------------------------------
        pastry_net_profit = (
            pastry_pos_sales - pastry_expenses_total - pastry_losses_total - pastry_purchases_total
        )
        coffee_net_profit = (
            coffee_pos_sales - coffee_expenses_total - coffee_losses_total - coffee_purchases_total
        )
        total_net_profit = pastry_net_profit + coffee_net_profit

        all_pos_products = self.env['product.product'].sudo().search_read(
            [('available_in_pos', '=', True)], ['id', 'display_name', 'lst_price']
        )

        return {
            'filter_info': {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'prod_date': prod_date.strftime('%Y-%m-%d'),
                'num_days': num_days,
            },
            'pos_configs': all_pos_configs,
            'pos_categories': all_pos_categs,
            'all_pos_products': all_pos_products,
            'settings': {
                'pastry_categ_ids': settings.pastry_categ_ids.ids,
                'coffee_categ_ids': settings.coffee_categ_ids.ids,
                'production_categ_ids': settings.production_categ_ids.ids,
                'pastry_config_ids': settings.pastry_config_ids.ids,
                'coffee_config_ids': settings.coffee_config_ids.ids,
                'shared_pastry_pct': settings.shared_pastry_pct,
                'shared_coffee_pct': settings.shared_coffee_pct,
                'ai_provider': settings.ai_provider,
                'gemini_api_key': settings.gemini_api_key or '',
                'gemini_model': settings.gemini_model or 'gemini-2.5-flash',
                'openrouter_api_key': settings.openrouter_api_key or '',
                'openrouter_model': settings.openrouter_model or 'google/gemini-2.5-flash',
            },
            'kpis': {
                'total_sales': round(total_pos_sales, 2),
                'total_production_value': round(total_production_value, 2),
                'total_production_qty': round(total_production_qty, 2),
                'total_expenses': round(total_expenses, 2),
                'total_losses': round(total_losses, 2),
                'total_purchases': round(total_purchases, 2),
                'total_net_profit': round(total_net_profit, 2),
                'pastry': {
                    'sales': round(pastry_pos_sales, 2),
                    'production_value': round(pastry_production_total_value, 2),
                    'sales_vs_prod_diff': round(pastry_pos_sales - pastry_production_total_value, 2),
                    'expenses': round(pastry_expenses_total, 2),
                    'losses': round(pastry_losses_total, 2),
                    'purchases': round(pastry_purchases_total, 2),
                    'net_profit': round(pastry_net_profit, 2),
                },
                'coffee': {
                    'sales': round(coffee_pos_sales, 2),
                    'expenses': round(coffee_expenses_total, 2),
                    'losses': round(coffee_losses_total, 2),
                    'purchases': round(coffee_purchases_total, 2),
                    'net_profit': round(coffee_net_profit, 2),
                },
            },
            'daily_sales_chart': [
                {'date': k, 'sales': round(v, 2)} for k, v in sorted(daily_sales_map.items())
            ],
            'production_groups': production_groups,
            'tracked_card': {
                'products': tracked_card_list,
                'candidates': [{'id': c.id, 'name': c.display_name} for c in storable_candidates],
                'all_active': all_tracked_active,
            },
            'expenses': expenses_list,
            'manual_losses': manual_losses_list,
            'auto_inv_losses': auto_inv_losses,
            'raw_materials_catalog': raw_materials_catalog,
            'purchases': purchases_list,
            'reconciliation_tiers': reconciliation_tiers,
        }

    # =========================================================================
    # ACTION METHODS FOR TABS
    # =========================================================================
    @api.model
    def save_aio_settings(self, vals):
        settings = self.env['all_in_one.settings'].get_singleton()
        settings.sudo().write({
            'pastry_categ_ids': [fields.Command.set(vals.get('pastry_categ_ids', []))],
            'coffee_categ_ids': [fields.Command.set(vals.get('coffee_categ_ids', []))],
            'production_categ_ids': [fields.Command.set(vals.get('production_categ_ids', []))],
            'pastry_config_ids': [fields.Command.set(vals.get('pastry_config_ids', []))],
            'coffee_config_ids': [fields.Command.set(vals.get('coffee_config_ids', []))],
            'shared_pastry_pct': float(vals.get('shared_pastry_pct', 50.0)),
            'shared_coffee_pct': float(vals.get('shared_coffee_pct', 50.0)),
            'ai_provider': vals.get('ai_provider', 'gemini'),
            'gemini_api_key': vals.get('gemini_api_key', ''),
            'gemini_model': vals.get('gemini_model', 'gemini-2.5-flash'),
            'openrouter_api_key': vals.get('openrouter_api_key', ''),
            'openrouter_model': vals.get('openrouter_model', 'google/gemini-2.5-flash'),
        })
        return True

    @api.model
    def save_production_batch(self, prod_date_str, items):
        prod_date = datetime.strptime(prod_date_str, '%Y-%m-%d').date()
        Entry = self.env['all_in_one.production.entry'].sudo()

        for item in items:
            product_id = int(item['product_id'])
            new_qty = float(item.get('quantity', 0.0))
            product = self.env['product.product'].sudo().browse(product_id)
            cat = self._get_primary_pos_categ(product)

            existing = Entry.search([('date', '=', prod_date), ('product_id', '=', product_id)], limit=1)
            old_qty = existing.quantity if existing else 0.0
            delta = new_qty - old_qty

            if existing:
                if new_qty <= 0:
                    existing.unlink()
                else:
                    existing.write({'quantity': new_qty, 'unit_price': product.lst_price})
            elif new_qty > 0:
                Entry.create({
                    'date': prod_date,
                    'product_id': product_id,
                    'pos_categ_id': cat.id if cat else False,
                    'quantity': new_qty,
                    'unit_price': product.lst_price,
                })

            if delta != 0 and product.is_storable:
                self._create_stock_adjustment_move(product, delta, f"AIO Production {prod_date_str}")
        return True

    @api.model
    def add_product_to_tracked_card(self, product_id):
        prod = self.env['product.product'].sudo().browse(int(product_id))
        if prod.exists():
            prod.product_tmpl_id.aio_tracked_card = True
        return True

    @api.model
    def remove_product_from_tracked_card(self, product_id):
        prod = self.env['product.product'].sudo().browse(int(product_id))
        if prod.exists():
            prod.product_tmpl_id.aio_tracked_card = False
        return True

    @api.model
    def toggle_tracked_card_storable(self, enable_storable):
        """
        One-click toggle for all products in the Permanent Storable Card:
        Turns `is_storable` ON or OFF without changing product type and without removing them from the card.
        """
        prods = self.env['product.product'].sudo().search([('aio_tracked_card', '=', True)])
        prods.mapped('product_tmpl_id').sudo().write({'is_storable': bool(enable_storable)})
        return True

    @api.model
    def create_expense_record(self, vals):
        self.env['all_in_one.expense'].sudo().create({
            'name': vals.get('name') or 'مصروف',
            'date': vals.get('date') or fields.Date.context_today(self),
            'expense_type': vals.get('expense_type', 'other'),
            'department': vals.get('department', 'shared'),
            'periodicity': vals.get('periodicity', 'daily'),
            'amount': float(vals.get('amount', 0.0)),
        })
        return True

    @api.model
    def delete_record(self, model_name, record_id):
        allowed = {'all_in_one.expense', 'all_in_one.loss', 'all_in_one.purchase.entry'}
        if model_name in allowed:
            self.env[model_name].sudo().browse(int(record_id)).unlink()
        return True

    @api.model
    def create_loss_record(self, vals):
        product_id = int(vals['product_id']) if vals.get('product_id') else False
        product = self.env['product.product'].sudo().browse(product_id) if product_id else self.env['product.product']
        cat = self._get_primary_pos_categ(product) if product else self.env['pos.category']
        unit_val = float(vals.get('unit_value') or (product.lst_price if product else 0.0))

        self.env['all_in_one.loss'].sudo().create({
            'date': vals.get('date') or fields.Date.context_today(self),
            'loss_type': vals.get('loss_type', 'expired'),
            'department': vals.get('department', 'pastry'),
            'product_id': product.id if product else False,
            'pos_categ_id': cat.id if cat else False,
            'note': vals.get('note', ''),
            'quantity': float(vals.get('quantity', 1.0)),
            'unit_value': unit_val,
        })
        return True

    @api.model
    def create_purchase_record(self, vals):
        raw_id = int(vals['raw_product_id'])
        raw_prod = self.env['product.product'].sudo().browse(raw_id)
        final_prod = raw_prod.aio_final_product_id
        cat = self._get_primary_pos_categ(final_prod or raw_prod)
        unit_cost = float(vals.get('unit_cost') or raw_prod.standard_price or 0.0)

        self.env['all_in_one.purchase.entry'].sudo().create({
            'date': vals.get('date') or fields.Date.context_today(self),
            'raw_product_id': raw_prod.id,
            'final_product_id': final_prod.id if final_prod else False,
            'pos_categ_id': cat.id if cat else False,
            'department': vals.get('department', 'pastry'),
            'entry_type': vals.get('entry_type', 'purchased'),
            'quantity': float(vals.get('quantity', 1.0)),
            'unit_cost': unit_cost,
        })
        return True

    @api.model
    def approve_pastry_tier_reconciliation(self, date_str, price_tier, sold_qty, allocations):
        """
        Validates & executes the end-of-day stock deduction for a Pastry Price Tier.
        Enforces Rule 1 (never deduct from qty_available <= 0).
        """
        rec_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        Reconcile = self.env['all_in_one.pastry.reconcile'].sudo()
        rec = Reconcile.search([('date', '=', rec_date), ('price_tier', '=', float(price_tier))], limit=1)

        if rec:
            # Reverse previous stock moves if re-approving after Edit
            for old_line in rec.line_ids:
                if old_line.allocated_qty > 0 and old_line.product_id.is_storable:
                    self._create_stock_adjustment_move(
                        old_line.product_id,
                        old_line.allocated_qty,
                        f"Reversal Pastry Reconcile {date_str}",
                    )
            rec.line_ids.unlink()
            rec.write({'sold_qty': float(sold_qty), 'state': 'approved'})
        else:
            rec = Reconcile.create({
                'date': rec_date,
                'price_tier': float(price_tier),
                'sold_qty': float(sold_qty),
                'state': 'approved',
            })

        for item in allocations:
            pid = int(item['product_id'])
            qty = float(item.get('allocated_qty', 0.0))
            if qty <= 0:
                continue
            product = self.env['product.product'].sudo().browse(pid)
            if product.qty_available <= 0:
                raise UserError(_("يُمنع الخصم من المنتج '%s' لأن مخزونه الحالي يساوي صفر أو أقل!", product.display_name))
            if qty > product.qty_available:
                raise UserError(
                    _("الكمية المخصومة (%(q)s) للمنتج '%(p)s' تتجاوز المخزون المتوفر (%(a)s)!",
                      q=qty, p=product.display_name, a=product.qty_available)
                )

            move = self._create_stock_adjustment_move(product, -qty, f"Pastry EOD Deduction {date_str}")
            self.env['all_in_one.pastry.reconcile.line'].sudo().create({
                'reconcile_id': rec.id,
                'product_id': product.id,
                'allocated_qty': qty,
                'stock_move_id': move.id if move else False,
            })
        return True

    @api.model
    def reject_pastry_tier_reconciliation(self, date_str, price_tier):
        rec_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        Reconcile = self.env['all_in_one.pastry.reconcile'].sudo()
        rec = Reconcile.search([('date', '=', rec_date), ('price_tier', '=', float(price_tier))], limit=1)
        if rec:
            rec.write({'state': 'rejected'})
        else:
            Reconcile.create({'date': rec_date, 'price_tier': float(price_tier), 'state': 'rejected'})
        return True

    # =========================================================================
    # 8. AI ASSISTANT (GOOGLE GEMINI & OPENROUTER)
    # =========================================================================
    @api.model
    def ask_ai_assistant(self, user_prompt, stats_context):
        settings = self.env['all_in_one.settings'].get_singleton()
        provider = settings.ai_provider or 'gemini'

        system_instruction = (
            "أنت مستشار مالي وتشغيلي خبير لمشروع باتيسري ومقهى (Bakery, Pastry & Coffee) في المغرب (العملة: درهم DH).\n"
            "إليك البيانات المالية والتشغيلية الدقيقة للفترة المحددة حالياً في الفلتر:\n"
            f"{json.dumps(stats_context, ensure_ascii=False, indent=2)}\n\n"
            "قدم إجابات دقيقة، عملية، ومبنية على هذه الأرقام لتحسين صافي الربح وتقليل الخسائر والهدر."
        )

        if provider == 'gemini':
            api_key = (settings.gemini_api_key or '').strip()
            model = (settings.gemini_model or 'gemini-2.5-flash').strip()
            if not api_key:
                return _("يرجى إدخال مفتاح Google Gemini API Key في تبويب الإعدادات أولاً.")

            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            payload = {
                "contents": [{
                    "parts": [{"text": f"{system_instruction}\n\nسؤال المستخدم: {user_prompt}"}]
                }]
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST',
            )
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    result = json.loads(resp.read().decode('utf-8'))
                    return result['candidates'][0]['content']['parts'][0]['text']
            except Exception as e:
                return _("خطأ في الاتصال بـ Google Gemini API: %s", str(e))

        else:
            api_key = (settings.openrouter_api_key or '').strip()
            model = (settings.openrouter_model or 'google/gemini-2.5-flash').strip()
            if not api_key:
                return _("يرجى إدخال مفتاح OpenRouter API Key في تبويب الإعدادات أولاً.")

            url = "https://openrouter.ai/api/v1/chat/completions"
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_prompt},
                ],
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode('utf-8'),
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {api_key}',
                },
                method='POST',
            )
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    result = json.loads(resp.read().decode('utf-8'))
                    return result['choices'][0]['message']['content']
            except Exception as e:
                return _("خطأ في الاتصال بـ OpenRouter API: %s", str(e))