# Copyright 2025 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import datetime
import logging
import traceback

from odoo import _, api, exceptions, fields, models
from odoo.tools.safe_eval import safe_eval

from .odoo_xmlrpc_wrapper import OdooXmlrpcWrapper


@api.model
def _lang_get(self):
    return self.env["res.lang"].get_installed()


class OdooDataTransferWizard(models.TransientModel):
    _name = "odoo.data.transfer.wizard"
    _description = "Generic wizard to transfer data between Odoos"
    _inherit = ["odoo.data.transfer.template.mixin"]

    url = fields.Char(required=True)
    db_name = fields.Char(required=True)
    db_user = fields.Char(required=True, default="admin")
    db_password = fields.Char(required=True)
    template_id = fields.Many2one(
        string="Data transfer template",
        comodel_name="odoo.data.transfer.template",
        required=True,
        domain=[("is_many2one_template", "=", False)],
    )
    record_limit = fields.Integer(
        default=1000,
        help="Maximun number of records to migrate in the transference event",
    )
    record_pack_number = fields.Integer(default=10)
    warn_msg = fields.Char()
    transfer_line_ids = fields.One2many(
        string="Transference Lines",
        comodel_name="odoo.data.transfer.wizard.line",
        inverse_name="transfer_id",
    )
    log_id = fields.Many2one(comodel_name="odoo.data.transfer.log")
    migration_lang = fields.Selection(
        selection=_lang_get,
        string="Language",
        default=lambda self: self.env.lang or "en_US",
        required=True,
        help="Useful when migrating translated fields",
    )
    migrate_archived = fields.Boolean(default=True)
    migrate_failed = fields.Boolean(
        help="Failed records won't be migrated by default for better automating. "
        "Mark this check after fixing the data to migrate failed records"
    )
    state = fields.Selection(
        selection=[("new", "New"), ("validated", "Validated")],
        required=True,
        default="new",
    )

    # remote_identifier_field = fields.Char(
    #     string='Remote Record Identifier Field',
    #     required=True,
    # )
    # local_record_identifier_field = fields.Many2one(
    #     string='Local Target Model',
    #     comodel_name='ir.model',
    #     required=True,
    # )
    # # TODO: OPTIONAL: Required for write mode.

    @api.onchange("template_id")
    def _onchange_template_id(self):
        for rec in self:
            rec.remote_source_model_name = rec.template_id.remote_source_model_name
            rec.local_target_model_id = rec.template_id.local_target_model_id.id

    def _change_template_id(self):
        for rec in self:
            rec.write({"transfer_line_ids": [(5, 0, 0)]})
            rec.write(
                {
                    "remote_source_model_name": (
                        rec.template_id.remote_source_model_name
                    ),
                    "local_target_model_id": rec.template_id.local_target_model_id.id,
                    "domain": rec.template_id.domain,
                    "warn_msg": "",
                    "transfer_line_ids": (
                        rec.template_id.transfer_line_ids._copy_line_vals(
                            **{"transfer_id": rec.id}
                        )
                    ),
                }
            )

    def _autocalculate_id_mappings(self, wrapper, tmpl_line):
        """Calculates a {remote_id:new_id} map for a the
        related remote model of the relational tmpl_line field"""
        res_id_mappings = {}
        ids_grouped_dict = {}
        rem_model = self._get_related_remote_model(wrapper, tmpl_line)
        rem_model_key_name = tmpl_line.remote_identifier_field
        loc_model_key_name = tmpl_line.local_identifier_field_id.name

        # Get key values for local and remote records
        rem_model_recs = wrapper.search_read(
            model=rem_model, domain=[], fields=[rem_model_key_name]
        )
        local_model_recs = self.env[tmpl_line.related_model].search_read(
            [], [loc_model_key_name]
        )
        # Group remote ids by key
        for rem_rec in rem_model_recs:
            ids_grouped_dict[rem_rec[rem_model_key_name]] = [rem_rec["id"], False]
        # Add local ids to agrupation by key
        for local_rec in local_model_recs:
            key = local_rec[loc_model_key_name]
            if key in ids_grouped_dict:
                ids_grouped_dict[key][1] = local_rec["id"]
        # Create final dict, remove initial key
        for ids_list in ids_grouped_dict.values():
            res_id_mappings.update({ids_list[0]: ids_list[1]})
        tmpl_line.write({"auto_id_mappings": str(res_id_mappings)})

    def _validate_transference(self, wrapper):
        self._validate_template(wrapper)
        for tmpl in self.mapped("transfer_line_ids.one2many_template_id"):
            tmpl._validate_template(wrapper)

    def _create_record(self, record_dict):
        new_rec_vals = self._get_new_record_vals(record_dict)
        model = self.env[self.local_target_model_id.model]
        return model.create(new_rec_vals)

    def create_record(self, record_dict):
        """Tries record creation and handles exceptions
        Returns: dict with 'code', 'record', 'id' and 'error' keys
        """
        try:
            with self.env.cr.savepoint():
                record_id = self._create_record(record_dict)
                self.log_id.write(
                    {
                        "transfered_records_ids": [
                            (
                                0,
                                0,
                                {
                                    "remote_id": record_dict["id"],
                                    "local_id": f"{record_id._name},{record_id.id}",
                                },
                            )
                        ]
                    }
                )
        except exceptions.MissingError as e:
            self.log_id.write(
                {
                    "missing_error_record_ids": [
                        (
                            0,
                            0,
                            {
                                "remote_id": record_dict["id"],
                                "error_type": "missing_error",
                                "error_msg": str(e),
                            },
                        )
                    ]
                }
            )
        except Exception as e:
            self.log_id.write(
                {
                    "other_error_record_ids": [
                        (
                            0,
                            0,
                            {
                                "remote_id": record_dict["id"],
                                "error_type": "other_error",
                                "error_msg": str(e),
                            },
                        )
                    ]
                }
            )
            # logging.error(e)
            # logging.error(f"dict_vals: {record_dict}")
            traceback.print_exc()

    def _create_logs(self):
        res = self.env["odoo.data.transfer.log"].create(
            {
                "remote_source_model_name": self.remote_source_model_name,
                "local_target_model_id": self.local_target_model_id.id,
                "domain": self.domain,
                "url": self.url,
                "db_name": self.db_name,
                "date_start": datetime.datetime.now(),
                "transfered_field_ids": (self.transfer_line_ids._copy_line_vals()),
                "is_failed_migration": self.migrate_failed,
            }
        )
        return res

    def action_log(self):
        return {
            "name": _("Transference Log"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "odoo.data.transfer.log",
            "res_id": self.log_id.id,
        }

    def _get_data(self, wrapper, tmpl_line_ids, model, domain, limit=None, offset=0):
        fields = tmpl_line_ids.mapped("remote_source_field")
        data = wrapper.search_read(
            model=model,
            domain=domain,
            fields=fields,
            limit=limit,
            offset=offset,
        )
        # One2many data query:
        for line in tmpl_line_ids.filtered(
            lambda li: (
                li.local_target_field_type == "one2many" and li.one2many_template_id
            )
        ):
            # Get ids
            field = line.remote_source_field
            ids = set()
            for rec_data in data:
                for rec_id in rec_data[field]:
                    ids.add(rec_id)
            # Get data related records
            data2 = self._get_data(
                wrapper,
                line.one2many_template_id.transfer_line_ids,
                line.related_model,
                [("id", "in", list(ids))],
            )
            data2_dic = {rec_data["id"]: rec_data for rec_data in data2}
            # Replace ids with data related records
            for rec_index in range(len(data)):
                data[rec_index][field] = [
                    data2_dic[rec_id] for rec_id in data[rec_index][field]
                ]
        return data

    def action_validate(self):
        wrapper = OdooXmlrpcWrapper(
            self.url,
            self.db_name,
            self.db_user,
            self.db_password,
            self.migration_lang,
            self.migrate_archived,
        )
        self._change_template_id()
        self._validate_transference(wrapper)
        self.warn_msg = "Everything seems valid"
        self.state = "validated"
        return {
            "context": self.env.context,
            "view_mode": "form",
            "res_model": self._name,
            "res_id": self.id,
            "type": "ir.actions.act_window",
            "target": "new",
        }

    def action_accept(self):
        # Create conection
        wrapper = OdooXmlrpcWrapper(
            self.url,
            self.db_name,
            self.db_user,
            self.db_password,
            self.migration_lang,
            self.migrate_archived,
        )
        self = self.with_context(
            **{"lang": self.migration_lang, "active_test": not self.migrate_archived}
        )

        # Validate data
        self._validate_transference(wrapper)

        self.log_id = self._create_logs()

        # Calculate relational fields data mappings
        logging.info("Calculating ID Associations for relational fields")
        for rel_tmpl_line in self._get_relational_lines_to_compute():
            self._autocalculate_id_mappings(wrapper, rel_tmpl_line)
        logging.info("End of calculation of ID Associations for relational fields")

        # Get already transfered records and update domain
        logging.info("Creating transference domain")
        if not self.migrate_failed:
            last_transfered_id = self.env[
                "odoo.data.transfer.log"
            ]._get_last_transfered_record_id(self.local_target_model_id)
            already_transfered_domain = [("id", ">", last_transfered_id)]
            final_domain = already_transfered_domain + safe_eval(self.domain)
        else:
            not_transferred_ids = self.env[
                "odoo.data.transfer.log"
            ]._get_failed_record_ids(self.local_target_model_id)
            not_transferred_domain = [("id", "in", list(not_transferred_ids))]
            final_domain = not_transferred_domain + safe_eval(self.domain)
        logging.info("End of creation of transference domain")
        logging.info(f"Domain: {final_domain}")

        # Loop records packages
        record_counter = 0
        record_total = (
            wrapper.search_count(
                model=self.remote_source_model_name,
                domain=final_domain,
            )
            if self.record_limit <= 0
            else self.record_limit
        )
        while record_counter < record_total:
            # Query data
            records_data = self._get_data(
                wrapper,
                self.transfer_line_ids,
                model=self.remote_source_model_name,
                domain=final_domain,
                limit=min(self.record_pack_number, record_total - record_counter),
                offset=record_counter,
            )
            record_counter += len(records_data)
            if len(records_data) == 0:
                break
            # Loop records
            for record_dict in records_data:
                self.create_record(record_dict)
            logging.info(f"{record_counter} / {record_total} records created")
        self.log_id._calculate_state()
        self.log_id.write(
            {"date_end": datetime.datetime.now(), "record_total_counter": record_total}
        )
        return self.log_id.action_log()
