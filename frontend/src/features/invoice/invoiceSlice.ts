import {createSlice, PayloadAction} from "@reduxjs/toolkit";
import {AppThunk, RootState} from "../../app/store";
import {handleError} from "../error/errorSlice";
import {selectBackendBase} from "../backend/backendSlice";
import { request } from "../../app/request";
import { Bulk } from "../bulk/bulkSlice";

const API_PATH_INVOICE = 'invoice'

export type Invoice = {
    name: string,
    status: string,
    recipient_name: string,
    esr: string,
    last_email_sent: string,
}

export type InvoiceDict = {
    [Key: string]: Invoice
}

export interface InvoiceState {
    items: InvoiceDict;
    selected: string,
}

const initialState: InvoiceState = {
    items: {},
    selected: '',
}

export const invoiceSlice = createSlice({
    name: 'invoice',
    initialState,
    reducers: {
        setInvoices: (state, { payload }: PayloadAction<Invoice[]>) => {
            state.items = {};
            payload.forEach((r) => {
                state.items[r.name] = r;
            })
        }
    }
})

const { setInvoices } = invoiceSlice.actions;

export const fetchInvoicesByBulk = (bulk: Bulk): AppThunk => async (
    dispatch,
    getState,
) => {

    const BACKEND_BASE = selectBackendBase(getState());

    interface InvoiceResponse {
        items: Invoice[],
    }

    request(new URL(bulk.name + '/' + API_PATH_INVOICE, BACKEND_BASE))
        .then(r => {
            const data = r as unknown as InvoiceResponse;
            dispatch(setInvoices(data.items));
        })
        .catch(e => dispatch(handleError(e)));
}

export const selectInvoices = (state: RootState) => state.invoice.items;

export default invoiceSlice.reducer;