# Copyright 2020 Valentin Vinagre <valentin.vinagre@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    show_internal_users_cc = fields.Boolean(
        string='Show Internal Users CC',
        related='company_id.show_internal_users_cc',
        readonly=False
    )
    cc_blocked_models = fields.Many2many(
        string='CC Blocked Models',
        comodel_name="ir.model",
        related='company_id.cc_blocked_models',
        readonly=False
    )
