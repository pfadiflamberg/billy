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
            .catch(e => dispatch(handleError(e))); // TODO: needs different error here

    }

    const handleClose = () => {
        dispatch(showCreateBulkView(false));
    }

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        formData[e.target.name] = e.target.value;
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
                        <Form.Label>Root Group ID</Form.Label>
                        <Form.Control
                            name="group"
                            type="text"
                            placeholder="12345"
                            onChange={handleChange}></Form.Control>
                        <Form.Text className="text-muted">All users in this and it's child groups are added to the bulk.</Form.Text>
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