# Copyright 2025 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest import mock

from odoo import _
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
        self.template_many2one = self.env.ref(
            "odoo_2_odoo_data_transfer.template_many2one"
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
        wiz_form.template_id = self.template_ok
        wiz_form.url = wiz_form.db_name = wiz_form.db_user = wiz_form.db_password = (
            "Foo"
        )
        wiz_form.record_limit = 10
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
        wiz_form.template_id = self.template_validation_error
        wiz_form.url = wiz_form.db_name = wiz_form.db_user = wiz_form.db_password = (
            "Foo"
        )
        wiz_form.record_limit = 10
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
        wiz_form.template_id = self.template_missing_error
        wiz_form.url = wiz_form.db_name = wiz_form.db_user = wiz_form.db_password = (
            "Foo"
        )
        wiz_form.record_limit = 10
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
        wiz_form.template_id = self.template_one2many
        wiz_form.url = wiz_form.db_name = wiz_form.db_user = wiz_form.db_password = (
            "Foo"
        )
        wiz_form.record_limit = 1
        wizard = wiz_form.save()
        wizard.action_validate()
        wizard.transfer_line_ids.filtered(
            lambda li: (li.local_target_field_type == "one2many")
        ).one2many_template_id = self.template_one2many_childs
        res = wizard.action_accept()
        log_id = self.env[res["res_model"]].browse(res["res_id"])
        self.assertEqual(log_id.state, "transfered")
        self.assertTrue(log_id.transfered_records_ids.local_id.child_ids)

    @mock.patch(
        "odoo.addons.odoo_2_odoo_data_transfer.wizards.odoo_data_transfer_wizard.OdooXmlrpcWrapper"
    )
    def test_many2one(self, mock_class, *args):
        mock_class.side_effect = (
            lambda url, db, username, password, lang, archived: MockXMLRpcWrapper(
                url, db, username, password, lang, archived, env=self.env
            )
        )
        wiz_form = Form(self.env["odoo.data.transfer.wizard"])
        wiz_form.template_id = self.template_many2one
        wiz_form.url = wiz_form.db_name = wiz_form.db_user = wiz_form.db_password = (
            "Foo"
        )
        wiz_form.record_limit = 1
        wizard = wiz_form.save()
        wizard.action_validate()
        wizard.transfer_line_ids._compute_related_model()
        res = wizard.action_accept()
        log_id = self.env[res["res_model"]].browse(res["res_id"])
        self.assertEqual(log_id.state, "transfered")
        self.assertEqual(log_id.transfered_records_counter, 1)
        self.assertTrue(log_id.transfered_records_ids.local_id.country_id)

    @mock.patch(
        "odoo.addons.odoo_2_odoo_data_transfer.wizards.odoo_data_transfer_wizard.OdooXmlrpcWrapper"
    )
    def test_migrate_failed(self, mock_class, *args):
        mock_class.side_effect = (
            lambda url, db, username, password, lang, archived: MockXMLRpcWrapper(
                url, db, username, password, lang, archived, env=self.env
            )
        )
        wiz_form = Form(self.env["odoo.data.transfer.wizard"])
        wiz_form.template_id = self.template_missing_error
        wiz_form.url = wiz_form.db_name = wiz_form.db_user = wiz_form.db_password = (
            "Foo"
        )
        wiz_form.record_limit = 10
        wizard = wiz_form.save()
        wizard.action_validate()
        res = wizard.action_accept()
        log_id = self.env[res["res_model"]].browse(res["res_id"])
        attempted_records1 = log_id.mapped("missing_error_record_ids.remote_id")
        wiz_form = Form(self.env["odoo.data.transfer.wizard"])
        wiz_form.template_id = self.template_ok
        wiz_form.url = wiz_form.db_name = wiz_form.db_user = wiz_form.db_password = (
            "Foo"
        )
        wiz_form.record_limit = 100
        wiz_form.migrate_failed = 1
        wizard = wiz_form.save()
        wizard.action_validate()
        res = wizard.action_accept()
        log_id = self.env[res["res_model"]].browse(res["res_id"])
        self.assertEqual(log_id.state, "transfered")
        self.assertEqual(log_id.transfered_records_counter, 10)
        attempted_records2 = log_id.mapped("transfered_records_ids.remote_id")
        self.assertEqual(attempted_records1, attempted_records2)

    def test_parse_value_conversions(self):
        TemplateLine = self.env["odoo.data.transfer.template.line"]
        test_cases = [
            ("char", False, False, bool),
            ("char", True, True, bool),
            ("char", 123, "123", str),
            ("char", "test@example.com", "test@example.com", str),
            ("integer", True, 1, int),
            ("integer", False, 0, int),
        ]
        for field_type, value, expected, expected_type in test_cases:
            with self.subTest(field_type=field_type, value=value):
                line = TemplateLine.new(
                    {
                        "migration_type": "normal",
                        "local_target_field_type": field_type,
                    }
                )
                result = line._parse_value(value)
                self.assertEqual(result, expected)
                self.assertIs(type(result), expected_type)

    def test_autocalculate_id_mappings_integer_to_char(self):
        partner = self.env["res.partner"].create(
            {
                "name": "Test Parent Company",
                "ref": "297682",
                "is_company": True,
            }
        )
        line = mock.Mock()
        line.related_model = "res.partner"
        line.remote_identifier_field = "id"
        line.local_identifier_field_id.name = "ref"
        line.local_identifier_field_id.ttype = "char"
        line._get_id_mappings.side_effect = lambda mappings: mappings
        wrapper = mock.Mock()
        wrapper.search_read.return_value = [{"id": 297682}]
        wrapper.fields_get.return_value = {"id": {"type": "integer"}}
        with mock.patch.object(
            type(self.env["odoo.data.transfer.wizard"]),
            "_get_related_remote_model",
            return_value="res.partner",
        ):
            mappings = self.env["odoo.data.transfer.wizard"]._autocalculate_id_mappings(
                wrapper, line
            )
        self.assertEqual(mappings, {297682: partner.id})
        line.write.assert_called_once_with(
            {"auto_id_mappings": str({297682: partner.id})}
        )

    def test_retry_with_empty_value(self):
        wiz_form = Form(self.env["odoo.data.transfer.wizard"])
        wiz_form.template_id = self.template_ok
        wiz_form.url = wiz_form.db_name = wiz_form.db_user = wiz_form.db_password = (
            "Foo"
        )
        wizard = wiz_form.save()

        vat_field = self.env["ir.model.fields"]._get("res.partner", "vat")
        wizard.transfer_line_ids = [
            (
                0,
                0,
                {
                    "remote_source_field": "vat",
                    "local_target_field_id": vat_field.id,
                    "retry_with_empty_value": True,
                },
            )
        ]

        record_dict = {
            "id": 12345,
            "name": "Test Partner",
            "vat": "INVALID_VAT",
        }

        def mock_create_record(values, **kwargs):
            if values["vat"]:
                raise ValidationError(_("Invalid VAT"))
            return self.env["res.partner"].create({"name": values["name"]})

        with mock.patch.object(
            type(wizard),
            "_create_record",
            side_effect=mock_create_record,
        ) as mocked_create:
            record, warning = wizard._create_record_with_retry(record_dict)

        self.assertEqual(mocked_create.call_count, 2)
        self.assertTrue(record.exists())
        self.assertEqual(record.name, "Test Partner")
        self.assertEqual(record_dict["vat"], "INVALID_VAT")
        self.assertEqual(warning["error_msg"], "Invalid VAT")
        self.assertEqual(warning["cleared_fields"], "vat")

    def test_retry_with_empty_value_migrated_with_exceptions(self):
        wiz_form = Form(self.env["odoo.data.transfer.wizard"])
        wiz_form.template_id = self.template_ok
        wiz_form.url = wiz_form.db_name = wiz_form.db_user = wiz_form.db_password = (
            "Foo"
        )
        wizard = wiz_form.save()
        vat_field = self.env["ir.model.fields"]._get("res.partner", "vat")
        wizard.transfer_line_ids = [
            (
                0,
                0,
                {
                    "remote_source_field": "vat",
                    "local_target_field_id": vat_field.id,
                    "retry_with_empty_value": True,
                },
            )
        ]
        log = self.env["odoo.data.transfer.log"].create(
            {
                "url": "Foo",
                "db_name": "Foo",
                "local_target_model_id": self.template_ok.local_target_model_id.id,
                "remote_source_model_name": self.template_ok.remote_source_model_name,
            }
        )
        wizard.log_id = log
        record_dict = {
            "id": 12345,
            "name": "Test Partner",
            "vat": "INVALID_VAT",
        }

        def mock_create_record(values, **kwargs):
            if values["vat"]:
                raise ValidationError(_("Invalid VAT"))
            return self.env["res.partner"].create({"name": values["name"]})

        with mock.patch.object(
            type(wizard),
            "_create_record",
            side_effect=mock_create_record,
        ):
            wizard.create_record(record_dict)
        self.assertEqual(len(log.transfered_records_ids), 1)
        self.assertEqual(len(log.migrated_with_exceptions_record_ids), 1)
        self.assertEqual(log.transfered_records_counter, 1)
        transferred_record = log.transfered_records_ids
        self.assertEqual(transferred_record.remote_id, 12345)
        self.assertEqual(
            log.migrated_with_exceptions_record_ids,
            transferred_record,
        )
        self.assertEqual(transferred_record.error_type, "migrated_with_exceptions")
        self.assertEqual(transferred_record.error_msg, "Invalid VAT")
        self.assertEqual(transferred_record.cleared_fields, "vat")
        self.assertFalse(log.missing_error_record_ids)
        self.assertFalse(log.other_error_record_ids)

    def test_retry_with_empty_value_boolean_constraint(self):
        active_field = self.env["ir.model.fields"]._get("res.partner", "active")
        with self.assertRaises(ValidationError):
            self.env["odoo.data.transfer.template.line"].create(
                {
                    "transfer_id": self.template_ok.id,
                    "remote_source_field": "active",
                    "local_target_field_id": active_field.id,
                    "retry_with_empty_value": True,
                }
            )
