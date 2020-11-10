# Copyright 2020 Valentin Vinagre <valentin.vinagre@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, api


class MailMail(models.Model):
    _inherit = "mail.mail"

    @api.multi
    def _send(self, auto_commit=False, raise_exception=False, smtp_session=None):
        plain_text = '<div summary="o_mail_notification" style="padding: 0px; font-size: 10px;"><b>CC</b>: %s<hr style="background-color:rgb(204,204,204);border:medium none;clear:both;display:block;font-size:0px;min-height:1px;line-height:0; margin:4px 0 12px 0;"></div>'
        group_portal = self.env.ref('base.group_portal')
        for mail_id in self.ids:
            mail = self.browse(mail_id)
            # if the email has a model, id and it belongs to the portal group
            if mail.model and mail.res_id and group_portal:
                obj = self.env[mail.model].browse(mail.res_id)
                # those partners are obtained, who do not have a user and
                # if they do it must be a portal, we exclude internal
                # users of the system.
                partners = obj.message_follower_ids.mapped('partner_id').filtered(
                    lambda x: not x.user_ids or group_portal in x.user_ids.groups_id
                    )
                if len(partners) > 1:
                    final_cc = None
                    mails = ""
                    # get names and emails
                    for p in partners:
                        mails += "%s &lt;%s&gt;, " % (p.name, p.email)
                    # join texts
                    final_cc = plain_text % (mails[:-2])
                    # it is saved in the body_html field so that it does
                    # not appear in the odoo log
                    mail.body_html = final_cc + mail.body_html
        return super(MailMail, self)._send(auto_commit=auto_commit, raise_exception=raise_exception, smtp_session=smtp_session)
