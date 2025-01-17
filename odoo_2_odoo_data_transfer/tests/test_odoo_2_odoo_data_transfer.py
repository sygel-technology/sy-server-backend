# Copyright 2025 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest import mock

from odoo.exceptions import ValidationError
from odoo.tests.common import Form, TransactionCase


class MockXMLRpcWrapper:
    def __init__(self, url, db, username, password, lang, archived, env=None):
        self.env = env

    def search_read(self, model, domain, fields, limit=None, offset=0):
        res = self.env[model].search_read(
            domain=domain, fields=fields, limit=limit, offset=offset
        )
        return res

    def search_count(self, model, domain, fields, limit=None, offset=0):
        return self.env[model].search_count(
            domain=domain, fields=fields, limit=limit, offset=offset
        )

    def fields_get(self, model, fields):
        return self.env[model].fields_get(fields)


class TestOdoo2OdooDataTransfer(TransactionCase):
    def setUp(self):
        super().setUp()
        self.template_ok = self.env.ref("odoo_2_odoo_data_transfer.template_ok")
        self.template_validation_error = self.env.ref(
            "odoo_2_odoo_data_transfer.template_validation"
        )
        self.template_missing_error = self.env.ref(
            "odoo_2_odoo_data_transfer.template_missing"
        )
        self.template_one2many = self.env.ref(
            "odoo_2_odoo_data_transfer.template_one2many"
        )
        self.template_one2many_childs = self.env.ref(
            "odoo_2_odoo_data_transfer.template_one2many_childs"
        )

    @mock.patch(
        "odoo.addons.odoo_2_odoo_data_transfer.wizards.odoo_data_transfer_wizard.OdooXmlrpcWrapper"
    )
    def test_wizard_ok(self, mock_class, *args):
        mock_class.side_effect = (
            lambda url, db, username, password, lang, archived: MockXMLRpcWrapper(
                url, db, username, password, lang, archived, env=self.env
            )
        )
        wiz_form = Form(self.env["odoo.data.transfer.wizard"])
        wiz_form.url = (
            wiz_form.db_name
        ) = wiz_form.db_user = wiz_form.db_password = "Foo"
        wiz_form.record_limit = 10
        wiz_form.template_id = self.template_ok
        wizard = wiz_form.save()
        wizard.action_validate()
        res = wizard.action_accept()
        log_id = self.env[res["res_model"]].browse(res["res_id"])
        self.assertEqual(log_id.state, "transfered")
        self.assertEqual(log_id.transfered_records_counter, 10)

    @mock.patch(
        "odoo.addons.odoo_2_odoo_data_transfer.wizards.odoo_data_transfer_wizard.OdooXmlrpcWrapper"
    )
    def test_validation_error(self, mock_class, *args):
        mock_class.side_effect = (
            lambda url, db, username, password, lang, archived: MockXMLRpcWrapper(
                url, db, username, password, lang, archived, env=self.env
            )
        )
        wiz_form = Form(self.env["odoo.data.transfer.wizard"])
        wiz_form.url = (
            wiz_form.db_name
        ) = wiz_form.db_user = wiz_form.db_password = "Foo"
        wiz_form.record_limit = 10
        wiz_form.template_id = self.template_validation_error
        wizard = wiz_form.save()
        with self.assertRaises(ValidationError):
            wizard.action_validate()

    @mock.patch(
        "odoo.addons.odoo_2_odoo_data_transfer.wizards.odoo_data_transfer_wizard.OdooXmlrpcWrapper"
    )
    def test_missing_error(self, mock_class, *args):
        mock_class.side_effect = (
            lambda url, db, username, password, lang, archived: MockXMLRpcWrapper(
                url, db, username, password, lang, archived, env=self.env
            )
        )
        wiz_form = Form(self.env["odoo.data.transfer.wizard"])
        wiz_form.url = (
            wiz_form.db_name
        ) = wiz_form.db_user = wiz_form.db_password = "Foo"
        wiz_form.record_limit = 10
        wiz_form.template_id = self.template_missing_error
        wizard = wiz_form.save()
        wizard.action_validate()
        res = wizard.action_accept()
        log_id = self.env[res["res_model"]].browse(res["res_id"])
        self.assertTrue(log_id.missing_error_record_ids)

    @mock.patch(
        "odoo.addons.odoo_2_odoo_data_transfer.wizards.odoo_data_transfer_wizard.OdooXmlrpcWrapper"
    )
    def test_one2many(self, mock_class, *args):
        mock_class.side_effect = (
            lambda url, db, username, password, lang, archived: MockXMLRpcWrapper(
                url, db, username, password, lang, archived, env=self.env
            )
        )
        wiz_form = Form(self.env["odoo.data.transfer.wizard"])
        wiz_form.url = (
            wiz_form.db_name
        ) = wiz_form.db_user = wiz_form.db_password = "Foo"
        wiz_form.record_limit = 1
        wiz_form.template_id = self.template_one2many
        wizard = wiz_form.save()
        wizard.action_validate()
        wizard.transfer_line_ids.filtered(
            lambda li: (li.local_target_field_type == "one2many")
        ).one2many_template_id = self.template_one2many_childs
        res = wizard.action_accept()
        log_id = self.env[res["res_model"]].browse(res["res_id"])
        self.assertEqual(log_id.state, "transfered")
        self.assertTrue(log_id.transfered_records_ids.local_id.child_ids)
