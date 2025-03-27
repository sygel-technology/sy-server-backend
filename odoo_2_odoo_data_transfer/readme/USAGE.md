To use this module, you need to create transference templates, and then execute the transference wizard.

## Create transfer templates

1. Go to Settings / Odoo Data Transfer / Odoo Data Transfer Templates. Create a new template

2. Fill the transferred model data in the "Remote Source Model", "Local Target Model", and "Domain" fields. In the local model, you will see a list of all the model names, while in the remote model you will have to type the model name.

3. Fill the transfer template lines. The information is detailed in the following section

Note: You have "helps" in the data transfer template fields to explain what are they used for. To see them point the cursor at the field name.


#### Transfer template lines
The transfer template lines, also shown as "field mappings", are used to indicate which fields of the model are going to be transferred. 

For each line you will have to fill the "Remote Source Field" and "Local Target Field" fields. The first one indicates a field of the remote model that will be transferred, and the second one indicates the field of the local model the first field will be transferred to. You should make sure both fields have similar types. 

If the field types are relational (many2one, many2many, one2many) the transference will be more complex and you will have to fill more data:


-  If the fields are many2one or many2many, for example: a contact, Odoo will need to associate the remote contact with the local one. For that you will have to choose a Transference method. Note: Creating records is not currently supported, the remote related record has to be created in the local odoo

    - "Map ids" is the simplest method, you have to do the associations filling a python dictionary with two keys for each related record, old_id and new_id. For example, if you have the "Pedrito" partner in the remote Odoo with id 6, but his id in the local odoo is 10, the map will be {6:10,}. 

    - "Match keys" is the default method. You have to fill a identifier field for the remote and local model, then odoo will automatically make the associations. In the partner example, you can have the "Vat" field as the identifier for both fields, "Pedrito" should have the same vat in both Odoos and Odoo will identify them as the same contact for having the same identifier field. The map of ids will also be available to manually override the associations if some related records do not have the same value in the key field.

-  If the related field has one2many type, there is usually a strong dependency between the fields, and in this case we have to create the records of the related model at the same time. For example, if you are transferring posted invoices, you will have to transfer its invoice lines at the same time. In order to do that, you have to fill the "One2Many Template" field with another data transfer template for the related model, that second transfer template should have the "Is Many2One Template" boolean field set as true.


#### Import / export data transfer templates

You can use the default odoo import tool to import / export data transfer templates.

To export a template, you should:
1. Go to Settings / Odoo Data Transfer / Odoo Data Transfer Templates
2. Select the desired templates to export
3. Click on action / export
4. Select the "Official Export / Import Format" export template
5. Click on the "I want to update data" check
6. Click on export

The generated file can be imported as usual. 

Some predefined templates have been placed under the "templates" folder of this module as examples and for being reused.

## Execute the transfer wizard

1. Go to Settings / Odoo Data Transfer / Odoo Data Transfer Wizard.
2. Fill the information of the remote audio to make the connection: "Url", "DB Name", "DB User" and "DB Password"
3. Choose the data transfer template with the predefined data to transfer.
4. Click the "Validate" button. If the models and fields of the template have incompatibilities an error will be shown.
5. The template models and fields will appear, review them. You can edit them without affecting the template.
6. You can also edit other options of the Transference like the record limit, Transference language, or an option to include archived fields in the transference.
7. Click the "Accept" button to start the Transference process. When finalized, the Transference will show a log with the transferred records, and records that could not be transferred for some error. A error on the migration of a record won't block the migration of the other records.


#### After Transference

After a Transference process, you should review the Transference errors on the Transference log, fix the data, and repeat the migration process.

On every failed record, the remote id and the error message are shown. We have 2 types of errors:
- Missing Errors: Records that could not be migrated because another related record could not be found locally. For example, if we are migrating a sale order of our customer "Pedro", and "Pedro" could not be found locally, this error will be generated. To have the missing error you have some common options.
    - If the record does not exist you can create it.
    - If the record does exist but the key has changed, you can edit it to be the same 
    - If the record does exist but the key has changed, you can add the remote id and the local id to the id mappings of the template.
    - If fixing the data is too difficult or expensive, you can skip the errors with the "Skip Relational Errors" of the migration template line. If a related field is not found, it will be set to false instead of throwing an error.

- Other errors: The rest of the errors. Less common but more difficult to resolve, they will probably need a developer.

If you execute again the same Transference template, the last transfered record will be queried in the logs, the next migration process will start from that record. 

You can repeat the execution of the migration process until there are no errors in the migration log.

The failed records won't be included in the next migration process if they are before that last migrated record, if you have fixed the problems and you want to include again the failed records in the migration, you should mark the "Migrate Failed" check of the migration wizard, then it will only try to migrate those failed records.
