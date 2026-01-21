# Copyright 2025 Ángel García de la Chica Herrera <angel.garcia@sygel.es>
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0

from odoo_test_helper import FakeModelLoader

from odoo.tests import common


class TestFileDownload(common.TransactionCase):
    @classmethod
    def setUp(self):
        super().setUpClass()
        self.loader = FakeModelLoader(self.env, self.__module__)
        self.loader.backup_registry()
        self.addClassCleanup(self.loader.restore_registry)
        from .models.report import ReportTest

        self.loader.update_registry((ReportTest,))

        def tearDown(self):
            self.loader.restore_registry()
            super().tearDown()

    def test_download_file(self):
        wizard = self.env["report.test"].create({})
        self.assertFalse(wizard.name)
        self.assertFalse(wizard.data)
        wizard.set_file()
        self.assertEqual(wizard.name, "Test_file_name.xlsx")
        self.assertTrue(wizard.data)
