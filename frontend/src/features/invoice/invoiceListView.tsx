import { useAppSelector, useAppDispatch } from "../../app/hooks";
import { selectInvoices, annulInvoice, viewPDF, Invoice } from "./invoiceSlice";
import { Form, ListGroup, Dropdown, Row, Col, ButtonGroup, Button, DropdownButton } from 'react-bootstrap';
import { useState } from "react";

export function badgeVariantForStatus(status: string): string {
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

    const [filter, setFilter] = useState<string>('');

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

    if (props.show_filter && filter !== '') {
        invoices = invoices.filter(i => {
            var include = false;
            [i.esr, i.recipient_name].forEach((field) => {
                if (field.toLowerCase().includes(filter.toLowerCase())) {
                    include = true;
                }
            })
            return include;
        });
    }

    return (
        <div className="InvoiceListView">
            {props.show_filter &&
                <Form>
                    <Form.Group>
                        <Form.Control
                            name="invoice search"
                            type="text"
                            onChange={e => setFilter(e.target.value)}
                            placeholder="Find invoice...">
                        </Form.Control>
                    </Form.Group>
                </Form>
            }
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
                                            {invoice.status !== 'annulled' &&
                                                <DropdownButton
                                                    as={ButtonGroup}
                                                    title={''}
                                                    id={invoice.name}
                                                    size="sm"
                                                    variant={badgeVariantForStatus(invoice.status)}
                                                    active={invoice.status !== 'annulled'}
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
                                            }
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