# Copyright 2025 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models

ERROR_TYPES = [
    ("ok", "Ok"),
    ("already_transfered", "Already Transfered"),
    ("missing_error", "Missing Record"),
    ("other_error", "Other Error"),
]


class OdooDataTransferTemplateLogRecord(models.Model):
    _name = "odoo.data.transfer.log.record"
    _description = "Record transference log"

    log_id = fields.Many2one(
        comodel_name="odoo.data.transfer.log", ondelete="cascade", required=True
    )
    remote_id = fields.Integer(
        string="Remote Record Id",
    )
    local_id = fields.Reference(
        lambda self: [
            (m.model, m.name) for m in self.env["ir.model"].sudo().search([])
        ],
        string="Created Record",
    )
    error_type = fields.Selection(ERROR_TYPES)
    error_msg = fields.Char()
