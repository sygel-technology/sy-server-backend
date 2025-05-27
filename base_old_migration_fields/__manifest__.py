# Copyright 2023 Ángel García de la Chica <angel.garcia@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Base Old Migration Fields",
    "summary": "Base Old Migration Fields",
    "version": "15.0.1.0.1",
    "category": "Custom",
    "website": "https://github.com/sygel-technology/sy-server-backend",
    "development_status": "Production/Stable",
    "author": "Sygel, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["base"],
    "data": [
        "security/base_old_migration_fields_security.xml",
    ],
}
