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
    already_transfered_record_ids = fields.One2many(
        string="Already transfered records",
        comodel_name="odoo.data.transfer.log.record",
        inverse_name="log_id",
        domain=[("error_type", "=", "already_transfered")],
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
        compute="_compute_transfered_records_counter", string="Transfer Records"
    )
    record_total_counter = fields.Integer()

    @api.depends("transfered_records_ids")
    def _compute_transfered_records_counter(self):
        for rec in self:
            rec.transfered_records_counter = len(rec._get_valid_records())

    @api.model
    def _get_transfered_record_log_lines(self, model_id):
        """Returns record of model created befor with this module"""
        return (
            self.search([("local_target_model_id", "=", model_id.id)])
            .mapped("transfered_records_ids")
            .filtered(lambda li: li.local_id and li.local_id.exists())
        )

    def action_log(self):
        self.ensure_one()
        return {
            "name": _("Transference Log"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "odoo.data.transfer.log",
            "res_id": self.id,
        }

    def _copy_transfered_records_ids(self, transfered_records_ids):
        """Creates in already_transfered_record_ids of self
        another transfered_records_ids"""
        already_transfered_records_dict = {}
        already_transfered_records_dict.update(
            {
                "already_transfered_record_ids": [
                    (
                        0,
                        0,
                        {
                            "remote_id": rec.remote_id,
                            "local_id": "%s,%s" % (rec.local_id._name, rec.local_id.id),
                            "error_type": "already_transfered",
                        },
                    )
                    for rec in transfered_records_ids
                ]
            }
        )
        self.write(already_transfered_records_dict)

    def _calculate_state(self):
        for rec in self:
            if rec.missing_error_record_ids or rec.other_error_record_ids:
                if rec.transfered_records_ids:
                    rec.state = "transfered_error"
                else:
                    rec.state = "error"
            else:
                rec.state = "transfered"

    def _get_valid_records(self):
        self.ensure_one()
        return self.transfered_records_ids.filtered(
            lambda rec: rec.local_id and rec.local_id.exists()
        )

    def action_view_transfered_records(self):
        valid_recs = self._get_valid_records()
        view = self.env.ref(
            "odoo_2_odoo_data_transfer.odoo_data_transfer_log_record_tree"
        ).id
        return {
            "type": "ir.actions.act_window",
            "name": "Transfered Records",
            "view_type": "tree",
            "view_mode": "tree",
            "res_model": "odoo.data.transfer.log.record",
            "views": [(view, "tree")],
            "domain": [("id", "in", valid_recs.ids)],
            "target": "current",
        }
