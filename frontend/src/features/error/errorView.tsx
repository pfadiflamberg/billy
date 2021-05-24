import {useAppDispatch, useAppSelector} from "../../app/hooks";
import {clearErrors, selectErrors} from "./errorSlice";
import React from "react";
import {Modal} from 'react-bootstrap';

export function ErrorView() {

    const dispatch = useAppDispatch();

    const errors = useAppSelector(selectErrors);

    let message = 'no errors';
    let hasErrors = 0 < errors.length;
    if (hasErrors) {
        message = errors[0].message;
    }

    return (
        <Modal show={hasErrors} onHide={() => dispatch(clearErrors())}>
            <Modal.Header closeButton>
                <Modal.Title>Error</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                {message}
            </Modal.Body>
        </Modal>
    )

}