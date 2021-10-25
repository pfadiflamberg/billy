import { useAppSelector, useAppDispatch } from "../../app/hooks";
import { selectInvoices, annulInvoice, viewPDF, Invoice } from "./invoiceSlice";
import { ListGroup, Dropdown, Row, Col, ButtonGroup, Button, DropdownButton } from 'react-bootstrap';

function badgeVariantForStatus(status: string): string {
    switch (status) {
        case 'pending':
            return 'primary'
        case 'paid':
            return 'success'
        case 'annulled':
            return 'secondary'
        default:
            return 'warning'
    }
}


export function InvoiceListView(props: any) {


    const dispatch = useAppDispatch();
    const allInvoices = useAppSelector(selectInvoices);

    var invoices = Object.values(allInvoices).sort((a: Invoice, b: Invoice) => {
        if (a.status < b.status) {
            return 1;
        } else {
            return -1;
        }
    });
    if (props.with_names) {
        invoices = invoices.filter(i => props.with_names.includes(i.name));
    }

    return (
        <div className="InvoiceListView">
            <ListGroup>
                {invoices.map((invoice) => {
                    return (
                        <ListGroup.Item key={invoice.name}>
                            <Row>
                                <Col>
                                    <div className="BulkInvoiceListTitle">
                                        {invoice.recipient_name}
                                    </div>
                                    <div className="BulkInvoiceListSubTitle">
                                        {invoice.esr}
                                        {invoice.last_email_sent &&
                                            <div>
                                                Last Email Sent: {new Date(invoice.last_email_sent).toLocaleString('de-DE')}
                                            </div>
                                        }
                                    </div>
                                </Col>
                                <Col xs={3}>
                                    <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                                        <ButtonGroup size="sm">

                                            <Button
                                                onClick={e => e.stopPropagation()}
                                                variant={badgeVariantForStatus(invoice.status)}>
                                                {invoice.status}
                                            </Button>
                                            <DropdownButton
                                                as={ButtonGroup}
                                                title={''}
                                                id={invoice.name}
                                                size="sm"
                                                variant={badgeVariantForStatus(invoice.status)}
                                                onClick={e => e.stopPropagation()}
                                            >
                                                <Dropdown.Item onClick={e => dispatch(viewPDF(invoice))}>View PDF</Dropdown.Item>
                                                {invoice.status === 'pending' &&
                                                    <div>
                                                        <Dropdown.Divider />
                                                        <Dropdown.Item onClick={e => dispatch(annulInvoice(invoice))}>Annul</Dropdown.Item>
                                                    </div>
                                                }
                                            </DropdownButton>
                                        </ButtonGroup>
                                    </div>
                                </Col>
                            </Row>
                        </ListGroup.Item>
                    )
                })}
            </ListGroup>
        </div>
    )
}