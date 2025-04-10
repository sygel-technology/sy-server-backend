# Copyright 2025 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestModelAccessRestriction(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.model = cls.env.ref("base.model_res_partner")
        cls.group = cls.env["res.groups"].create(
            {
                "name": "Test Group",
            }
        )
        cls.restriction = cls.env["ir.model.access.restriction"].create(
            {
                "name": "Test Restriction",
                "model_id": cls.model.id,
                "perm_create": True,
                "perm_unlink": True,
                "groups": [(4, cls.group.id)],
            }
        )

    def test_one_restriction(self):
        self.assertFalse(self.env["res.partner"].check_access_rights("create"))

    def test_one_restriction_passed(self):
        self.group.write({"users": [(4, self.env.uid)]})
        self.assertTrue(self.env["res.partner"].check_access_rights("create"))

    def test_no_restriction(self):
        self.restriction.unlink()
        self.assertTrue(self.env["res.partner"].check_access_rights("create"))

    def test_two_restrictions(self):
        self.restriction2 = self.env["ir.model.access.restriction"].create(
            {
                "name": "Test Restriction 2",
                "model_id": self.model.id,
                "perm_create": True,
                "perm_unlink": True,
                "groups": [(4, self.env.ref("base.group_user").id)],
            }
        )
        self.assertFalse(self.env["res.partner"].check_access_rights("create"))
