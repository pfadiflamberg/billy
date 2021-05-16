from qrbill.bill import QRBill, A4, mm
import os
import svgwrite
import cairosvg
import pdfkit

TMP_SVG_FILE = 'tmp.svg'
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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


def bill(title, text_body, account, creditor, hitobito_debtor, hitobito_sender, ref, amount=None):
    """
    Generate returns the PDF of a bill.
    """

    # generate qr bill as svg
    bill = QRBill(
        account=account,
        creditor=creditor,
        amount=amount,
        language='de',
        ref_number=ref,
    )
    bill.as_svg('bill.svg', full_page=True)

    pdfkit.from_file('resources/html/invoice.html', 'tmp.pdf', options={
        'page-size': 'A4',
        'margin-left': '0',
        'margin-right': '0',
        'margin-top': '0',
        'margin-bottom': '0',
        'zoom': '1.329',
        'disable-smart-shrinking': None,
        'enable-local-file-access': None,
    })





    # # create svg file with qr bill
    # dwg = svgwrite.Drawing(
    #     size=A4,
    #     viewBox=('0 0 %f %f' % (mm(A4[0]), mm(A4[1]))),
    # )
    # dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill='white'))
    # bill.transform_to_full_page(dwg, bill.draw_bill(dwg))
    # # add address field
    # xr = 30
    # window_left = 400
    # window_top = 200
    # # Address block
    # # Return address, splitted over two lines
    # l = hitobito_sender['addr'].split('\n')
    # send_back_addr_delimiter = 1
    # dwg.add(dwg.text(
    #     ', '.join(l[:send_back_addr_delimiter]),
    #     insert=(window_left, window_top),
    #     font_size='10px'
    # ))
    # dwg.add(dwg.text(
    #     ', '.join(l[send_back_addr_delimiter:]),
    #     insert=(window_left, window_top+14),
    #     font_size='10px'
    # ))
    # # PP image by Swiss Post
    # dwg.add(dwg.image(
    #     href=BASE_PATH + '/resources/images/pp.png',
    #     insert=(window_left, window_top + 18),
    #     size=(187, 52),
    # ))
    # # recipient address
    # add_multiline_text(dwg, hitobito_debtor['addr'],
    #                    insert=(window_left, window_top+60),
    #                    font_size='14px',
    #                    font_family="helvetica"
    #                    )
    # # header
    # # header text
    # add_multiline_text(dwg,
    #                    '\n'.join([
    #                        'Pfadfinderkorps Flamberg, Kasse und Versicherung',
    #                        hitobito_sender['addr'].replace('\n', ', '),
    #                        'cassa@flamberg.ch, www.flamberg.ch',
    #                    ]),
    #                    insert=(xr, 50),
    #                    font_size='10px',
    #                    font_family='helvetica',
    #                    )
    # # Logo
    # dwg.add(dwg.image(
    #     href=BASE_PATH + '/resources/images/logo.png',
    #     insert=(550, 40),
    #     size=(150, 60),
    #     font_weight="bold",
    #     font_family='Goblin One'
    # ))
    # # add title
    # dwg.add(dwg.text(
    #     title,
    #     font_size='18px',
    #     style='font-weight:bold;',
    #     font_family='helvetica',
    #     insert=(xr, 320)
    # ))
    # add_multiline_text(dwg, text_body,
    #                    insert=(xr, 350),
    #                    font_size='12px',
    #                    )
    # dwg.saveas(TMP_SVG_FILE)
    # # convert svg to pdf
    # return cairosvg.svg2pdf(
    #     file_obj=open(TMP_SVG_FILE, 'rb'),
    # )