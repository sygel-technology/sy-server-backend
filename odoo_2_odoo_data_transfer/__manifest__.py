# Copyright 2025 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Odoo 2 Odoo Data Transfer",
    "summary": "Generic tools to manage data transfer between Odoos",
    "version": "17.0.1.1.0",
    "category": "Tools",
    "website": "https://github.com/sygel-technology/sy-server-backend",
    "author": "Sygel, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "base",
        "web",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_exports.xml",
        "views/odoo_data_transfer_template_line_mixin_views.xml",
        "views/odoo_data_transfer_log_field.xml",
        "views/odoo_data_transfer_log_record.xml",
        "views/odoo_data_transfer_log.xml",
        "views/odoo_data_transfer_template_line_views.xml",
        "views/odoo_data_transfer_template_views.xml",
        "views/menuitems.xml",
        "wizards/odoo_data_transfer_wizard_line_views.xml",
        "wizards/odoo_data_transfer_wizard_views.xml",
    ],
    "demo": [
        "demo/odoo.data.transfer.template.csv",
        "demo/odoo.data.transfer.template.line.csv",
    ],
}
