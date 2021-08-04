import {createSlice, PayloadAction} from "@reduxjs/toolkit";
import {AppThunk, RootState} from "../../app/store";
import {handleError} from "../error/errorSlice";
import {fetchInvoicesByBulk} from "../invoice/invoiceSlice";
import {selectBackendBase} from "../backend/backendSlice";
import { request } from "../../app/request";

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
    selected: string,
    showCreateBulkView: boolean,
    showUpdateBulkView: boolean,
    showEmailPreviewBulkView: boolean,
    sendingEmail: boolean,
}

const initialState: BulkState = {
    items: {},
    selected: '',
    showCreateBulkView: false,
    showUpdateBulkView: false,
    showEmailPreviewBulkView: false,
    sendingEmail: false,
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
        setSelectedBulk: (state, { payload }: PayloadAction<string>) => {
            state.selected = payload;
        },
        deselectBulk: (state) => {
            state.selected = '';
            window.history.replaceState({}, "", window.location.origin);
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

const { setBulks, setBulk, setSelectedBulk, deselectBulk, showCreateBulkView, showUpdateBulkView, showEmailPreviewBulkView, setSendingEmail } = bulkSlice.actions;

export const selectBulk = (bulk: Bulk): AppThunk => async (
    dispatch,
) => {
    window.history.replaceState({}, "", bulk.name);
    dispatch(setSelectedBulk(bulk.name));
    if (bulk.status !== 'draft') {
        dispatch(fetchInvoicesByBulk(bulk));
    }
}

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
            dispatch(selectBulk(bulk));
        })
        .catch(e => dispatch(handleError(e)));
}

export const updateBulk = (bulk: Bulk): AppThunk => async (
    dispatch,
    getState
) => {

    // check for invalid variables
    const ALLOWED_VARIABLES = ['title', 'due_date', 'year_issued', 'date_issued', 'recipient_name', 'recipient_shortname', 'sender_name', 'sender_shortname']
    var unknownVariables = [bulk.text_mail, bulk.text_invoice, bulk.text_reminder].map(text => {
        return [ ...text.matchAll(/{{ *([^} ]*) *}}/gm) ].map(match => match[1]).filter(v => !ALLOWED_VARIABLES.includes(v));
    }).flat()
    console.log(unknownVariables);
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
        dispatch(handleError({title: 'Invalid Variable', description: 'Invalid variable used. Use: ' + ALLOWED_VARIABLES.join(', ') + '. You used:', details: errors}));
        return
    }

    const BACKEND_BASE = selectBackendBase(getState());

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
        })
        .catch(e => dispatch(handleError(e)));
}

export const sendBulk = (bulk: Bulk): AppThunk => async (
    dispatch,
    getState,
) => {

    const BACKEND_BASE = selectBackendBase(getState());
    dispatch(setSendingEmail(true));

    request(new URL(bulk.name + ":send", BACKEND_BASE), 'POST')
        .then(r => {
            dispatch(showEmailPreviewBulkView(false));
        })
        .catch(e => dispatch(handleError(e)))
        .finally(() => dispatch(setSendingEmail(false)));
}

export const getBulkPDFs = (bulk: Bulk): AppThunk => async (
    dispatch,
    getState,
) => {

    const BACKEND_BASE = selectBackendBase(getState());

    request(new URL(bulk.name + ":generate", BACKEND_BASE), 'POST')
        .then(r => {
            console.log("hello");
        })
        .catch(e => dispatch(handleError(e)));
}

export const selectBulks = (state: RootState) => state.bulk.items;
export const selectSelectedBulk = (state: RootState) => state.bulk.selected;
export const selectShowCreateBulkView = (state: RootState) => state.bulk.showCreateBulkView;
export const selectShowUpdateBulkView = (state: RootState) => state.bulk.showUpdateBulkView;
export const selectEmailPreviewBulkView = (state: RootState) => state.bulk.showEmailPreviewBulkView;
export const selectIsSendingBulk = (state: RootState) => state.bulk.sendingEmail;

export { showCreateBulkView, showUpdateBulkView, showEmailPreviewBulkView, deselectBulk };

export default bulkSlice.reducer;
