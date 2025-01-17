# Copyright 2025 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import fields, models


class OdooDataTransferWizardLine(models.TransientModel):
    _name = "odoo.data.transfer.wizard.line"
    _inherit = ["odoo.data.transfer.template.line.mixin"]
    _description = "Field mappings for a data transfer between Odoos"

    transfer_id = fields.Many2one(
        string="Template", comodel_name="odoo.data.transfer.wizard", required=True
    )
