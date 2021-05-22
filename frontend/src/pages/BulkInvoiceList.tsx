import React, {useEffect} from 'react';
import {useAppDispatch} from "../app/hooks";
import {fetchBulks} from "../features/bulk/bulkSlice";
import {Card} from 'react-bootstrap';

export function BulkInvoiceList() {

    const dispatch = useAppDispatch();

    useEffect(() => {
        console.log('load data')
        dispatch(fetchBulks())
    })

    return (
        <div className="BulkInvoiceList">
            <Card />
        </div>
    )
}