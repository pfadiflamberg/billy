import {useAppDispatch, useAppSelector} from "../../app/hooks";
import {Button, Form, Modal} from 'react-bootstrap';
import {selectShowUpdateBulkView, selectSelectedBulk, showUpdateBulkView, selectBulk, selectBulks, updateBulk, Bulk} from "./bulkSlice";

export function BulkView() {

    const dispatch = useAppDispatch();

    const bulks = useAppSelector(selectBulks);
    const selected = useAppSelector(selectSelectedBulk);
    const update = useAppSelector(selectShowUpdateBulkView);

    const readOnly = !update;
    const orgBulk = bulks[selected];
    var bulk: Bulk | undefined;
    if (orgBulk) {
        bulk = JSON.parse(JSON.stringify(orgBulk));
    }

    return (
        <div>
            <Modal show={bulk} onHide={() => {
                dispatch(showUpdateBulkView(false));
                dispatch(selectBulk(''))
            }} size="lg">
                { bulk &&
                    <div>
                        <Modal.Header closeButton>
                        <Modal.Title>{bulk.display_name}</Modal.Title>
                        </Modal.Header>
                        <Modal.Body>
                            <Form>
                                <Form.Group>
                                    <Form.Label >Title:</Form.Label>
                                    <Form.Control readOnly={readOnly}
                                        name="display_name"
                                        type="text"
                                        onChange={e => (bulk) ? bulk.display_name = e.target.value : true}
                                        defaultValue={bulk.display_name}>
                                    </Form.Control>
                                </Form.Group>
                                <Form.Group>
                                    <Form.Label>Mail:</Form.Label>
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
                                        style={{ height: '300px' }}
                                        onChange={e => (bulk) ? bulk.text_invoice = e.target.value : true}
                                        defaultValue={bulk.text_invoice}>
                                    </Form.Control>
                                </Form.Group>
                                <Form.Group>
                                    <Form.Label>Reminder:</Form.Label>
                                    <Form.Control readOnly={readOnly} as="textarea"
                                        name="text_reminder"
                                        type="text"
                                        style={{ height: '300px' }}
                                        onChange={e => (bulk) ? bulk.text_reminder = e.target.value : true}
                                        defaultValue={bulk.text_reminder}>
                                    </Form.Control>
                                </Form.Group>
                            </Form>
                            { readOnly &&
                                <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                                    <Button variant="secondary" type="submit" onClick={() => dispatch(showUpdateBulkView(true))}>
                                        Edit
                                    </Button>
                                </div>
                            }
                            { !readOnly &&
                                <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                                    <Button variant="primary" type="submit" onClick={() => {
                                        if (bulk) {
                                            dispatch(updateBulk(bulk));
                                        }
                                    }}>
                                        Save
                                    </Button>
                                </div>
                            }
                        </Modal.Body>
                    </div>
                }
            </Modal>
        </div>
    )

}