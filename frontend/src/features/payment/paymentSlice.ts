import {AppThunk} from "../../app/store";
import {handleError} from "../error/errorSlice";
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

    request(new URL(API_PATH_PAYMENT, BACKEND_BASE), 'POST', {payments: payments})
        .then(r => {
            console.log("done");
        })
        .catch(e => dispatch(handleError(e)));
}