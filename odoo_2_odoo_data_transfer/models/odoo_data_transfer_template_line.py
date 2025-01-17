# Copyright 2025 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import _, api, exceptions, fields, models


class OdooDataTransferTemplateLine(models.Model):
    _name = "odoo.data.transfer.template.line"
    _inherit = ["odoo.data.transfer.template.line.mixin"]
    _description = "Field mappings for a data transfer between Odoos"

    transfer_id = fields.Many2one(
        string="Template",
        comodel_name="odoo.data.transfer.template",
        required=True,
        ondelete="cascade",
    )

    @api.constrains("one2many_template_id")
    def _check_infinite_recursivity(self):
        for rec in self:
            if rec.one2many_template_id and (
                rec.one2many_template_id.transfer_line_ids.filtered(
                    "one2many_template_id"
                )
                or self.search_count(
                    [("one2many_template_id", "=", rec.transfer_id.id)]
                )
            ):
                raise exceptions.ValidationError(
                    _(
                        "The associated template lines can not"
                        " be associated to more templates"
                    )
                )
