# Copyright 2025 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models
from odoo.tools.safe_eval import safe_eval


class OdooDataTransferTemplate(models.Model):
    _name = "odoo.data.transfer.template"
    _description = "Model and field mappings for a data transfer between Odoos"
    _inherit = ["odoo.data.transfer.template.mixin"]

    name = fields.Char(required=True)
    description = fields.Text()
    transfer_line_ids = fields.One2many(
        string="Template Lines",
        comodel_name="odoo.data.transfer.template.line",
        inverse_name="transfer_id",
    )
    is_many2one_template = fields.Boolean(
        help="Mark this only if the template will be used "
        "inside other template to create a related record"
    )

    @api.constrains("domain")
    def _check_domain(self):
        for field in self:
            try:
                safe_eval(field.domain)
            except SyntaxError as e:
                raise exceptions.ValidationError from e(
                    _("The domain is bad formed: {}").format(e)
                )

    def copy(self, default=None):
        self.ensure_one()
        new_template = super().copy(default)
        for line in self.transfer_line_ids:
            line.copy({"transfer_id": new_template.id})
        return new_template
