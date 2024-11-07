# Copyright 2024 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from .res_company import CSS_FIELDS


class BaseDocumentLayout(models.TransientModel):
    _inherit = "base.document.layout"

    computed_report_css = fields.Text(compute="_compute_computed_report_css")
    manual_report_css = fields.Text(
        related="company_id.manual_report_css",
        readonly=False,
    )
    text_size = fields.Float(
        related="company_id.text_size",
        readonly=False,
    )
    text_size_unit = fields.Selection(
        related="company_id.text_size_unit",
        readonly=False,
        required=True,
    )
    header_size = fields.Float(
        related="company_id.header_size",
        readonly=False,
    )
    header_size_unit = fields.Selection(
        related="company_id.header_size_unit",
        readonly=False,
        required=True,
    )

    def _compute_computed_report_css(self):
        for rec in self:
            rec.computed_report_css = (
                self.company_id._compute_computed_report_css_common(rec)
            )

    @api.depends(*CSS_FIELDS)
    def _compute_preview(self):
        return super()._compute_preview()
