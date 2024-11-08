# Copyright 2024 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64

from odoo.tests.common import TransactionCase


class TestReportsFontSize(TransactionCase):
    def setUp(cls):
        # Well use demo data. We dont care about data, only report css
        res = super().setUp()
        cls.company_id = cls.env.company
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
