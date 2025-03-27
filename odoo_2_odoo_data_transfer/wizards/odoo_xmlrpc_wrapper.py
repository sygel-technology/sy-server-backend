import xmlrpc

from odoo import _, exceptions
from odoo.tools.safe_eval import safe_eval


class OdooXmlrpcWrapper:
    common_conn = None
    models_conn = None
    url = None
    db = None
    username = None
    password = None
    uid = None

    def __init__(self, url, db, username, password, lang, archived):
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        self.common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
        self.models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
        self.lang = lang
        self.archived = archived
        try:
            self.uid = self.common.authenticate(db, username, password, {})
        except xmlrpc.client.ProtocolError as e:
            raise exceptions.ValidationError(
                _("Error creating conection with remote Odoo. Bad URL:\n")
            ) from e
        except xmlrpc.client.Fault as e:
            raise exceptions.ValidationError(
                _("Error creating conection with remote Odoo. Bad Database\n")
            ) from e
        if not self.uid:
            raise exceptions.ValidationError(
                _(
                    "Error creating conection with remote Odoo. "
                    "Bad Username or Password\n"
                )
            )

    def search_read(self, model, domain, fields, limit=None, offset=0):
        if isinstance(domain, str):
            domain = safe_eval(domain)
        kwargs = {
            "order": "id",
            "fields": fields,
            "offset": offset,
            "context": {"lang": self.lang, "active_test": not self.archived},
        }
        if limit:
            kwargs["limit"] = limit

        return self.models.execute_kw(
            self.db, self.uid, self.password, model, "search_read", [domain], kwargs
        )

    def search_count(self, model, domain):
        if isinstance(domain, str):
            domain = safe_eval(domain)
        kwargs = {
            "context": {"lang": self.lang, "active_test": not self.archived},
        }
        return self.models.execute_kw(
            self.db, self.uid, self.password, model, "search_count", [domain], kwargs
        )

    def fields_get(self, model, fields):
        kwargs = {
            "context": {"lang": self.lang, "active_test": not self.archived},
        }
        return self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            model,
            "fields_get",
            [fields],
            kwargs,
        )
