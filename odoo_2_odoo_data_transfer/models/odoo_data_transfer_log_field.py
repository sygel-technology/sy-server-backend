# Copyright 2025 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class OdooDataTransferTemplateLogField(models.Model):
    _name = "odoo.data.transfer.log.field"
    _inherit = ["odoo.data.transfer.template.line.mixin"]
    _description = "Data transference wizard event field mappings log"

    log_id = fields.Many2one(
        string="Log",
        comodel_name="odoo.data.transfer.log",
        required=True,
        ondelete="cascade",
    )
    model = fields.Char(related="log_id.local_target_model_id.model")
