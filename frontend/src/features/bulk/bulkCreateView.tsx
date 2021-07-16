import { useAppDispatch, useAppSelector } from "../../app/hooks";
import React from "react";
import { Button, Form, Modal } from 'react-bootstrap';
import { selectShowCreateBulkView } from "./bulkSlice";
import { showCreateBulkView, createBulk } from "./bulkSlice";

export function BulkCreateView() {

    const dispatch = useAppDispatch();

    const show = useAppSelector(selectShowCreateBulkView);

    let formData: { [key: string]: string } = {};

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
                        <Form.Label>Mailing List URL</Form.Label>
                        <Form.Control
                            name="mailing_list"
                            type="text"
                            placeholder="https://db.scout.ch/de/groups/1147/mailing_lists/3518"
                            onChange={handleChange}></Form.Control>
                        <Form.Text className="text-muted">The URL of the mailing list containing the recipients of the bulk invoice.</Form.Text>
                    </Form.Group>
                </Form>
            </Modal.Body>
            <Modal.Footer>
                <Button variant="primary" onClick={() => dispatch(createBulk(formData))}>
                    Create
                </Button>
            </Modal.Footer>
        </Modal>
    )

}