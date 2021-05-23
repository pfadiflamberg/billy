import {useAppDispatch, useAppSelector} from "../../app/hooks";
import React from "react";
import {Button, Form, Modal} from 'react-bootstrap';
import {selectShowCreateBulkView} from "./bulkSlice";
import {showCreateBulkView} from "./bulkSlice";

export function BulkCreateView() {

    const dispatch = useAppDispatch();

    const show = useAppSelector(selectShowCreateBulkView);

    function handleClose(save: boolean) {
        dispatch(showCreateBulkView(false));
    }

    return (
        <Modal show={show} onHide={() => handleClose(false)}>
            <Modal.Header closeButton>
                <Modal.Title>Create new Bulk</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                <Form>

                </Form>
            </Modal.Body>
            <Modal.Footer>
                <Button variant="primary" onClick={() => handleClose(true)}>
                    Create
                </Button>
            </Modal.Footer>
        </Modal>
    )

}