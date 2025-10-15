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

    job_channel_id = fields.Many2one(comodel_name="queue.job.channel")
    job_delay_seconds = fields.Integer(string="Job Delay (Seconds)")
    job_priority = fields.Integer(default=10)
    job_max_retries = fields.Integer(default=5)

    _sql_constraints = [
        (
            "job_priority",
            "CHECK (job_priority >= 0)",
            "Max retries should be greater than 0 or equal",
        ),
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

    def _get_log_values(self, method, url, **kwargs):
        kwargs.pop("headers", None)
        kwargs.pop("auth", None)
        ctx = self.env.context
        active_id = ctx.get("active_id") or ctx.get("params", {}).get("id")
        active_model = ctx.get("active_model") or ctx.get("params", {}).get("model")
        job_uuid = self.env.context.get("job_uuid", False)
        return {
            "api_id": self.id,
            "datetime": datetime.datetime.now(),
            "user_id": self.env.user.id,
            "executed_request": f"requests.{method}({url})",
            "executed_request_params": kwargs,
            "execution_record": f"{active_model}({active_id})"
            if active_model and active_id
            else False,
            "job_id": self.env["queue.job"].search([("uuid", "=", job_uuid)]).id
            if job_uuid
            else False,
        }

    def _create_log(self, method, url, new_cursor=False, status_vals=False, **kwargs):
        log_model = self.env["external.api.log"]
        if self.enable_logs:
            if new_cursor:
                new_cr = Registry(self.env.cr.dbname).cursor()
                env = api.Environment(new_cr, self.env.uid, self.env.context)
                log_model = env["external.api.log"]
            log_values = self._get_log_values(method, url, **kwargs)
            if status_vals:
                log_values.update(status_vals)
            res = log_model.create(log_values)
            if new_cursor:
                new_cr.commit()
                new_cr.close()
        else:
            res = log_model
        return res

    def _call_and_create_log(self, method, url, **kwargs):
        updated_kwargs = self._update_kwargs(**kwargs)
        url = self._build_url(url)
        request_func = getattr(requests, method)
        res = False
        new_cursor = False
        status_vals = {}
        try:
            res = request_func(url=url, **updated_kwargs)
        except requests.exceptions.Timeout as exception:
            new_cursor = True
            status_vals.update({"status": "exception", "response": exception})
            raise RetryableJobError(
                "Timeout connecting remote server. Must be retried later"
            ) from exception
        except requests.exceptions.RequestException as exception:
            status_vals.update({"status": "exception", "response": exception})
        else:
            status_vals.update(
                {
                    "status": "success" if res.ok else "http_error",
                    "status_code": res.status_code,
                    "response": res.text if not res.ok else "",
                }
            )
        finally:
            self._create_log(
                method, url, new_cursor=new_cursor, status_vals=status_vals, **kwargs
            )
        return res

    def call(self, method, url, **kwargs):
        self.ensure_one()
        self.env = self.sudo().env
        if self.state != "production":
            res = False
        else:
            res = self._call_and_create_log(method, url, **kwargs)
        return res

    def queued_call(self, method, url, **kwargs):
        self.ensure_one()
        self.env = self.sudo().env
        if self.state != "production":
            job = False
        else:
            job = self.with_delay(
                priority=kwargs.get("job_priority", False) or self.job_priority,
                eta=kwargs.get("job_delay_seconds", False) or self.job_delay_seconds,
                max_retries=kwargs.get("job_max_retries", False)
                or self.job_max_retries,
                channel=kwargs.get("job_channel", False)
                or self.job_channel_id.complete_name,
            ).call(method, url, **kwargs)
        return job
