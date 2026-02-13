# Copyright 2024 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64

from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestReportCSSInjection(TransactionCase):
    def setUp(cls):
        # Well use demo data. We dont care about data, only report css
        res = super().setUp()
        cls.company_id = cls.env.company
        return res

    def test_document_layout_form(self):
        """Ensure computed_report_css is computed and _compute_preview is triggered"""
        layout = (
            self.env["base.document.layout"]
            .with_context(allowed_company_ids=[self.company_id.id])
            .create({"report_layout_id": self.env.ref("web.report_layout_standard").id})
        )
        preview_before = layout.preview
        doc_layout = Form(layout)
        doc_layout.text_size = 20
        doc_layout.text_size_unit = "pt"
        doc_layout.header_size = 2
        doc_layout.header_size_unit = "em"
        layout = doc_layout.save()
        self.assertIn("font-size: 20.0pt;", layout.computed_report_css)
        self.assertIn("font-size: 2.0em;", layout.computed_report_css)
        self.assertNotEqual(preview_before, layout.preview)

    def test_css_injection(self):
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

    def test_css_update(self):
        """Make sure that the css injection is still there after an update"""
        self.company_id.write(
            {
                "text_size": 20,
                "text_size_unit": "pt",
                "header_size": 2,
                "header_size_unit": "em",
                "manual_report_css": "font-weight: bold;",
            }
        )
        xml_id = "web.asset_styles_company_report"
        record = self.env.ref(xml_id)

        self.env["ir.model.data"]._update_xmlids(
            [
                {
                    "xml_id": xml_id,
                    "record": record,
                    "noupdate": True,
                }
            ]
        )

        css = str(base64.b64decode(record.datas))
        self.assertIn("font-size: 20.0pt;", css)
        self.assertIn("font-size: 2.0em;", css)
        self.assertIn("font-weight: bold;", css)
