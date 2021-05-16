import generate
import hitobito

p = hitobito.getPerson(76100)
r = hitobito.getPerson(43867)
print(p)

drawing = generate.bill(
    title="Jahresrechnung",
    text_body="""
    Jedes Jahr erhalten alle Stufen, jeder Harst und Zug einen Beitrag aus der Korpskasse, um Anschaffungen von Material
    und anderen Ausgaben zu finanzieren. Ihr Sohn ist während den Übungen und Lagern, sowie bei der Hin- und Rückfahrt zu
    Pfadianlässen subsidiär gegen Unfall versichert. Für die Pfadileiter besteht zudem eine Haftpflichtversicherung. Um diese
    Kosten decken zu können, sind wir auf den Jahresbeitrag angewiesen.
    
    Der Jahresbeitrag für das Jahr 2021 beträgt CHF 70.00. Wir bitten Sie, den Jahresbeitrag bis zum oben angegebenen Datum auf
    unser Bankkonto einzuzahlen.
    """,
    account='CH4031000039529071000',
    creditor={
        'name': 'Pfadfinderkorps Flamberg', 'pcode': '8070', 'city': 'Zürich', 'country': 'CH',
    },
    hitobito_debtor=p,
    hitobito_sender=r,
    ref='210000000003139471430009017'
)