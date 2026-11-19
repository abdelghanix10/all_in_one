from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import json
import logging
import urllib.request

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class AioAutomation(models.Model):
    _name = 'all_in_one.automation'
    _description = 'All In One Automation Workflow'
    _order = 'id desc'

    name = fields.Char(string='Workflow Name', required=True)
    active = fields.Boolean(string='Active', default=True)
    trigger_type = fields.Selection(
        [
            ('manual', 'Manual Trigger'),
            ('daily', 'Daily Schedule'),
            ('weekly', 'Weekly Schedule'),
            ('interval', 'Interval (Every N Hours)'),
        ],
        string='Trigger',
        default='daily',
        required=True,
    )
    schedule_time = fields.Char(string='Run At (HH:MM)', default='23:00')
    schedule_weekday = fields.Selection(
        [
            ('0', 'Monday'),
            ('1', 'Tuesday'),
            ('2', 'Wednesday'),
            ('3', 'Thursday'),
            ('4', 'Friday'),
            ('5', 'Saturday'),
            ('6', 'Sunday'),
        ],
        string='Day of Week',
        default='6',
    )
    interval_hours = fields.Integer(string='Interval (Hours)', default=24)
    steps_json = fields.Text(string='Workflow Nodes (JSON)', default='[]')
    last_run = fields.Datetime(string='Last Run', readonly=True)
    last_status = fields.Selection(
        [('never', 'Never'), ('success', 'Success'), ('error', 'Error')],
        string='Last Status',
        default='never',
        readonly=True,
    )
    last_message = fields.Text(string='Last Result', readonly=True)
    run_count = fields.Integer(string='Run Count', default=0, readonly=True)
    log_ids = fields.One2many('all_in_one.automation.log', 'automation_id', string='Execution Logs')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    def _get_steps(self):
        self.ensure_one()
        try:
            steps = json.loads(self.steps_json or '[]')
            return steps if isinstance(steps, list) else []
        except Exception:
            return []

    def _resolve_target_products(self, cfg):
        scope = cfg.get('scope', 'all_storable')
        if scope == 'tracked_card':
            return self.env['product.product'].sudo().search([('aio_tracked_card', '=', True)])
        if scope == 'pos_category' and cfg.get('pos_categ_id'):
            return self.env['product.product'].sudo().search([
                ('is_storable', '=', True),
                ('product_tmpl_id.pos_categ_ids', 'in', [int(cfg['pos_categ_id'])]),
            ])
        return self.env['product.product'].sudo().search([('is_storable', '=', True)])

    def _execute_step(self, step):
        step_type = step.get('type')
        cfg = step.get('config') or {}
        dashboard = self.env['all_in_one.dashboard']
        today = fields.Date.context_today(self)

        # 1. Reset Product Quantities to Target (default 0)
        if step_type == 'reset_product_qty':
            target_qty = float(cfg.get('target_qty', 0.0))
            products = self._resolve_target_products(cfg)
            updated = 0
            for prod in products:
                if not prod.is_storable:
                    continue
                delta = target_qty - prod.qty_available
                if abs(delta) > 1e-6:
                    dashboard._create_stock_adjustment_move(
                        prod, delta, f"AIO Automation: {self.name}"
                    )
                    updated += 1
            return f"Reset stock to {target_qty:g} for {updated} product(s)"

        # 2. Convert Remaining Positive Stock to Expired Loss + Reset to 0
        if step_type == 'record_expired_loss':
            department = cfg.get('department', 'pastry')
            products = self._resolve_target_products(cfg)
            logged = 0
            total_val = 0.0
            for prod in products:
                qty = prod.qty_available
                if qty <= 0:
                    continue
                unit_val = prod.lst_price or prod.standard_price or 0.0
                cat = dashboard._get_primary_pos_categ(prod)
                self.env['all_in_one.loss'].sudo().create({
                    'date': today,
                    'loss_type': 'expired',
                    'department': department,
                    'product_id': prod.id,
                    'pos_categ_id': cat.id if cat else False,
                    'note': f"Auto EOD ({self.name})",
                    'quantity': qty,
                    'unit_value': unit_val,
                })
                if prod.is_storable:
                    dashboard._create_stock_adjustment_move(
                        prod, -qty, f"AIO Expired Loss: {self.name}"
                    )
                logged += 1
                total_val += qty * unit_val
            return f"Logged {logged} expired product(s) totaling {total_val:.2f} DH and zeroed stock"

        # 3. Toggle Tracked Card is_storable ON / OFF
        if step_type == 'toggle_tracked_storable':
            enable = str(cfg.get('enable', 'true')).lower() in ('true', '1', 'yes')
            dashboard.toggle_tracked_card_storable(enable)
            return f"Tracked card stock tracking set to {'ON' if enable else 'OFF'}"

        # 4. Auto-Approve Pastry End-of-Day Reconciliation
        if step_type == 'auto_approve_reconcile':
            date_preset = cfg.get('date_preset', 'today')
            data = dashboard.get_all_in_one_data({'datePreset': date_preset})
            target_date = data['filter_info']['end_date']
            approved = 0
            for tier in data.get('reconciliation_tiers', []):
                if tier['state'] != 'approved' and tier['allocated_total'] > 0:
                    dashboard.approve_pastry_tier_reconciliation(
                        target_date, tier['price_tier'], tier['sold_qty'], tier['products']
                    )
                    approved += 1
            return f"Auto-approved {approved} pastry price tier(s) for {target_date}"

        # 5. Log Recurring Expense
        if step_type == 'create_expense':
            name = cfg.get('expense_name') or f"Auto: {self.name}"
            amount = float(cfg.get('amount', 0.0))
            if amount <= 0:
                return "Skipped expense (amount <= 0)"
            dashboard.create_expense_record({
                'name': name,
                'date': today,
                'expense_type': cfg.get('expense_type', 'other'),
                'department': cfg.get('department', 'shared'),
                'periodicity': cfg.get('periodicity', 'daily'),
                'amount': amount,
            })
            return f"Created expense '{name}' ({amount:.2f} DH)"

        # 6. Bulk Adjust Product Prices (% or Fixed)
        if step_type == 'adjust_prices':
            mode = cfg.get('mode', 'percent')
            delta = float(cfg.get('value', 0.0))
            if delta == 0:
                return "Skipped price adjustment (value = 0)"
            domain = [('available_in_pos', '=', True)]
            if cfg.get('pos_categ_id'):
                domain.append(('pos_categ_ids', 'in', [int(cfg['pos_categ_id'])]))
            tmpls = self.env['product.template'].sudo().search(domain)
            for tmpl in tmpls:
                if mode == 'percent':
                    new_price = max(0.0, round(tmpl.list_price * (1.0 + delta / 100.0), 2))
                else:
                    new_price = max(0.0, round(tmpl.list_price + delta, 2))
                tmpl.list_price = new_price
            return f"Adjusted prices ({delta:+g}{'%' if mode == 'percent' else ' DH'}) on {len(tmpls)} product(s)"

        # 7. Snapshot Daily KPIs
        if step_type == 'kpi_snapshot':
            data = dashboard.get_all_in_one_data({'datePreset': cfg.get('date_preset', 'today')})
            k = data['kpis']
            return (
                f"KPI Snapshot ({data['filter_info']['end_date']}): "
                f"Sales={k['total_sales']:.2f} DH | Expenses={k['total_expenses']:.2f} DH | "
                f"Losses={k['total_losses']:.2f} DH | Net Profit={k['total_net_profit']:.2f} DH"
            )

        # 8. Outgoing HTTP Webhook (n8n / Zapier / Telegram / Make)
        if step_type == 'webhook_http':
            url = (cfg.get('url') or '').strip()
            if not url:
                return "Skipped webhook (empty URL)"
            data = dashboard.get_all_in_one_data({'datePreset': 'today'})
            payload = {
                'workflow': self.name,
                'triggered_at': fields.Datetime.now().isoformat(),
                'kpis': data['kpis'],
                'note': cfg.get('custom_message', ''),
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST',
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                return f"Webhook POST {url} → HTTP {resp.status}"

        return f"Unknown node type: {step_type}"

    def execute_workflow(self, trigger_source='manual'):
        self.ensure_one()
        steps = self._get_steps()
        results = []
        status = 'success'

        try:
            if not steps:
                results.append("No action nodes configured.")
            for idx, step in enumerate(steps, start=1):
                msg = self._execute_step(step)
                results.append(f"[{idx}] {msg}")
        except Exception as err:
            status = 'error'
            results.append(f"ERROR: {err}")
            _logger.exception("AIO Automation '%s' failed", self.name)

        summary = "\n".join(results)
        now = fields.Datetime.now()
        self.sudo().write({
            'last_run': now,
            'last_status': status,
            'last_message': summary,
            'run_count': self.run_count + 1,
        })
        self.env['all_in_one.automation.log'].sudo().create({
            'automation_id': self.id,
            'trigger_source': trigger_source,
            'status': status,
            'details': summary,
        })
        return {
            'status': status,
            'summary': summary,
            'results': results,
        }

    def _is_due_now(self, now_utc, now_local):
        self.ensure_one()
        if self.trigger_type == 'manual':
            return False

        if self.trigger_type == 'interval':
            hours = max(1, self.interval_hours or 24)
            if not self.last_run:
                return True
            return (now_utc - self.last_run) >= timedelta(hours=hours)

        # Daily / Weekly schedule
        try:
            hh, mm = (self.schedule_time or '23:00').split(':')
            target_minutes = int(hh) * 60 + int(mm)
        except Exception:
            target_minutes = 23 * 60

        current_minutes = now_local.hour * 60 + now_local.minute
        if current_minutes < target_minutes:
            return False

        if self.trigger_type == 'weekly' and str(now_local.weekday()) != (self.schedule_weekday or '6'):
            return False

        if self.last_run:
            last_local = self.last_run.replace(tzinfo=ZoneInfo('UTC')).astimezone(now_local.tzinfo)
            if last_local.date() == now_local.date():
                return False

        return True

    @api.model
    def _cron_run_due_automations(self):
        now_utc = fields.Datetime.now()
        tz_name = self.env.user.tz or self.env.company.partner_id.tz or 'UTC'
        try:
            local_tz = ZoneInfo(tz_name)
        except Exception:
            local_tz = ZoneInfo('UTC')
        now_local = now_utc.replace(tzinfo=ZoneInfo('UTC')).astimezone(local_tz)

        workflows = self.sudo().search([('active', '=', True), ('trigger_type', '!=', 'manual')])
        for wf in workflows:
            if wf._is_due_now(now_utc, now_local):
                wf.execute_workflow(trigger_source='cron')


class AioAutomationLog(models.Model):
    _name = 'all_in_one.automation.log'
    _description = 'All In One Automation Execution Log'
    _order = 'create_date desc, id desc'

    automation_id = fields.Many2one('all_in_one.automation', required=True, ondelete='cascade')
    trigger_source = fields.Selection(
        [('manual', 'Manual'), ('cron', 'Scheduled')],
        default='manual',
    )
    status = fields.Selection([('success', 'Success'), ('error', 'Error')], default='success')
    details = fields.Text(string='Execution Details')
