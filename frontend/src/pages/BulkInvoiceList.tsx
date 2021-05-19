import React from 'react';
import {useBackendAPI } from "../features/backend/backendAPI";
import {handleError} from "../features/error/errorHandler";
import {useAppDispatch} from "../app/hooks";

export function BulkInvoiceList() {

    const dispatch = useAppDispatch();

    console.log(useBackendAPI('bulk'))

    fetch(useBackendAPI('bulk'))
        .then(result => console.log(result))
        .catch(error => handleError(dispatch, error))

    return (
        <div className="BulkInvoiceList">
            List
        </div>
    )
}