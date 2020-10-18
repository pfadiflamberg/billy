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


def bill(text_body, account, creditor, hitobito_debtor, hitobito_sender, ref, amount):
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
    # Address block
    # Return address, splitted over two lines
    l = hitobito_sender['addr'].split('\n')
    send_back_addr_delimiter = 1
    dwg.add(dwg.text(
        ', '.join(l[:send_back_addr_delimiter]),
        insert=(xl, y)
    ))
    dwg.add(dwg.text(
        ', '.join(l[send_back_addr_delimiter:]),
        insert=(xl, y+15)
    ))
    # PP image by Swiss Post
    dwg.add(dwg.image(
        href='resources/images/pp.png',
        insert=(xl, y + 20),
        size=(234, 65),
    ))
    # recipient address
    add_multiline_text(dwg, hitobito_debtor['addr'],
                       insert=(xl, y+65),
                       font_size='16px',
                       font_family="helvetica"
                       )
    # header
    # header text
    add_multiline_text(dwg,
                       '\n'.join([
                           'Pfadfinderkorps Flamberg, Kasse und Versicherung',
                           hitobito_sender['addr'].replace('\n', ', '),
                           'cassa@flamberg.ch, www.flamberg.ch',
                       ]),
                       insert=(xr, 50),
                       font_size='10px',
                       font_family='helvetica',
                       )
    # Logo
    dwg.add(dwg.image(
        href='resources/images/logo.png',
        insert=(550, 40),
        size=(150, 60),
    ))
    # add title
    dwg.add(dwg.text(
        'Jahresrechnung',
        font_size='18px',
        insert=(xr, 300)
    ))
    add_multiline_text(dwg, text_body,
                       insert=(xr, 350),
                       font_size='14px',
                       )
    dwg.saveas(TMP_SVG_FILE)
    # convert svg to pdf
    return svg2rlg(TMP_SVG_FILE)


def billAsFile(drawing, file):
    renderPDF.drawToFile(drawing, file)


def billAsString(drawing):
    return renderPDF.drawToString(drawing)
