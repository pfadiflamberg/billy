import { useAppSelector } from "../../app/hooks";
import { selectBackendBase } from "../backend/backendSlice";
import { selectInvoices } from "./invoiceSlice";
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


export function InvoiceListView() {

    const BACKEND_BASE = useAppSelector(selectBackendBase);

    const invoices = useAppSelector(selectInvoices);

    return (
        <div className="InvoiceListView">
            <ListGroup>
                {Object.keys(invoices).map((key) => {
                    const invoice = invoices[key];
                    return (
                        <ListGroup.Item key={key}>
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
                                                <Dropdown.Item onClick={e => window.open(BACKEND_BASE + invoice.name + '.pdf')}>Get PDF</Dropdown.Item>
                                                <Dropdown.Item disabled onClick={e => console.log('TODO')}>Send as Email (TODO)</Dropdown.Item>
                                                <Dropdown.Divider />
                                                <Dropdown.Item disabled onClick={e => console.log('TODO')}>Annul (TODO)</Dropdown.Item>
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