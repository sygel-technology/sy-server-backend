# Copyright 2025 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import _, exceptions, fields, models


class OdooDataTransferTemplateLineMixin(models.AbstractModel):
    _name = "odoo.data.transfer.template.mixin"
    _description = "Basic Fields for a data transfer between Odoos"

    domain = fields.Char(
        default="[]",
        help="Determines the records of the remote Odoo that will be migrated",
    )
    local_target_model_id = fields.Many2one(
        string="Local Target Model",
        comodel_name="ir.model",
        required=True,
        ondelete="cascade",
        help="Model of the current Odoo where the records will be created / updated",
    )
    remote_source_model_name = fields.Char(
        string="Remote Source Model",
        required=True,
        help="Model of the remote Odoo whose records will be transfered",
    )
    transfer_line_ids = fields.One2many(
        string="Transfer Lines",
        comodel_name="odoo.data.transfer.template.line.mixin",
        inverse_name="transfer_id",
        help="Fields that will be transfered",
    )

    def _get_template_line(self, key):
        return self.transfer_line_ids.filtered(
            lambda li: li.remote_source_field == key
        )[:1]

    def _get_relational_lines_to_compute(self):
        res = [
            line
            for line in self.transfer_line_ids.filtered(
                lambda li: (
                    li.migration_type == "relational"
                    and li.relational_migration_method == "match_keys"
                )
            )
        ]
        one2many_templates = self.mapped("transfer_line_ids.one2many_template_id")
        if one2many_templates:
            res += [
                line for line in one2many_templates._get_relational_lines_to_compute()
            ]
        return res

    def _parse_key(self, key):
        return self._get_template_line(key).local_target_field_id.name

    def _parse_value(self, key, value):
        tmpl_line = self._get_template_line(key)
        return tmpl_line._parse_value(value)

    def _get_new_record_vals(self, record_dict):
        """Returns vals of a new record given the template and the old values
        Inherit this function to add new custom values."""
        new_rec_vals = {}
        # Loop fields
        for key, value in record_dict.items():
            if not self._get_template_line(key):
                continue
            new_rec_vals.update({self._parse_key(key): self._parse_value(key, value)})
        return new_rec_vals

    def _equivalent_types(self, type1, type2):
        """Returns if type2 can be created from in type1 without data conversions"""
        if type2 == "boolean":
            return True
        equivalences = {
            "boolean": ("integer"),  # Bool
            "char": ("text"),  # Str
            "binary": ("text"),  # Str
            "html": ("text", "char"),  # Str
            "text": ("char"),  # Str
            "selection": (),  # Str
            "date": ("datetime"),  # Str (especial)
            "datetime": ("date"),  # Str (especial)
            "integer": ("float", "monetary", "many2one_reference"),  # Int
            "float": ("monetary", "integer"),  # Float
            "monetary": ("float", "integer"),  # Float
            "many2many": (),  # [int1...intN]
            "many2one": (),  # (int, name)
            "one2many": (),  # [int1...intN]
            "many2one_reference": ("integer"),  # Int
            "reference": (),
            "json": (),  # Dict
        }
        return type1 in equivalences.get(type2, []) or type1 == type2

    def _get_related_remote_model(self, wrapper, tmpl_line):
        """Returns the related remote model of the relational tmpl_line field"""
        use_same_model = tmpl_line.local_target_field_type == "many2one_reference"
        if use_same_model:
            return tmpl_line.related_model
        rem_field = tmpl_line.remote_source_field
        return wrapper.fields_get(
            tmpl_line.transfer_id.remote_source_model_name, [rem_field]
        )[rem_field]["relation"]

    def _validate_template(self, wrapper):
        # Validate model
        model = self.remote_source_model_name
        if not wrapper.search_read("ir.model", [("model", "=", model)], ["id"]):
            raise exceptions.ValidationError(
                _("The '{}' model does not exist in the remote Odoo").format(model)
            )

        # Validate fields
        tmpl_line_ids = self.transfer_line_ids
        fields_data = wrapper.fields_get(
            model, tmpl_line_ids.mapped("remote_source_field")
        )
        error = ""
        for line in tmpl_line_ids:
            error += self._validate_remote_field(line, fields_data)
        if error:
            raise exceptions.ValidationError(
                _("Error validating remote {} model's fields:\n\n").format(model)
                + error
            )

        # Validate remote relational fields keys
        for line in self._get_relational_lines_to_compute():
            remote_model = self._get_related_remote_model(wrapper, line)
            field_data = wrapper.fields_get(remote_model, line.remote_identifier_field)
            error = self._validate_remote_field(
                line, field_data, relational_key_mode=True
            )
            if error:
                raise exceptions.ValidationError(
                    _(
                        "Error validating key matching fields of related "
                        "remote '{rmodel}' model "
                        "through '{rfield}' related field.\n\n"
                    ).format(rmodel=remote_model, rfield=line.remote_source_field)
                    + error
                )

    def _validate_remote_field(
        self, tmpl_line_id, fields_data, relational_key_mode=False
    ):
        """Returns if the remote specified field in tmpl_line_id
        is compatible with local field.
        The relational_key_mode changes the tmpl_line_id fields to validate.
        """
        rem_field_ref = (
            "remote_identifier_field" if relational_key_mode else "remote_source_field"
        )
        local_field_ref = (
            "local_identifier_field_id"
            if relational_key_mode
            else "local_target_field_id"
        )

        field_name = tmpl_line_id[rem_field_ref]
        error = ""
        if field_name not in fields_data:
            error += _("Field not found in remote Odoo: '{}'\n\n").format(field_name)
            return error

        field_type = fields_data[field_name]["type"]
        local_field_type = tmpl_line_id[local_field_ref].ttype
        local_field_name = tmpl_line_id[local_field_ref].name
        if not self._equivalent_types(field_type, local_field_type):
            error += _(
                "Type incompatibility with remote Odoo field: "
                "'{fname} ({ftype})', "
                "and local field: "
                "'{lfname} ({lftype})'\n\n"
            ).format(
                fname=field_name,
                ftype=field_type,
                lfname=local_field_name,
                lftype=local_field_type,
            )
        return error
