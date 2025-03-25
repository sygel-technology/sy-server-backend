# Copyright 2025 Ángel García de la Chica Herrera <angel.garcia@sygel.es>
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0

from odoo_test_helper import FakeModelLoader

from odoo.tests import common


class TestFileDownload(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        cls.addClassCleanup(cls.loader.restore_registry)
        from .models.report import ReportTest

        cls.loader.update_registry((ReportTest,))

    def test_download_file(self):
        wizard = self.env["report.test"].create({})
        self.assertFalse(wizard.name)
        self.assertFalse(wizard.data)
        wizard.set_file()
        self.assertEqual(wizard.name, "Test_file_name.xlsx")
        self.assertTrue(wizard.data)
