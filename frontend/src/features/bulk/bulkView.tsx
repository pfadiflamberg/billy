import { useAppDispatch, useAppSelector } from "../../app/hooks";
import { Button, Form, Modal } from 'react-bootstrap';
import { selectShowUpdateBulkView, selectSelectedBulk, selectEmailPreviewBulkView, showUpdateBulkView, showEmailPreviewBulkView, deselectBulk, selectBulks, updateBulk, Bulk, issueBulk, sendBulk, selectIsSendingBulk } from "./bulkSlice";
import { selectInvoices } from "../invoice/invoiceSlice";
import { InvoiceListView } from "../invoice/invoiceListView";
import { InvoiceStatusView } from "../invoice/invoiceStatusView";

export function BulkView() {

    const dispatch = useAppDispatch();

    const bulks = useAppSelector(selectBulks);
    const selected = useAppSelector(selectSelectedBulk);
    const update = useAppSelector(selectShowUpdateBulkView);
    const emailPreview = useAppSelector(selectEmailPreviewBulkView);
    const invoices = useAppSelector(selectInvoices);
    const isSendingEmail = useAppSelector(selectIsSendingBulk);

    const readOnly = !update;
    const orgBulk = bulks[selected];
    var bulk: Bulk | undefined;
    if (orgBulk) {
        bulk = JSON.parse(JSON.stringify(orgBulk));
    }

    function DaysTillDue(bulk: Bulk) {
        var due_date = new Date(bulk.due_date);
        var date_now = new Date();
        var diff = due_date.getTime() - date_now.getTime();
        if (diff < 0) {
            return 'overdue since ' + Math.abs(Math.floor(diff / (1000 * 60 * 60 * 24)));
        }
        return Math.ceil(diff / (1000 * 60 * 60 * 24));
    }

    var skipIncomplete: boolean = false;
    var email_text: string = (bulk) ? bulk.text_mail : '';

    return (
        <div>
            <Modal show={emailPreview} onHide={() => {
                dispatch(showEmailPreviewBulkView(false));
            }}>
                {bulk &&
                    <div>
                        <Modal.Header closeButton>
                            <Modal.Title>Send as Email.</Modal.Title>
                        </Modal.Header>
                        <Modal.Body>
                            Sending <em>{bulk.title}</em> to {Object.entries(invoices).filter(([k, b]) => b.status === 'pending').length}/{Object.keys(invoices).length} pending recipients due in {DaysTillDue(bulk)} days.
                            <Form.Group>
                                <Form.Label>Email:</Form.Label>
                                <Form.Control as="textarea"
                                    name="text_mail"
                                    type="text"
                                    style={{ height: '300px' }}
                                    onChange={e => email_text = e.target.value}
                                    defaultValue={email_text}>
                                </Form.Control>
                            </Form.Group>
                            <Form>
                                <Form.Check type={'checkbox'} label={'Skip recipients without email address'} onChange={e => skipIncomplete = e.target.checked} />
                            </Form>
                        </Modal.Body>
                        <Modal.Footer>
                            <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                                <Button variant="primary" type="submit" disabled={isSendingEmail} onClick={() => (bulk) ? dispatch(sendBulk(bulk, email_text, { skip: Number(skipIncomplete) })) : true} >
                                    {isSendingEmail ? 'Sending...' : 'Send'}
                                </Button>
                            </div>
                        </Modal.Footer>
                    </div>
                }
            </Modal>
            <Modal show={bulk !== undefined} onHide={() => {
                dispatch(showUpdateBulkView(false));
                dispatch(deselectBulk())
            }} size="lg">
                {bulk &&
                    <div>
                        <Modal.Header closeButton>
                            <Modal.Title>{bulk.title}</Modal.Title>
                        </Modal.Header>
                        <Modal.Body>
                            <Form>
                                <Form.Group>
                                    <Form.Label>Mailing List:</Form.Label>
                                    <Form.Control readOnly={readOnly}
                                        name="mailing_list"
                                        type="text"
                                        onChange={e => (bulk) ? bulk.mailing_list = e.target.value : true}
                                        defaultValue={bulk.mailing_list}>
                                    </Form.Control>
                                </Form.Group>
                                <Form.Group>
                                    <Form.Label >Title:</Form.Label>
                                    <Form.Control readOnly={readOnly}
                                        name="title"
                                        type="text"
                                        onChange={e => (bulk) ? bulk.title = e.target.value : true}
                                        defaultValue={bulk.title}>
                                    </Form.Control>
                                </Form.Group>
                                {bulk && bulk.status !== 'draft' &&
                                    <Form.Group>
                                        <Form.Label>Due Date:</Form.Label>
                                        <Form.Control readOnly={true}
                                            name="due_date"
                                            type="date"
                                            // onChange={e => (bulk) ? bulk.due_date = new Date(e.target.value).toISOString() : true}
                                            defaultValue={new Date(bulk.due_date).toISOString().split('T')[0]}>
                                        </Form.Control>
                                    </Form.Group>
                                }
                                <Form.Group>
                                    <Form.Label>Email:</Form.Label>
                                    <Form.Control readOnly={readOnly} as="textarea"
                                        name="text_mail"
                                        type="text"
                                        style={{ height: '300px' }}
                                        onChange={e => (bulk) ? bulk.text_mail = e.target.value : true}
                                        defaultValue={bulk.text_mail}>
                                    </Form.Control>
                                </Form.Group>
                                <Form.Group>
                                    <Form.Label>Text:</Form.Label>
                                    <Form.Control readOnly={readOnly} as="textarea"
                                        name="text_invoice"
                                        type="text"
                                        style={{ height: '650px' }}
                                        onChange={e => (bulk) ? bulk.text_invoice = e.target.value : true}
                                        defaultValue={bulk.text_invoice}>
                                    </Form.Control>
                                </Form.Group>
                                <Form.Group>
                                    <Form.Label>Reminder:</Form.Label>
                                    <Form.Control readOnly={readOnly} as="textarea"
                                        name="text_reminder"
                                        type="text"
                                        style={{ height: '650px' }}
                                        onChange={e => (bulk) ? bulk.text_reminder = e.target.value : true}
                                        defaultValue={bulk.text_reminder}>
                                    </Form.Control>
                                </Form.Group>
                            </Form>
                            {readOnly &&
                                <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                                    <div className="actions">
                                        {bulk && bulk.status === 'draft' &&
                                            <div>
                                                <Button variant="secondary" type="submit" onClick={() => dispatch(showUpdateBulkView(true))}>
                                                    Edit
                                                </Button>
                                                <Button variant="primary" type="submit" onClick={() => (bulk) ? dispatch(issueBulk(bulk)) : true}>
                                                    Issue
                                                </Button>
                                            </div>
                                        }
                                        {bulk && bulk.status === 'issued' &&
                                            <Button variant="primary" type="submit" onClick={() => (bulk) ? dispatch(showEmailPreviewBulkView(true)) : true}>
                                                Send as Email
                                            </Button>
                                        }
                                    </div>
                                </div>
                            }
                            {!readOnly &&
                                <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                                    <Button variant="primary" type="submit" onClick={() => (bulk) ? dispatch(updateBulk(bulk)) : true} >
                                        Save
                                    </Button>
                                </div>
                            }
                            {bulk && bulk.status !== 'draft' &&
                                <div>
                                    <InvoiceStatusView />
                                    <InvoiceListView />
                                </div>
                            }
                        </Modal.Body>
                    </div>
                }
            </Modal>
        </div>
    )

}