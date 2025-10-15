# Copyright 2025 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest import mock

from odoo.tests.common import TransactionCase

OK_MSG_200 = "It does work!"
ERROR_MSG_401 = "Unauthorized"
ERROR_MSG_404 = "Url not found"
USER = "admin"
PASSWD = "admin"
APIKEY = "qwerty123"


class MockResponse:
    def __init__(self, ok, status_code, text):
        self.ok = ok
        self.status_code = status_code
        self.text = text


def mocked_requests_get(*args, **kwargs):
    url = args.get(0) if len(args) else kwargs.get("url")
    if url == "https://www.test.com/test/test":
        res = MockResponse(True, 200, OK_MSG_200)
    else:
        res = MockResponse(False, 404, ERROR_MSG_404)
    return res


def mocked_requests_basic_auth(*args, **kwargs):
    auth = kwargs.get("auth", False)
    if auth and auth[0] == USER and auth[1] == PASSWD:
        res = MockResponse(True, 200, OK_MSG_200)
    else:
        res = MockResponse(False, 401, ERROR_MSG_401)
    return res


def mocked_requests_apikey_auth(*args, **kwargs):
    apikey = kwargs.get("headers", {}).get("api-key")
    if apikey and apikey == APIKEY:
        res = MockResponse(True, 200, OK_MSG_200)
    else:
        res = MockResponse(False, 401, ERROR_MSG_401)
    return res


class TestBaseExternalAPI(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.api = cls.env.ref("base_external_api.external_api_test_configuration")
        cls.api.state = "production"

    def test_basic_call_exception(self):
        self.api.call(method="post", url="/test")
        log = self.env["external.api.log"].search([("api_id", "=", self.api.id)])
        self.assertEqual(log.status, "exception")

    def test_queued_call(self):
        job = self.api.queued_call(method="post", url="/test")
        job.perform()
        log = self.env["external.api.log"].search([("api_id", "=", self.api.id)])
        self.assertTrue(job)
        self.assertTrue(log)
        self.assertEqual(log.status, "exception")
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
    def test_mock_ok(self, mocked_post):
        mocked_post.return_value.ok = True
        mocked_post.return_value.status_code = 200
        mocked_post.return_value.text = "I do know"
        self.api.call(method="post", url="/test")
        log = self.env["external.api.log"].search([("api_id", "=", self.api.id)])
        self.assertEqual(log.status, "success")
        self.assertEqual(log.status_code, 200)

    @mock.patch("requests.post")
    def test_mock_error_password(self, mocked_post):
        self.api.write(
            {
                "authentication_method": "basic",
                "auth_basic_user": "admin",
                "auth_basic_passwd": "notelocreesnitu",
            }
        )
        mocked_post.return_value.ok = False
        mocked_post.return_value.status_code = 401
        mocked_post.return_value.text = "Unauthorized. Bad password"
        self.api.call(method="post", url="/test")
        log = self.env["external.api.log"].search([("api_id", "=", self.api.id)])
        self.assertEqual(log.status, "http_error")
        self.assertEqual(log.status_code, 401)
        self.assertEqual(log.response, "Unauthorized. Bad password")

    @mock.patch("requests.post")
    def test_mock_login_error_apikey(self, mocked_post):
        self.api.write(
            {
                "authentication_method": "apikey",
                "auth_apikey_key": "api-key",
                "auth_apikey_value": "notelocreesnitu",
            }
        )
        mocked_post.return_value.ok = False
        mocked_post.return_value.status_code = 401
        mocked_post.return_value.text = "Unauthorized. Bad api-key"
        self.api.call(method="post", url="/test")
        log = self.env["external.api.log"].search([("api_id", "=", self.api.id)])
        self.assertEqual(log.status, "http_error")
        self.assertEqual(log.status_code, 401)
        self.assertEqual(log.response, "Unauthorized. Bad api-key")

    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_successful_call(self, mock_get):
        res = self.api.call(method="get", url="/test")
        log = self.env["external.api.log"].search([("api_id", "=", self.api.id)])
        self.assertEqual(log.status, "success")
        self.assertEqual(log.status_code, 200)
        self.assertTrue(res.ok)

    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_unsuccessful_call(self, mock_get):
        self.api.call(method="get", url="/testtt")
        log = self.env["external.api.log"].search([("api_id", "=", self.api.id)])
        self.assertEqual(log.status, "http_error")
        self.assertEqual(log.status_code, 404)
        self.assertEqual(log.response, ERROR_MSG_404)

    @mock.patch("requests.get", side_effect=mocked_requests_apikey_auth)
    def test_basic_auth_error(self, mock_get):
        self.api.write(
            {
                "authentication_method": "basic",
                "auth_basic_user": "admin",
                "auth_basic_passwd": "notelocreesnitu",
            }
        )
        self.api.call(method="get", url="/test")
        log = self.env["external.api.log"].search([("api_id", "=", self.api.id)])
        self.assertEqual(log.status, "http_error")
        self.assertEqual(log.status_code, 401)
        self.assertEqual(log.response, ERROR_MSG_401)

    @mock.patch("requests.get", side_effect=mocked_requests_basic_auth)
    def test_basic_auth_ok(self, mock_get):
        self.api.write(
            {
                "authentication_method": "basic",
                "auth_basic_user": USER,
                "auth_basic_passwd": PASSWD,
            }
        )
        res = self.api.call(method="get", url="/test")
        log = self.env["external.api.log"].search([("api_id", "=", self.api.id)])
        self.assertEqual(log.status, "success")
        self.assertEqual(log.status_code, 200)
        self.assertTrue(res.ok)

    @mock.patch("requests.get", side_effect=mocked_requests_basic_auth)
    def test_apikey_auth_error(self, mock_get):
        self.api.write(
            {
                "authentication_method": "apikey",
                "auth_apikey_key": "api-key",
                "auth_apikey_value": "notelocreesnitu",
            }
        )
        self.api.call(method="get", url="/test")
        log = self.env["external.api.log"].search([("api_id", "=", self.api.id)])
        self.assertEqual(log.status, "http_error")
        self.assertEqual(log.status_code, 401)
        self.assertEqual(log.response, ERROR_MSG_401)

    @mock.patch("requests.get", side_effect=mocked_requests_apikey_auth)
    def test_apikey_auth_ok(self, mock_get):
        self.api.write(
            {
                "authentication_method": "apikey",
                "auth_apikey_key": "api-key",
                "auth_apikey_value": APIKEY,
            }
        )
        res = self.api.call(method="get", url="/test")
        log = self.env["external.api.log"].search([("api_id", "=", self.api.id)])
        self.assertEqual(log.status, "success")
        self.assertEqual(log.status_code, 200)
        self.assertTrue(res.ok)
