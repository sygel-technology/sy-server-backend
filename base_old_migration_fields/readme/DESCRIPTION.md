This module helps during data migrations between Odoo versions or from other systems by allowing you to keep the original IDs from the old database. These IDs can be useful later to match or update records.

The module creates a group called Old Migration Fields Manager. Only users in this group can see or edit the "old ID" fields that are added by other modules like:

* partner_contact_old_migration_fields
* product_old_migration_fields

This module by itself doesn’t add any fields — it just provides the access control.
