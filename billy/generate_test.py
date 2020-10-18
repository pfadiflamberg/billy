import generate
import hitobito

p = hitobito.getPerson(76100)
r = hitobito.getPerson(43867)
print(p)

generate.bill(
    account='CH4431999123000889012',
    creditor={
        'name': 'Pfadfinderkorps Flamberg', 'pcode': '8070', 'city': 'Zürich', 'country': 'CH',
    },
    hitobito_debtor=p,
    hitobito_back=r,
    amount='12.12',
    ref='210000000003139471430009017'
)
