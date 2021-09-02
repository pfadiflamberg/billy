import { useAppSelector } from "../../app/hooks";
import { ProgressBar } from 'react-bootstrap';
import { selectInvoices } from "./invoiceSlice";

function fraction(total: number, count: number): number {
    return 100 * count / total;
}

export function InvoiceStatusView() {

    const invoices = useAppSelector(selectInvoices);

    var invoiceList = Object.values(invoices);
    var countPaid = invoiceList.filter(i => i.status === 'paid').length
    var countAnnulled = invoiceList.filter(i => i.status === 'annulled').length

    return (
        <div>
            <ProgressBar>
                <ProgressBar variant="success" now={fraction(invoiceList.length, countPaid)} key={1} />
                <ProgressBar variant="secondary" now={fraction(invoiceList.length, countAnnulled)} key={2} />
            </ProgressBar>
        </div>
    )
}