# Copyright 2025 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class IrModelFields(models.Model):
    _inherit = "ir.model.fields"
    _rec_names_search = ["name", "field_description"]

    @api.depends("name")
    def _compute_display_name(self):
        if self.env.context.get("technical_display_name"):
            for rec in self:
                rec.display_name = rec.name
        else:
            return super()._compute_display_name()
