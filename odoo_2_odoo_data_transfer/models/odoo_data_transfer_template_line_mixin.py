# Copyright 2025 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import _, api, exceptions, fields, models
from odoo.tools.safe_eval import safe_eval


class OdooDataTransferTemplateLineMixin(models.AbstractModel):
    _name = "odoo.data.transfer.template.line.mixin"
    _description = "Field mappings for a data transfer between Odoos"

    transfer_id = fields.Many2one(
        comodel_name="odoo.data.transfer.template.mixin",
        ondelete="cascade",
    )
    model = fields.Char(related="transfer_id.local_target_model_id.model")
    remote_source_field = fields.Char(
        required=True, help="Field of the remote model that will be transfered"
    )
    local_target_field_id = fields.Many2one(
        string="Local Target Field",
        comodel_name="ir.model.fields",
        required=True,
        ondelete="cascade",
        help="Field of the local model where the data will be created / updated",
    )
    local_target_field_type = fields.Selection(related="local_target_field_id.ttype")

    # FIELDS TO MANAGE RELATIONAL FIELDS TRANSFERENCES:
    migration_type = fields.Selection(
        selection=[
            ("normal", "Normal"),
            ("relational", "Relational"),
            ("one2many", "One2Many"),
        ],
        compute="_compute_migration_type",
    )
    relational_migration_method = fields.Selection(
        selection=[("match_keys", "Match Keys"), ("map_ids", "Map Ids")],
        # TODO: OPTIONAL: Add way to match external ids.
        #  Reuse match_keys logic
        default="match_keys",
    )
    skip_relational_errors = fields.Boolean()
    remote_identifier_field = fields.Char(
        string="Remote Record Identifier Field",
        help="Identifier field to match remote related records with local ones. "
        "For each relared record the field value must be equal",
    )
    local_identifier_field_id = fields.Many2one(
        string="Local Record Identifier Field",
        comodel_name="ir.model.fields",
        ondelete="cascade",
        help="Identifier field to match local related records with remote ones. "
        "For each relared record the field value must be equal",
    )
    related_model = fields.Char(
        compute="_compute_related_model", store=True, readonly=False
    )
    auto_id_mappings = fields.Text(
        default="{}",
        help="Dictionaty with {old_id: new_id,} format for relational record matching. "
        "This has max. priority even using 'match_keys' method",
    )
    manual_id_mappings = fields.Text(
        default="{}",
    )
    id_mappings = fields.Text(compute="_compute_id_mappings")
    one2many_template_id = fields.Many2one(
        string="One2Many Template",
        comodel_name="odoo.data.transfer.template",
        domain=[("is_many2one_template", "=", True)],
    )

    @api.depends("local_target_field_id")
    def _compute_related_model(self):
        for rec in self:
            rec.related_model = rec.local_target_field_id.relation

    @api.depends("local_target_field_type")
    def _compute_migration_type(self):
        for rec in self:
            if rec.local_target_field_type in [
                "many2many",
                "many2one",
                "many2one_reference",
            ]:
                rec.migration_type = "relational"
            elif rec.local_target_field_type == "one2many":
                rec.migration_type = "one2many"
            else:
                rec.migration_type = "normal"

    @api.depends(
        "auto_id_mappings", "manual_id_mappings", "relational_migration_method"
    )
    def _compute_id_mappings(self):
        for rec in self:
            if rec.relational_migration_method == "match_keys":
                id_mappings = safe_eval(rec.auto_id_mappings)
                id_mappings.update(safe_eval(rec.manual_id_mappings))
                rec.id_mappings = str(id_mappings)
            elif rec.relational_migration_method == "map_ids":
                rec.id_mappings = rec.manual_id_mappings

    def _copy_line_vals(self, **def_vals):
        res = []
        for line in self:
            vals = {
                "remote_source_field": line.remote_source_field,
                "local_target_field_id": line.local_target_field_id.id,
                "relational_migration_method": line.relational_migration_method,
                "related_model": line.related_model,
                "skip_relational_errors": line.skip_relational_errors,
                "remote_identifier_field": line.remote_identifier_field,
                "local_identifier_field_id": line.local_identifier_field_id.id,
                "manual_id_mappings": line.manual_id_mappings,
                "one2many_template_id": line.one2many_template_id.id,
            }
            vals.update(def_vals)
            res.append((0, 0, vals))
        return res

    @api.model
    def _parse_many2one_value(self, value):
        """
        value = [remote_id, remote_name]
        ids_map = {remote_id1: new_id1,... remote_idN: new_idN}
        """
        ids_map = safe_eval(self.id_mappings)
        if ids_map.get(value[0]):
            return ids_map[value[0]]
        elif self.skip_relational_errors:
            return False
        else:
            raise exceptions.MissingError(
                _(
                    "Could not find in the local database the remote record "
                    "of model '{model2}' with '{value}' values, "
                    "asociated to the '{model1}' record "
                    "to be imported in the '{field}' field"
                ).format(
                    value=value,
                    field=self.remote_source_field,
                    model1=self.model,
                    model2=self.related_model,
                )
            )

    @api.model
    def _parse_many2many_value(self, value):
        """
        value = [remote_id1..remote_idN]
        ids_map = {remote_id1: new_id1... remote_idN: new_idN}
        """
        ids_map = safe_eval(self.id_mappings)
        res = []
        for remote_id in value:
            if ids_map.get(remote_id):
                res.append((4, ids_map[remote_id]))
            elif self.skip_relational_errors:
                return False
            else:
                raise exceptions.MissingError(
                    _(
                        "Could not find in the local database the remote record "
                        "of model '{model2}' with '{value}' values, "
                        "asociated to the '{model1}' record "
                        "to be imported in the '{field}' field"
                    ).format(
                        value=value,
                        field=self.remote_source_field,
                        model1=self.model,
                        model2=self.related_model,
                    )
                )
        return res

    @api.model
    def _parse_many2one_reference_value(self, value):
        """
        value = remote_id
        ids_map = {remote_id1: new_id1,... remote_idN: new_idN}
        returns: new_id
        """
        ids_map = safe_eval(self.id_mappings)
        if ids_map.get(value):
            return ids_map[value]
        elif self.skip_relational_errors:
            return False
        else:
            raise exceptions.MissingError(
                _(
                    "Could not find in the local database the remote record "
                    "of model '{model2}' with '{value}' values, "
                    "asociated to the '{model1}' record "
                    "to be imported in the '{field}' field"
                ).format(
                    value=value,
                    field=self.remote_source_field,
                    model1=self.model,
                    model2=self.related_model,
                )
            )

    @api.model
    def _parse_one2many_value(self, value):
        """
        value = [{record_data}]
        returns: [(0, 0, {parsed_record_data})]
        """
        res = []
        for rec_data in value:
            parsed_rec_data = self.one2many_template_id._get_new_record_vals(rec_data)
            res.append((0, 0, parsed_rec_data))
        return res

    def _parse_value(self, value):
        if not value:
            return value

        if self.migration_type == "normal":
            return value

        if (
            self.migration_type == "relational"
            and self.local_target_field_type == "many2one"
        ):
            return self._parse_many2one_value(value)

        if (
            self.migration_type == "relational"
            and self.local_target_field_type == "many2many"
        ):
            return self._parse_many2many_value(value)

        if (
            self.migration_type == "relational"
            and self.local_target_field_type == "many2one_reference"
        ):
            return self._parse_many2one_reference_value(value)

        if self.migration_type == "one2many":
            return self._parse_one2many_value(value)

        else:
            raise NotImplementedError(
                "Data transfer template line can not be proccesed. "
                "The parse function is not defined."
            )
