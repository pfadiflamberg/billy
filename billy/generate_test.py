import generate
import hitobito
import datetime

recipient = hitobito.getPerson(76100)
sender = hitobito.getPerson(43867)

date = datetime.datetime.utcnow()

pdf = generate.invoicePDF(
    title="Jahresrechnung {year}".format(year=date.year),
    text_body="""
    Sehr geehrte Flambergeltern, {salutation},
    Jedes Jahr erhalten alle Stufen, jeder Harst und Zug einen Beitrag aus der Korpskasse, um Anschaffungen von Material und andere Ausgaben zu ﬁnanzieren. Ihr Sohn ist während den Übungen und Lagern, sowie bei der Hin- und Rückfahrt zu Pfadianlässen subsidiär gegen Unfall versichert. Für die Pfadileiter besteht zudem eine Haftpﬂichtversicherung. Um diese Kosten decken zu können, sind wir auf den Jahresbeitrag jedes einzelnen Flambergers angewiesen.
    Leider mussten wir feststellen, dass der Jahresbeitrag von {shortname} für das Jahr {year} noch nicht bezahlt wurde. Wir bitten Sie, den Jahresbeitrag von <b>CHF 70</b> in den nächsten 10 Tagen auf unser Bankkonto einzuzahlen. Bitte benützen Sie dazu ausschliesslich den untenstehenden Einzahlungsschein (mehrere Jahresbeiträge bitte jeweils separat). Beim e-Banking bitten wir Sie, die Referenznummer unbedingt aufzuführen. Sie erleichtern uns damit die Arbeit wesentlich. Besonders dankbar sind wir denjenigen, die den Betrag grosszügig aufrunden.
    Sollte Ihr Sohn nicht mehr Mitglied unseres Korps sein und diesen Brief irrtümlicherweise erhalten haben, so bitten wir Sie höﬂich, dies dem Korpskassier (Adresse siehe oben) schriftlich oder per Email mitzuteilen.
    Wir danken Ihnen herzlich für das uns entgegengebrachte Vertrauen und wünschen Ihrem Sohn ein ausgefülltes, erlebnisreiches Pfadijahr im Flamberg.
    Flamberggrüsse
    {sender}
    """.format(
        salutation=recipient['salutation'],
        shortname=recipient['shortname'],
        year=date.year,
        sender=sender['shortname']
    ),
    account='CH4031000039529071000',
    creditor={
        'name': 'Pfadfinderkorps Flamberg', 'pcode': '8070', 'city': 'Zürich', 'country': 'CH',
    },
    hitobito_debtor=recipient,
    hitobito_sender=sender,
    ref='210000000003139471430009017',
    date=date,
    due_date=date,
)

f = open("generate_test.pdf", "wb")
f.write(pdf)
f.close()