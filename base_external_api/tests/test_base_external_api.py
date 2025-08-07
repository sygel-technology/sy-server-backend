# Copyright 2025 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest import mock

from odoo.tests.common import TransactionCase


class TestBaseExternalAPI(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.api = cls.env.ref("base_external_api.external_api_test_configuration")
        cls.api.state = "production"

    def test_basic_call(self):
        self.api.call(method="post", url="/test")
        log = self.env["external.api.log"].search([("api_id", "=", self.api.id)])
        self.assertEqual(log.status, "exception")

    def test_queued_call(self):
        job = self.api.queued_call(method="post", url="/test")
        log = self.env["external.api.log"].search([("api_id", "=", self.api.id)])
        self.assertTrue(job)
        self.assertEqual(job.uuid, log.job_id.uuid)

    def test_api_disabled(self):
        self.api.state = "disabled"
        res1 = self.api.call(method="post", url="/test")
        res2 = self.api.queued_call(method="post", url="/test")
        logs = self.env["external.api.log"].search([("api_id", "=", self.api.id)])
        self.assertFalse(res1)
        self.assertFalse(res2)
        self.assertFalse(logs)

    def test_log_disabled(self):
        self.api.enable_logs = False
        self.api.call(method="post", url="/test")
        log = self.env["external.api.log"].search([("api_id", "=", self.api.id)])
        self.assertEqual(len(log), 0)

    @mock.patch("requests.post")
    def test_mock_login_error(self, mocked_post):
        mocked_post.return_value.ok = False
        mocked_post.return_value.status_code = 400
        mocked_post.return_value.text = "I don't know"
        self.api.call(method="post", url="/test")
        log = self.env["external.api.log"].search([("api_id", "=", self.api.id)])
        self.assertEqual(log.status, "http_error")
        self.assertEqual(log.status_code, 400)
        self.assertEqual(log.response, "I don't know")

    @mock.patch("requests.post")
    def test_mock_ok(self, mocked_post):
        mocked_post.return_value.ok = True
        mocked_post.return_value.status_code = 200
        mocked_post.return_value.text = "I do know"
        self.api.call(method="post", url="/test")
        log = self.env["external.api.log"].search([("api_id", "=", self.api.id)])
        self.assertEqual(log.status, "success")
        self.assertEqual(log.status_code, 200)
