# Copyright 2025 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class IrModelFields(models.Model):
    _inherit = "ir.model.fields"
    _rec_names_search = ["name", "field_description"]

    def name_get(self):
        if self.env.context.get("technical_display_name"):
            res = []
            for rec in self:
                res.append((rec.id, rec.name))
            return res
        else:
            return super().name_get()
