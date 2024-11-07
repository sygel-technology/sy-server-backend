# Copyright 2024 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

CSS_UNITS_SELECTION = [
    ("px", "Pixels"),
    ("pt", "Points"),
    ("cm", "Centimeters"),
    ("em", "em (font size of parent)"),
    ("rem", "rem (font size of root)"),
    ("%", "% (of parent element)"),
]

CSS_FIELDS = [
    "manual_report_css",
    "text_size",
    "text_size_unit",
    "header_size",
    "header_size_unit",
]


class ResCompany(models.Model):
    _inherit = "res.company"

    computed_report_css = fields.Text(
        compute="_compute_computed_report_css",
        store=True,
    )
    manual_report_css = fields.Text()
    text_size = fields.Float(default=16.0)
    text_size_unit = fields.Selection(
        selection=CSS_UNITS_SELECTION, required=True, default="px"
    )
    header_size = fields.Float(default=32.0)
    header_size_unit = fields.Selection(
        selection=CSS_UNITS_SELECTION, required=True, default="px"
    )

    @api.model
    def _compute_computed_report_css_common(self, rec):
        # Function must also be called from the wizard
        rec.ensure_one()
        return f"""
            font-size: {rec.text_size}{rec.text_size_unit};
            h2 {{
                font-size: {rec.header_size}{rec.header_size_unit};
            }}
            {rec.manual_report_css or ''}
        """

    @api.depends(*CSS_FIELDS)
    def _compute_computed_report_css(self):
        for rec in self:
            rec.computed_report_css = self._compute_computed_report_css_common(rec)

    def write(self, values):
        res = super().write(values)
        old_style_fields = {
            "external_report_layout_id",
            "font",
            "primary_color",
            "secondary_color",
        }
        new_style_fields = set(CSS_FIELDS)
        if not new_style_fields.isdisjoint(values) and old_style_fields.isdisjoint(
            values
        ):
            self._update_asset_style()
        return res
