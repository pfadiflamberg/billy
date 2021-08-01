import os
import pdfkit
import locale

from qrbill.bill import QRBill

# TODO: this should be in app.py or something
locale.setlocale(locale.LC_TIME, "de_CH.UTF-8")

TMP_SVG_FILE = 'bill.svg'
INVOICE_TEMPLATE = 'resources/html/invoice.html'
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def formatSenderAddress(address):
    DELIMINATER_POSITION = 1
    lines = address.split('\n')
    return ', '.join(lines[:DELIMINATER_POSITION]) + '<br>' + ', '.join(lines[DELIMINATER_POSITION:])


def invoicePDF(title, text_body, account, creditor, hitobito_debtor, hitobito_sender, ref, date, due_date, amount=None):

    template_file = open(INVOICE_TEMPLATE)
    invoice = template_file.read()

    # fix relative links (note: we expect all link to have a ../.. prefix)
    invoice = invoice.replace('../..', BASE_PATH)

    invoice = invoice.replace('{{ header }}', '<br>'.join(
        ['Pfadfinderkorps Flamberg, Kasse und Versicherung',
         ', '.join(
             [hitobito_sender['name']
              + ' / {nickname}'.format(
                  nickname=hitobito_sender['nickname']) if hitobito_sender['nickname'] else '',
              hitobito_sender['addr']['street'],
              ' '.join([hitobito_sender['addr']['zip'], hitobito_sender['addr']['town']])]),
         'cassa@flamberg.ch, www.flamberg.ch']))
    invoice = invoice.replace('{{ sender_address }}', ', '.join(
        [hitobito_sender['name'],
         hitobito_sender['addr']['street'],
         ' '.join([hitobito_sender['addr']['zip'], hitobito_sender['addr']['town']])]))
    invoice = invoice.replace('{{ recipient_address }}', '<br>'.join([
        hitobito_debtor['name']
        + (' / {nickname}'.format(
            nickname=hitobito_debtor['nickname']) if hitobito_debtor['nickname'] else ''),
        hitobito_debtor['addr']['street'],
        ' '.join([hitobito_debtor['addr']['zip'],
                 hitobito_debtor['addr']['town']])
    ]))
    invoice = invoice.replace('{{ info }}', '{place}, {date}'.format(
        place=hitobito_sender['addr']['town'],
        date=date.strftime('%d. %B %Y'),
    ))
    invoice = invoice.replace('{{ title }}', title)
    invoice = invoice.replace(
        '{{ text }}', text_body
        .replace('\n\n', '<span class="nl2"></span>')
        .replace('\n', '<span class="nl"></span>'))

    # generate qr bill as svg
    bill = QRBill(
        account=account,
        creditor=creditor,
        amount=amount,
        language='de',
        ref_number=ref,
        due_date=due_date.strftime("%Y-%m-%d"),
        debtor={
            'name': hitobito_debtor['name'],
            'street': hitobito_debtor['addr']['street'],
            'pcode': hitobito_debtor['addr']['zip'],
            'city': hitobito_debtor['addr']['town'],
        }
    )
    bill.as_svg(TMP_SVG_FILE, full_page=True)

    return pdfkit.from_string(invoice, False, options={
        'page-size': 'A4',
        'margin-left': '0',
        'margin-right': '0',
        'margin-top': '0',
        'margin-bottom': '0',
        'zoom': '1.329',
        'disable-smart-shrinking': None,
        'enable-local-file-access': None,
    })
