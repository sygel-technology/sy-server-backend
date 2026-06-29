To use this module, you need to create a new module with:

1. A data file that creates an External API Config with an external ID.
2. A python file with code that gets the External API Config and uses it to make an external call with the call() or queued_call() methods.


Some use cases of this module would be sending every new res partner record to, or sending every update in the price of the products, to a remote API.


The code of the first example would look like this:

```
<odoo noupdate="1">

    <record id="your_external_api_external_id" model="external.api.config">
        <field name="name">Your API Name</field>
        <field name="base_url">https://www.test.com</field>
    </record>

</odoo>
```
```
class ResPartner(models.Model):

    _inherit = "res.partner"

    def create(self, vals):
        recs = super().write(vals)
        if SYNCED_FIELDS.intersection(vals):
            for rec in recs:
                partner_json = rec.json()  # Custom function to complete
                self.env.ref(
                    'your_module.your_external_api_external_id'
                ).queued_call(
                    method="post",
                    url="/partner/create",
                    data=partner_json
                )
        return res
```


To configure the schedule action that deletes logs you need to:

1. Go to Settings / Technical /  Scheduled Actions
2. Go to the 'External Api Logs Cleanup' scheduled action
3. You can edit the execution interval or the function params
4. You can manually test the scheduled action.
5. You can manually edit the parameters of the scheduled action's function to customize the behaviour. Important fields:
    - server_timeout_seconds: Max time for the scheduled action. If you have edited your server's timeout_seconds, you'll have to manually edit this field
    - batch_size: Number of records to delete at the same time. Take into account, that this value should be low enough to delete at least one batch in the server_timeout_seconds
    - model: you can edit the model parameter to delete other sytem logs
    - write_logs: If you set this to True, logs will be printed showing the number of deleted logs
