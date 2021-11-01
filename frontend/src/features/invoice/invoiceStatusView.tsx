import { useAppSelector } from "../../app/hooks";
import { ProgressBar } from 'react-bootstrap';
import { selectInvoices } from "./invoiceSlice";
import { badgeVariantForStatus } from "./invoiceListView";

function fraction(total: number, count: number): number {
    return 100 * count / total;
}

export function InvoiceStatusView() {

    const invoices = useAppSelector(selectInvoices);
    var invoiceList = Object.values(invoices);

    interface info {
        count: number,
        status: string
    }

    var infos: info[] = ['pending', 'paid', 'annulled'].map((status) => {
        return {
            'count': invoiceList.filter(i => i.status === status).length,
            'status': status
        }
    });

    return (
        <div>
            {invoiceList.length} Invoices ({infos.map((info) => { return info.count + " " + info.status }).join(', ')})
            <ProgressBar>
                {infos.map((info, idx) => {
                    return <ProgressBar
                        variant={badgeVariantForStatus(info.status)}
                        now={fraction(invoiceList.length, info.count)}
                        key={idx} />
                })}
            </ProgressBar>
        </div>
    )
}