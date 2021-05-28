import {useAppDispatch, useAppSelector} from "../../app/hooks";
import React from "react";
import {Button, Form, Modal} from 'react-bootstrap';
import {selectShowCreateBulkView} from "./bulkSlice";
import {showCreateBulkView} from "./bulkSlice";
import {selectBackendBase} from "../backend/backendSlice";
import {handleError} from "../error/errorSlice";
import {request} from "../../app/request";

export function BulkCreateView() {

    const dispatch = useAppDispatch();

    const show = useAppSelector(selectShowCreateBulkView);
    const BACKEND_BASE = useAppSelector(selectBackendBase);

    let formData: { [key: string]: string } = {};

    const handleCreate = () => {
        request(new URL('bulk', BACKEND_BASE),
            'POST',
            formData)
            .then(r => {
                console.log('got response');
                console.log(r);
            })
            .catch(e => dispatch(handleError(e)));

    }

    const handleClose = () => {
        dispatch(showCreateBulkView(false));
    }

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        let target: string = e.target.name;
        let value: string = e.target.value;
        if (target === 'link') {
            let groups = value.match('groups/(?<groupID>[0-9]+)/mailing_lists/(?<mailingListID>[0-9]+)')?.groups;
            let group = groups?.groupID;
            let mailing = groups?.mailingListID;
            if (group) {
                formData['group'] = group;
            }
            if (mailing) {
                formData['mailing_list'] = mailing;
            }
        } else {
            formData[e.target.name] = value;
        }
    }

    return (
        <Modal show={show} onHide={() => handleClose()}>
            <Modal.Header closeButton>
                <Modal.Title>Create new Bulk</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                <Form>
                    <Form.Group>
                        <Form.Label>Title</Form.Label>
                        <Form.Control
                            name="title"
                            type="text"
                            placeholder="Title"
                            onChange={handleChange}></Form.Control>
                    </Form.Group>
                    <Form.Group>
                        <Form.Label>Mailing List URL</Form.Label>
                        <Form.Control
                            name="link"
                            type="text"
                            placeholder="https://db.scout.ch/de/groups/1147/mailing_lists/3518"
                            onChange={handleChange}></Form.Control>
                        <Form.Text className="text-muted">The URL of the mailing list containing the recipients of the bulk invoice.</Form.Text>
                    </Form.Group>
                </Form>
            </Modal.Body>
            <Modal.Footer>
                <Button variant="primary" onClick={() => handleCreate()}>
                    Create
                </Button>
            </Modal.Footer>
        </Modal>
    )

}