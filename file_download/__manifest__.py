# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# Copyright (c) 2020 Sygel (http://www.sygel.es)

{
    "name": "File download",
    "version": "17.0.1.0.0",
    "sequence": 14,
    "summary": "Download file",
    "author": "Sygel",
    "license": "AGPL-3",
    "website": "https://github.com/sygel-technology/sy-server-backend",
    "category": "report",
    "external_dependencies": {
        "python": ["odoo_test_helper"],
    },
    "depends": [
        "base",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/download_file_view.xml",
    ],
    "installable": True,
    "application": False,
}
