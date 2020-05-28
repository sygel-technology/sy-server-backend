# Copyright 2020 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields


class AccountAccount(models.Model):
    _inherit = "account.account"

    external_id = fields.Char(
        string="External ID",
        compute="compute_external_id",
        store=True,
    )

    def compute_external_id(self):
        for sel in self:
            sel.external_id = sel.get_external_id()
