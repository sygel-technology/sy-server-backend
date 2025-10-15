# Copyright 2025 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Base External API",
    "summary": "Tools to manage external api connections.",
    "version": "17.0.1.2.0",
    "website": "https://github.com/sygel-technology/sy-server-backend",
    "author": "Sygel, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "queue_job",
    ],
    "external_dependencies": {"python": ["requests"]},
    "data": [
        "security/ir.model.access.csv",
        "views/external_api_config_views.xml",
        "views/external_api_log_views.xml",
        "views/external_api_menus.xml",
    ],
    "demo": ["demo/external_api_config.xml"],
}
