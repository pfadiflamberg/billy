import os
import env


class BillyError(Exception):
    """
    General Billy errors that are returned to the client.
    """

    def __init__(self, title, description, details=None, details_type=None, link=None):
        if details is not None and not details_type:
            raise "Define details type!"
        self.title = title
        self.description = description
        self.details = details
        self.details_type = details_type
        self.link = link

    def asJSON(self):
        json = {
            'title': self.title,
            'description': self.description
        }
        if self.details:
            json['details'] = self.details
            json['details_type'] = self.details_type
        if self.link:
            json['link'] = self.link
        return json

        def __str__(self):
            return "BillyError: " + self.asJSON()


class InvoiceListError(BillyError):

    def __init__(self, title, description, invoices):
        super().__init__(title, description, details=invoices, details_type='INVOICE_NAME')


class InvalidMailingListURL(BillyError):

    def __init__(self, mailing_list_url):
        super().__init__("Mailing List URL Invalid",
                         "The provided mailing list {mailing_list} is not valid.".format(mailing_list=mailing_list_url), link=mailing_list_url)


class MailingListHasNoRecipients(BillyError):

    def __init__(self, mailing_list_url):
        super().__init__("Mailing List has no recipients",
                         "The provided mailing list {mailing_list} has no recipients.".format(mailing_list=mailing_list_url), link=mailing_list_url)


def recipientLink(id):
    return os.path.join(env.HITOBITO_HOST, env.HITOBITO_LANG, 'people', id)


class RecipientRequiresEmail(BillyError):

    def __init__(self, id):
        super().__init__("Recipient requires Email", "Recipient {id} requires an email address envabled for shippment.".format(
            id=id), link=recipientLink(id))


class RecipientAddressError(BillyError):

    def __init__(self, id):
        super().__init__("Recipient Address Error",
                         "Recipient {id} has an incomplete address.".format(id=id), link=recipientLink(id))


class MultipleErrors(BillyError):

    def __init__(self, errors: BillyError):
        details = []
        for e in errors:
            details.append(e.asJSON())
        super().__init__("Multiple Erros", "Multiple issues encountered:",
                         details=details, details_type='ERROR')


class InvoiceNotIssued(BillyError):

    def __init__(self, bulk):
        super().__init__("Invoice not active",
                         "The invoice needs to be in the issued state for this operation.")


class CannotCloseBulk(BillyError):

    def __init__(self, invoices):
        super().__init__("Cannot close bulk",
                         "There are still pending invoices in this bulk.",
                         details=invoices, details_type='INVOICE_NAME')
