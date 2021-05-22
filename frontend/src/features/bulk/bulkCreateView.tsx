import {useAppSelector} from "../../app/hooks";
import React from "react";
import {Modal} from 'react-bootstrap';
import {selectShowCreateBulkView} from "./bulkSlice";

export function BulkCreateView() {

    const show = useAppSelector(selectShowCreateBulkView);

    return (
        <Modal show={show}>
            <Modal.Header>
                <Modal.Title>Create new Bulk</Modal.Title>
            </Modal.Header>
            <Modal.Body>

            </Modal.Body>
        </Modal>
    )

}