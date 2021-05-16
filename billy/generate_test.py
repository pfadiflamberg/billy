import generate
import hitobito

p = hitobito.getPerson(76100)
r = hitobito.getPerson(43867)
print(p)

drawing = generate.bill(
    title="Title",
    text_body="""
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
    """,
    account='CH4031000039529071000',
    creditor={
        'name': 'Pfadfinderkorps Flamberg', 'pcode': '8070', 'city': 'Zürich', 'country': 'CH',
    },
    hitobito_debtor=p,
    hitobito_sender=r,
    amount='12.12',
    ref='210000000003139471430009017'
)

generate.billAsFile(drawing, "tmp.pdf")
