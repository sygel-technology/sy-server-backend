Improvements proposed:

- Use module queue job or odoo triggers to queue the migration process.
- Add unit tests, for:
    - many2one and many2many field transferences.
    - The migrate_archived option of the wizard.
- Add write mode
- Match records by external id
- Add smartbutton to see a list of migrated records in log