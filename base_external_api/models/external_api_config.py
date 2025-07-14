# Copyright 2025 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import datetime
from urllib.parse import urljoin

import requests

from odoo import api, fields, models
from odoo.modules.registry import Registry

from odoo.addons.queue_job.exception import RetryableJobError


class ExternalApiConfig(models.Model):
    _name = "external.api.config"
    _description = "Defines a external api used by the system and its connection data"

    name = fields.Char(required=True)

    base_url = fields.Char(
        string="Base URL",
        required=True,
        help="Common URL of all the endpoints of the external API",
    )
    state = fields.Selection(
        selection=[
            ("test", "Test"),
            ("production", "Production"),
            ("disabled", "Disabled"),
        ],
        default="test",
        required=True,
        help="Only production connections will be executed",
    )
    enable_logs = fields.Boolean(
        default=True,
    )
    authentication_method = fields.Selection(
        string="Auth method",
        selection=[("none", "None"), ("basic", "Basic Auth"), ("apikey", "API Key")],
        default="none",
        required=True,
    )

    auth_basic_user = fields.Char(string="User")
    auth_basic_passwd = fields.Char(string="Password")

    auth_apikey_key = fields.Char(string="Header", default="api-key")
    auth_apikey_value = fields.Char(string="APIKey value")

    job_delay_seconds = fields.Integer(string="Job Delay (Seconds)")
    job_max_retries = fields.Integer(default=5)

    _sql_constraints = [
        (
            "job_max_retries",
            "CHECK (job_max_retries > 0)",
            "Max retries should be greater than 0",
        ),
        ("name_uniq", "unique(name)", "External API name must be unique."),
    ]

    def _build_url(self, endpoint):
        self.ensure_one()
        url = self.base_url
        if endpoint:
            url = urljoin(url.rstrip("/") + "/", endpoint.lstrip("/"))
        return url

    def _update_kwargs(self, **kwargs):
        """Updates query kwargs adding security parameters"""
        self.ensure_one()
        res = kwargs
        if self.authentication_method == "apikey":
            res.setdefault("headers", {})[self.auth_apikey_key] = self.auth_apikey_value
        if self.authentication_method == "basic":
            res["auth"] = (self.auth_basic_user, self.auth_basic_passwd)
        return res

    def _create_log(self, method, url, **kwargs):
        if self.enable_logs:
            ctx = self.env.context
            active_id = ctx.get("active_id") or ctx.get("params", {}).get("id")
            active_model = ctx.get("active_model") or ctx.get("params", {}).get("model")
            res = self.env["external.api.log"].create(
                {
                    "api_id": self.id,
                    "datetime": datetime.datetime.now(),
                    "user_id": self.env.user.id,
                    "executed_request": f"requests.{method}({url}, {kwargs})",
                    "execution_record": f"{active_model}({active_id})"
                    if active_model and active_id
                    else False,
                }
            )
        else:
            res = False
        return res

    @api.model
    def _update_log(self, log, vals, new_cursor=False):
        if self.enable_logs:
            if new_cursor:
                new_cr = Registry(self.env.cr.dbname).cursor()
                env = api.Environment(new_cr, self.env.uid, self.env.context)
                log = env["external.api.log"].browse(log.id)
            log.update(vals)
            if new_cursor:
                new_cr.commit()
                new_cr.close()

    def _call_and_update_log(self, method, url, log, **kwargs):
        request_func = getattr(requests, method)
        res = False
        try:
            res = request_func(url=url, **kwargs)
        except requests.exceptions.Timeout as error:
            self._update_log(log, {"status": "exception", "response": error}, True)
            raise RetryableJobError(
                "Timeout connecting remote server. Must be retried later"
            ) from error
        except requests.exceptions.RequestException as error:
            self._update_log(log, {"status": "exception", "response": error})
        else:
            self._update_log(
                log,
                {
                    "status": "success" if res.ok else "http_error",
                    "status_code": res.status_code,
                    "response": res.text if not res.ok else "",
                },
            )
        return res

    def call(self, method, url, queued=False, **kwargs):
        self.ensure_one()
        if self.state != "production":
            res = False
        else:
            url = self._build_url(url)
            updated_kwargs = self._update_kwargs(**kwargs)
            log = self._create_log(method, url, **updated_kwargs)
            res = self._call_and_update_log(method, url, log, **updated_kwargs)
        return res

    def queued_call(self, method, url, **kwargs):
        self.ensure_one()
        if self.state != "production":
            job = False
        else:
            url = self._build_url(url)
            updated_kwargs = self._update_kwargs(**kwargs)
            log = self._create_log(method, url, **updated_kwargs)
            job = self.with_delay(
                eta=self.job_delay_seconds,
                max_retries=self.job_max_retries,
            )._call_and_update_log(method, url, log, **updated_kwargs)
            self._update_log(
                log,
                {"job_id": self.env["queue.job"].search([("uuid", "=", job.uuid)]).id},
            )
        return job
