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
