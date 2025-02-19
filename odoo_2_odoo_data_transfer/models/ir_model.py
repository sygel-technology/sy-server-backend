# Copyright 2025 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class IrModel(models.Model):
    _inherit = "ir.model"

    def name_get(self):
        if self.env.context.get("technical_display_name"):
            res = []
            for rec in self:
                res.append((rec.id, rec.model))
            return res
        else:
            return super().name_get()
