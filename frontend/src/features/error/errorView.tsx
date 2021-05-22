import {useAppSelector} from "../../app/hooks";
import {selectErrors} from "./errorSlice";
import React from "react";
import {Modal} from 'react-bootstrap';

export function ErrorView() {

    const errors = useAppSelector(selectErrors);

    let message = 'no errors';
    let hasErrors = 0 < errors.length;
    if (hasErrors) {
        message = errors[0].message;
    }

    return (
        <Modal show={hasErrors}>
            <Modal.Header>
                <Modal.Title>Opppssssss...</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                {message}
            </Modal.Body>
        </Modal>
    )

}