import {AppThunk} from "../../app/store";
import {handleError, newPopup, Popup} from "../popup/popupSlice";
import {selectBackendBase} from "../backend/backendSlice";
import { request } from "../../app/request";

const API_PATH_PAYMENT = 'payment'

export type Payment = {
    esr: String,
    amount: String,
    date: String
}

export const uploadPayments = (payments: Payment[]): AppThunk => async (
    dispatch,
    getState
) => {

    const BACKEND_BASE = selectBackendBase(getState());

    type UploadPaymentsResponse = {
        marked_paid: number;
        not_found: number;
    }

    request(new URL(API_PATH_PAYMENT, BACKEND_BASE), 'POST', {payments: payments})
        .then(r => {
            const resp = r as unknown as UploadPaymentsResponse;
            var popup = {title: 'Payments Processed', description: resp.marked_paid + ' invoices have been updated. While encountering ' + resp.not_found + ' unknown payments.'} as Popup;
            dispatch(newPopup(popup))
        })
        .catch(e => dispatch(handleError(e)));
}