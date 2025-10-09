# Copyright 2025 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


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
