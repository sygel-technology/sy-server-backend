# Copyright 2025 Ángel García de la Chica Herrera <angel.garcia@sygel.es>
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0

import base64
from io import BytesIO

import xlsxwriter

from odoo import models


class ReportTest(models.TransientModel):
    _inherit = "file.download.model"
    _name = "report.test"
    _description = "Report Test"

    def get_filename(self):
        name = "Test_file_name.xlsx"
        return name

    def get_content(self):
        output = BytesIO()
        wb = xlsxwriter.Workbook(output, {"in_memory": True})
        wb.close()
        datas = base64.encodebytes(output.getvalue())
        return datas
