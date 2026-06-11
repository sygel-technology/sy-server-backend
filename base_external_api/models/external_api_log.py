# Copyright 2025 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import datetime
import logging
import time

from odoo import _, api, exceptions, fields, models
from odoo.modules.registry import Registry

_logger = logging.getLogger(__name__)


class ExternalAPILog(models.Model):
    _name = "external.api.log"
    _description = "External API Logs"

    _order = "id desc"

    api_id = fields.Many2one(
        comodel_name="external.api.config",
        string="API Configuration",
        ondelete="cascade",
        required=True,
        readonly=True,
        index=True,
        help="External API configuration used for this call.",
    )
    status = fields.Selection(
        selection=[
            ("success", "Success"),
            ("http_error", "Http Error"),
            ("exception", "Exception"),
        ],
        default="exception",
        required=True,
        readonly=True,
        help="Outcome of the HTTP/SOAP request:"
        "- Penting = Requests pending of execute"
        "- Success = Request executed with correct response"
        "- Http Error = Request executed with an error response"
        "- Exception = Request not executed due to a connection exception",
    )
    status_code = fields.Integer(
        string="HTTP Status Code",
        readonly=True,
        help="Numeric HTTP status returned by the remote server (e.g. 200, 404).",
    )
    response = fields.Text(
        help="Full payload (body) returned by the remote server.",
    )
    datetime = fields.Datetime(
        string="Date",
        default=fields.Datetime.now(),
        required=True,
        readonly=True,
        index=True,
    )
    user_id = fields.Many2one(
        string="Execution User",
        comodel_name="res.users",
        ondelete="restrict",
        readonly=True,
    )
    executed_request = fields.Char(
        readonly=True,
    )
    executed_request_params = fields.Char(
        readonly=True,
    )
    execution_record = fields.Char(
        readonly=True,
    )
    job_id = fields.Many2one(
        comodel_name="queue.job",
        ondelete="set null",
    )

    @api.model
    def log_cleanup_cron(
        self,
        model="external.api.log",
        days_to_keep=30,
        batch_size=1000,
        server_timeout_seconds=300,
        hour_start=0,
        hour_end=6,
        forced_domain=False,
        write_logs=False,
        new_cursor=True,
    ):
        """Deletes the log records.
        It is important to pass a batch_size that can be deleted
            in the server_timeout_seconds
        """
        start = time.monotonic()
        hour = datetime.datetime.now().hour
        env = self.env

        def log(msg, write_logs):
            if write_logs:
                _logger.info(msg)

        def new_env_cursor(env):
            new_cr = Registry(env.cr.dbname).cursor()
            return api.Environment(new_cr, env.uid, env.context)

        def delete_batch(env, model, domain, batch_size, new_cursor):
            if new_cursor:
                env = new_env_cursor(env)
            model = env[model]
            records = model.search(domain, limit=batch_size)
            count = len(records)
            records.unlink()
            if new_cursor:
                env.cr.commit()
                env.cr.close()
            return count

        if not env["ir.model"].search([("model", "=", model)]):
            raise exceptions.UserError(_("The model does not exist"))

        domain = []
        if forced_domain:
            domain = forced_domain
        else:
            domain = [
                (
                    "create_date",
                    "<",
                    datetime.datetime.now() - datetime.timedelta(days=days_to_keep),
                )
            ]

        if (
            hour_start < hour_end
            and hour_start <= hour < hour_end
            or hour_end < hour_start
            and (hour_start <= hour or hour < hour_end)
        ):
            log("Start of log_cleanup_cron", write_logs)
            deleted_number_total = 0
            deleted_number = delete_batch(env, model, domain, batch_size, new_cursor)
            deleted_number_total += deleted_number
            batch_time = time.monotonic() - start
            log(f"batch cleanup time: {batch_time}", write_logs)
            server_timeout_seconds = server_timeout_seconds - batch_time - 60
            while time.monotonic() - start < server_timeout_seconds and deleted_number:
                deleted_number = delete_batch(
                    env, model, domain, batch_size, new_cursor
                )
                deleted_number_total += deleted_number
            log(
                "End of log_cleanup_cron. "
                f"Total time: {time.monotonic() - start} seconds. "
                f"Deleted logs={deleted_number_total} ",
                write_logs,
            )
