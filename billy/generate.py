from qrbill.bill import QRBill, A4, mm
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF

import svgwrite
import qrbill
import re

TMP_SVG_FILE = 'tmp.svg'


def add_multiline_text(dwg, text, insert=(0, 0), font_size='14px', font_family=None):
    """
    As we require the svg profile 'full' and this does not support text areas,
    we have this helper method. It creates a new line it it encounters a \n symbol.
    """
    for n, line in enumerate(text.split('\n')):
        dwg.add(dwg.text(
            line,
            insert=(insert[0], insert[1] + n * 1.2 * int(font_size[:-2])),
            font_size=font_size,
            font_family=font_family,
        ))


def bill(account, creditor, hitobito_debtor, hitobito_back, ref, amount):
    """
    Generate returnes the PDF of a bill.
    """
    # generate qr bill
    bill = QRBill(
        account=account,
        creditor=creditor,
        amount=amount,
        language='de',
        ref_number=ref,
    )
    # create svg file with qr bill
    dwg = svgwrite.Drawing(
        size=A4,
        viewBox=('0 0 %f %f' % (mm(A4[0]), mm(A4[1]))),
    )
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill='white'))
    bill.transform_to_full_page(dwg, bill.draw_bill(dwg))
    # add address field
    xr = 30
    xl = 460
    y = 200
    d = 1
    l = hitobito_back['addr'].split('\n')
    dwg.add(dwg.text(
        ', '.join(l[:d]),
        insert=(xl, y)
    ))
    dwg.add(dwg.text(
        ', '.join(l[d:]),
        insert=(xl, y+15)
    ))
    dwg.add(dwg.image(
        href='resources/images/pp.png',
        insert=(xl, y + 20),
        size=(234, 65),
    ))
    add_multiline_text(dwg, hitobito_debtor['addr'],
                       insert=(xl, y+65),
                       font_size='16px',
                       font_family="helvetica"
                       )
    dwg.add(dwg.image(
        href='resources/images/logo.png',
        insert=(550, 40),
        size=(150, 60),
    ))
    add_multiline_text(dwg,
                       '\n'.join([
                           'Pfadfinderkorps Flamberg, Kasse und Versicherung',
                           hitobito_back['addr'].replace('\n', ', '),
                           'cassa@flamberg.ch, www.flamberg.ch',
                       ]),
                       insert=(xr, 50),
                       font_size='10px',
                       font_family='14px',
                       )
    # add title
    dwg.add(dwg.text(
        'Jahresrechnung',
        font_size='18px',
        insert=(xr, 300)
    ))
    add_multiline_text(dwg,
                       """
        Jedes Jahr erhalten alle Stufen, jeder Harst und Zug einen Beitrag aus der Korpskasse, um Anschaffungen
        von Material und andere Ausgaben zu finanzieren. Ihr Sohn ist während den Übungen und Lagern, sowie bei
        der Hin- und Rückfahrt zu Pfadianlässen subsidiär gegen Unfall versichert. Für die Pfadileiter besteht
        zudem eine Haftpflichtversicherung. Um diese Kosten decken zu können, sind wir auf den Jahresbeitrag je-
        des einzelnen Flambergers angewiesen.
        Leider mussten wir feststellen, dass der Jahresbeitrag von Leandro für das Jahr 2019 noch nicht bezahlt
         wurde. Wir bitten Sie, den Jahresbeitrag von CHF 50.00 in den nächsten 10 Tagen auf unser Bankkonto
         einzuzahlen. Bitte benützen Sie dazu ausschliesslich den untenstehenden Einzahlungsschein (mehrere
         Jahresbeiträge bitte jeweils separat). Beim eBanking bitten wir Sie, die Referenznummer unbedingt
         aufzuführen. Sie erleichtern uns damit die Arbeit wesentlich. Besonders dankbar sind wir denjenigen,
         die den Betrag grosszügig aufrunden.
        Sollte Ihr Sohn nicht mehr Mitglied unseres Korps sein und diesen Brief irrtümlicherweise erhalten
        haben, so bitten wir Sie höflich, dies dem Korpskassier (Adresse siehe oben) schriftlich oder per Email
        mitzuteilen.
        Wir danken Ihnen herzlich für das uns entgegengebrachte Vertrauen und wünschen Ihrem Sohn ein ausgefülltes,
        """,
                       insert=(xr, 350),
                       font_family='14px',
                       )
    dwg.saveas(TMP_SVG_FILE)
    # convert svg to pdf
    drawing = svg2rlg(TMP_SVG_FILE)
    renderPDF.drawToFile(drawing, "tmp.pdf")
    # return renderPDF.drawToString(drawing)
