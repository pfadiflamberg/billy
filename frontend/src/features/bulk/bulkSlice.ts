import {createSlice, PayloadAction} from "@reduxjs/toolkit";
import {AppThunk, RootState} from "../../app/store";
import {handleError, newPopup, Popup} from "../popup/popupSlice";
import {fetchInvoicesByBulk} from "../invoice/invoiceSlice";
import {selectBackendBase} from "../backend/backendSlice";
import { request, checkRequest } from "../../app/request";

const API_PATH_BULK = 'bulk'

export type Bulk = {
    name: string,
    title: string,
    status: string,
    update_time: string,
    mailing_list: string,
    text_mail: string,
    text_invoice: string,
    text_reminder: string,
    due_date: string,
}

export type BulkDict = {
    [Key: string]: Bulk
}

export interface BulkState {
    items: BulkDict,
    showCreateBulkView: boolean,
    showUpdateBulkView: boolean,
    showEmailPreviewBulkView: boolean,
    sendingEmail: boolean,
}

const initialState: BulkState = {
    items: {},
    showCreateBulkView: false,
    showUpdateBulkView: false,
    showEmailPreviewBulkView: false,
    sendingEmail: false,
}

function variableCheck(...args: string[]) {
    const ALLOWED_VARIABLES = ['title', 'due_date', 'year_issued', 'date_issued', 'recipient_name', 'recipient_shortname', 'sender_name', 'sender_shortname']
    var unknownVariables = args.map(text => {
        return [ ...text.matchAll(/{{ *([^} ]*) *}}/gm) ].map(match => match[1]).filter(v => !ALLOWED_VARIABLES.includes(v));
    }).flat()
    var unknownVariablesWCount: { [Key: string]: number } = {};
    for (const v in unknownVariables) {
        unknownVariablesWCount[unknownVariables[v]] ? unknownVariablesWCount[unknownVariables[v]]++ : unknownVariablesWCount[unknownVariables[v]] = 1;
    }
    var errors = []
    for (let key in unknownVariablesWCount) {
        var str = ""
        const count = unknownVariablesWCount[key];
        if (count > 1) {
            str += " (" + count + "x)"
        }
        errors.push({description: key + str})
    }
    if (errors.length > 0) {
        return {title: 'Invalid Variable', description: 'Invalid variable used. Use: ' + ALLOWED_VARIABLES.join(', ') + '. You used:', details: errors};
    }
}

export const bulkSlice = createSlice({
    name: 'bulk',
    initialState,
    reducers: {
        setBulks: (state, { payload }: PayloadAction<Bulk[]>) => {
            state.items = {};
            payload.forEach((r) => {
                state.items[r.name] = r;
            })
        },
        setBulk: (state, { payload }: PayloadAction<Bulk>) => {
            state.items[payload.name] = payload;
        },
        showCreateBulkView: (state, { payload }: PayloadAction<boolean>) => {
            state.showCreateBulkView = payload;
        },
        showUpdateBulkView: (state, { payload }: PayloadAction<boolean>) => {
            state.showUpdateBulkView = payload;
        },
        showEmailPreviewBulkView: (state, { payload }: PayloadAction<boolean>) => {
            state.showEmailPreviewBulkView = payload;
        },
        setSendingEmail: (state, { payload }: PayloadAction<boolean>) => {
            state.sendingEmail = payload;
        }
    }
})

const { setBulks, setBulk, showCreateBulkView, showUpdateBulkView, showEmailPreviewBulkView, setSendingEmail } = bulkSlice.actions;

export const fetchBulks = (): AppThunk => async (
    dispatch,
    getState
) => {

    const BACKEND_BASE = selectBackendBase(getState());

    interface BulkResponse {
        items: any[],
    }

    request(new URL(API_PATH_BULK, BACKEND_BASE))
        .then(r => {
            const data = r as unknown as BulkResponse;
            dispatch(setBulks(data.items));
        })
        .catch(e => dispatch(handleError(e)));
}

export const createBulk = (data: { [key: string]: string }): AppThunk => async (
    dispatch,
    getState
) => {

    const BACKEND_BASE = selectBackendBase(getState());

    request(new URL(API_PATH_BULK, BACKEND_BASE), 'POST', data)
        .then(r => {
            dispatch(showCreateBulkView(false));
            const bulk = r as unknown as Bulk;
            dispatch(setBulk(bulk));
            dispatch(showUpdateBulkView(true));
            window.open(bulk.name, "_self");
        })
        .catch(e => dispatch(handleError(e)));
}

export const updateBulk = (bulk: Bulk): AppThunk => async (
    dispatch,
    getState
) => {

    const BACKEND_BASE = selectBackendBase(getState());

    // check for invalid variables
    var error = variableCheck(bulk.text_mail, bulk.text_invoice, bulk.text_reminder);
    if (error) {
        dispatch(handleError(error));
        return
    }

    request(new URL(bulk.name, BACKEND_BASE), 'PUT', bulk)
        .then(r => {
            dispatch(showUpdateBulkView(false));
            dispatch(setBulk(bulk));
        })
        .catch(e => dispatch(handleError(e)));
}

export const duplicateBulk = (org_bulk: Bulk): AppThunk => async (
    dispatch,
    getState
) => {

    const BACKEND_BASE = selectBackendBase(getState());

    // create new title (if possible change year)
    var year: number = new Date().getFullYear()
    var new_title = org_bulk.title.replace((year-1).toString(), year.toString());
    if (new_title === org_bulk.title) {
        new_title += ' (copy)';
    }

    var createBulkForm = {
        'title': new_title,
        'mailing_list': org_bulk.mailing_list,
    };

    request(new URL(API_PATH_BULK, BACKEND_BASE), 'POST', createBulkForm)
        .then(r => {
            var new_empty_bulk: Bulk = r as unknown as Bulk;
            var new_bulk = JSON.parse(JSON.stringify(org_bulk));
            new_bulk.name = new_empty_bulk.name;
            new_bulk.title = new_empty_bulk.title;
            new_bulk.status = new_empty_bulk.status;
            request(new URL(new_empty_bulk.name, BACKEND_BASE), 'PUT', new_bulk);
            dispatch(setBulk(new_bulk));
        })
        .catch(e => dispatch(handleError(e)));
}

export const issueBulk = (bulk: Bulk): AppThunk => async (
    dispatch,
    getState,
) => {

    const BACKEND_BASE = selectBackendBase(getState());

    request(new URL(bulk.name + ":issue", BACKEND_BASE), 'POST')
        .then(r => {
            var updated_bulk = JSON.parse(JSON.stringify(bulk));
            updated_bulk.status = 'issued'
            dispatch(setBulk(updated_bulk));
            dispatch(showUpdateBulkView(false));
            dispatch(fetchInvoicesByBulk(bulk));
        })
        .catch(e => dispatch(handleError(e)));
}

export const sendBulk = (bulk: Bulk, message: string, options = {}): AppThunk => async (
    dispatch,
    getState,
) => {

    const BACKEND_BASE = selectBackendBase(getState());
    var error = variableCheck(message);
    if (error) {
        dispatch(handleError(error));
        return
    }

    var url = new URL(bulk.name + ":send", BACKEND_BASE);
    Object.entries(options).forEach(option => url.searchParams.append(option[0], String(option[1])));

    type BulkSendResponse= {
        sent_count: number;
    }

    dispatch(setSendingEmail(true));
    request(url, 'POST', {'mail_body': message})
        .then(r => {
            const resp = r as unknown as BulkSendResponse;
            var popup = {title: 'Email Sent', description: resp.sent_count + ' emails sent.'} as Popup;
            dispatch(newPopup(popup));
            dispatch(showEmailPreviewBulkView(false));
        })
        .catch(e => dispatch(handleError(e)))
        .finally(() => dispatch(setSendingEmail(false)));
}

export const viewPDFs = (bulk: Bulk): AppThunk => async (
    dispatch,
    getState,
) => {

    const BACKEND_BASE = selectBackendBase(getState());
    // we check if API will respond without error before redirecting the user
    var url = new URL(bulk.name + ".pdf", BACKEND_BASE);
    checkRequest(url)
        .then(r => {
            window.open(url.toString(), "_self");
        })
        .catch(e => {
            dispatch(fetchInvoicesByBulk(bulk));
            dispatch(handleError(e));
        });
}

export const selectBulks = (state: RootState) => state.bulk.items;
export const selectShowCreateBulkView = (state: RootState) => state.bulk.showCreateBulkView;
export const selectShowUpdateBulkView = (state: RootState) => state.bulk.showUpdateBulkView;
export const selectEmailPreviewBulkView = (state: RootState) => state.bulk.showEmailPreviewBulkView;
export const selectIsSendingBulk = (state: RootState) => state.bulk.sendingEmail;

export { showCreateBulkView, showUpdateBulkView, showEmailPreviewBulkView };

export default bulkSlice.reducer;
