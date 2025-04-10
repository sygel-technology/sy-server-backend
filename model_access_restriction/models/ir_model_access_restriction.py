# Copyright 2025 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models


class IrModelAccessRestriction(models.Model):
    _name = "ir.model.access.restriction"
    _description = "Model Access Restrictions. Not having one will disable access."

    _order = "model_id,name,id"

    name = fields.Char(index=True)
    active = fields.Boolean(
        default=True,
    )
    model_id = fields.Many2one(
        string="Model",
        comodel_name="ir.model",
        index=True,
        required=True,
        ondelete="cascade",
        domain=lambda self: [
            (
                "id",
                "!=",
                self.env.ref(
                    "model_access_restriction.model_ir_model_access_restriction"
                ).id,
            )
        ],
    )
    groups = fields.Many2many(
        string="Allowed Groups",
        comodel_name="res.groups",
        relation="model_access_restriction_group_rel",
        column1="model_access_restriction_id",
        column2="group_id",
        ondelete="restrict",
    )
    # Commented for doint it in a possible module improvement
    # perm_read = fields.Boolean(string='Apply for Read', default=True)
    # perm_write = fields.Boolean(string='Apply for Write', default=True)
    perm_create = fields.Boolean(string="Apply for Create", default=True)
    perm_unlink = fields.Boolean(string="Apply for Delete", default=True)

    def init(self):
        self.env.cr.execute(
            """
            CREATE INDEX IF NOT EXISTS ir_model_access_restriction_model_name_id_idx
            ON ir_model_access_restriction(model_id,name,id)
        """
        )

    def _get_model_restrictions(self, model, operation):
        self._cr.execute(
            """ SELECT r.id
                FROM ir_model_access_restriction r JOIN ir_model m ON (r.model_id=m.id)
                WHERE m.model=%s AND r.active AND r.perm_{operation}
                ORDER BY r.id
            """.format(
                operation=operation
            ),
            (model,),
        )
        return self.browse(row[0] for row in self._cr.fetchall()).exists()

    def _get_passed_restrictions(self, model, operation):
        self._cr.execute(
            """ SELECT r.id
                FROM ir_model_access_restriction r
                    JOIN ir_model m ON (r.model_id=m.id)
                WHERE m.model=%s AND r.active AND r.perm_{operation}
                AND (r.id IN (
                    SELECT model_access_restriction_id
                    FROM model_access_restriction_group_rel rg
                    JOIN res_groups_users_rel gu ON (rg.group_id=gu.gid)
                    WHERE gu.uid=%s)
                )
                ORDER BY r.id
            """.format(
                operation=operation
            ),
            (model, self._uid),
        )
        return self.browse(row[0] for row in self._cr.fetchall()).exists()

    def check_restrictions(self, model, operation):
        res = False
        if operation not in ["create", "unlink"]:
            res = True
        else:
            model_restrictions = self._get_model_restrictions(model, operation)
            res = not model_restrictions or not (
                model_restrictions - self._get_passed_restrictions(model, operation)
            )
        return res

    @api.constrains("groups")
    def _check_groups(self):
        if self.filtered(lambda r: not r.groups):
            raise exceptions.ValidationError(
                _("Restrictions must have at least one allowed group")
            )
