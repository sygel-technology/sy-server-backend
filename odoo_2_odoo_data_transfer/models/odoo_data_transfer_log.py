# Copyright 2025 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class OdooDataTransferTemplateLog(models.Model):
    _name = "odoo.data.transfer.log"
    _description = "Data transference wizard event log"
    _inherit = ["odoo.data.transfer.template.mixin"]

    state = fields.Selection(
        selection=[
            ("error", "Error"),
            ("transfered_error", "Transfered with Errors"),
            ("transfered", "Transfered"),
        ],
        required=True,
        default="error",
    )
    remote_source_model_name = fields.Char(readonly=True)
    local_target_model_id = fields.Many2one(readonly=True)
    domain = fields.Char(readonly=True)
    date_start = fields.Datetime(
        default=fields.Datetime.now,
        readonly=True,
    )
    date_end = fields.Datetime(
        readonly=True,
    )
    url = fields.Char(
        required=True,
        readonly=True,
    )
    db_name = fields.Char(
        required=True,
        readonly=True,
    )
    transfered_field_ids = fields.One2many(
        string="Transfered Field",
        comodel_name="odoo.data.transfer.log.field",
        inverse_name="log_id",
    )

    transfered_records_ids = fields.One2many(
        string="Transfered Records",
        comodel_name="odoo.data.transfer.log.record",
        inverse_name="log_id",
        domain=["|", ("error_type", "=", False), ("error_type", "=", "ok")],
    )
    missing_error_record_ids = fields.One2many(
        string="Records with Missing Errors",
        comodel_name="odoo.data.transfer.log.record",
        inverse_name="log_id",
        domain=[("error_type", "=", "missing_error")],
    )
    other_error_record_ids = fields.One2many(
        string="Records with other errors",
        comodel_name="odoo.data.transfer.log.record",
        inverse_name="log_id",
        domain=[("error_type", "=", "other_error")],
    )
    transfered_records_counter = fields.Integer(
        compute="_compute_transfered_records_counter",
        store=True,
    )
    record_total_counter = fields.Integer()

    first_transferred_id = fields.Integer(
        compute="_compute_transfered_records_counter",
        store=True,
    )
    last_transferred_id = fields.Integer(
        compute="_compute_transfered_records_counter",
        store=True,
    )
    is_failed_migration = fields.Boolean(readonly=True)

    @api.depends("transfered_records_ids")
    def _compute_transfered_records_counter(self):
        for rec in self:
            rec.transfered_records_counter = len(rec.transfered_records_ids)
            rec.first_transferred_id = (
                self.env["odoo.data.transfer.log.record"]
                .search([("log_id", "=", rec.id)], order="remote_id asc", limit=1)
                .remote_id
            )
            rec.last_transferred_id = (
                self.env["odoo.data.transfer.log.record"]
                .search([("log_id", "=", rec.id)], order="remote_id desc", limit=1)
                .remote_id
            )

    @api.model
    def _get_last_transfered_record_id(self, model_id):
        return self.search(
            [("local_target_model_id", "=", model_id.id)],
            order="last_transferred_id desc",
            limit=1,
        ).last_transferred_id

    @api.model
    def _get_failed_record_ids(self, model_id):
        failed_records = set()
        fixed_records = set()
        logs = self.search([("local_target_model_id", "=", model_id.id)])
        for log in logs:
            failed_records.update(log.missing_error_record_ids.mapped("remote_id"))
            failed_records.update(log.other_error_record_ids.mapped("remote_id"))
            if log.is_failed_migration:
                fixed_records.update(log.transfered_records_ids.mapped("remote_id"))
        return failed_records - fixed_records

    def action_log(self):
        self.ensure_one()
        return {
            "name": _("Transference Log"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "odoo.data.transfer.log",
            "res_id": self.id,
        }

    def _calculate_state(self):
        for rec in self:
            if rec.missing_error_record_ids or rec.other_error_record_ids:
                if rec.transfered_records_ids:
                    rec.state = "transfered_error"
                else:
                    rec.state = "error"
            else:
                rec.state = "transfered"
