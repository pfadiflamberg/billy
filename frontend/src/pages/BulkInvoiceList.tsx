import React from 'react';
import {useBackendAPI, useBackendURL} from "../features/backend/backendAPI";

export function BulkInvoiceList() {

    console.log(useBackendAPI('bulk'))

    fetch(useBackendAPI('bulk'))
        .then(result => console.log(result))
        .catch(err => console.log(err))

    return (
        <div className="BulkInvoiceList">
            List
        </div>
    )
}