# Copyright 2020 Valentin Vinagre <valentin.vinagre@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Reports Font Size",
    "summary": "This module change the font size base of reports.",
    "version": "13.0.1.0.0",
    "category": "Reports",
    "website": "https://www.sygel.es",
    "author": "Sygel",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        'web',
    ],
    'data': [
        'views/reports_font_size.xml',
    ],
}
