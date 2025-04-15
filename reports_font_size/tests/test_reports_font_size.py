# Copyright 2024 Alberto Martínez <alberto.martinez@sygel.es>
# Copyright 2025 Juan Alberto Raja <juan.raja@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64

from odoo.tests.common import TransactionCase


class TestReportsFontSize(TransactionCase):
    def setUp(self):
        # Well use demo data. We dont care about data, only report css
        res = super().setUp()
        self.company_id = self.env.company
        return res

    def test_reports_font_size(self):
        """Change default company report layout config,
        and check if the css file is updated
        """
        self.company_id.write(
            {
                "text_size": 20,
                "text_size_unit": "pt",
                "header_size": 2,
                "header_size_unit": "em",
                "manual_report_css": "font-weight: bold;",
            }
        )
        css = str(
            base64.b64decode(self.env.ref("web.asset_styles_company_report").datas)
        )
        self.assertIn("font-size: 20.0pt;", css)
        self.assertIn("font-size: 2.0em;", css)
        self.assertIn("font-weight: bold;", css)

    def test_manual_css_only(self):
        """Only manual CSS without font sizes."""
        self.company_id.write(
            {
                "manual_report_css": "color: red;",
            }
        )
        css = str(
            base64.b64decode(self.env.ref("web.asset_styles_company_report").datas)
        )
        self.assertIn("color: red;", css)

    def test_empty_manual_css(self):
        """Ensure empty manual CSS does not cause issues."""
        self.company_id.write(
            {
                "manual_report_css": "",
            }
        )
        css = str(
            base64.b64decode(self.env.ref("web.asset_styles_company_report").datas)
        )
        self.assertNotIn("font-weight: bold;", css)

    def test_no_values_set(self):
        """Ensure default CSS is present if nothing is configured."""
        css = str(
            base64.b64decode(self.env.ref("web.asset_styles_company_report").datas)
        )
        self.assertNotIn("o_report_font_size_custom", css)
        self.assertNotIn("font-weight: bold;", css)

    def test_document_layout_compute(self):
        """Ensure computed_report_css is computed and _compute_preview is triggered."""
        layout = (
            self.env["base.document.layout"]
            .with_context(allowed_company_ids=[self.company_id.id])
            .create({})
        )
        layout._compute_computed_report_css()
        self.assertTrue(layout.computed_report_css is not None)

        layout.text_size = 15
        layout._compute_preview()
