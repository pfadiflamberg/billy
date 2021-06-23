import {createSlice, PayloadAction} from "@reduxjs/toolkit";
import {AppThunk, RootState} from "../../app/store";
import {handleError} from "../error/errorSlice";
import {selectBackendBase} from "../backend/backendSlice";
import { request } from "../../app/request";

const API_PATH_BULK = 'bulk'

export type Bulk = {
    name: string,
    display_name: string,
    status: string,
    update_time: string,
    mailing_list: string,
    text_mail: string,
    text_invoice: string,
    text_reminder: string,
}

export type BulkDict = {
    [Key: string]: Bulk
}

export interface BulkState {
    items: BulkDict;
    selected: string,
    showCreateBulkView: boolean;
    showUpdateBulkView: boolean;
}

const initialState: BulkState = {
    items: {},
    selected: '',
    showCreateBulkView: false,
    showUpdateBulkView: false,
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
            if (!payload) {
                window.history.replaceState({}, "", window.location.origin);
            }
        },
        selectBulk: (state, { payload }: PayloadAction<string>) => {
            state.selected = payload;
            window.history.replaceState({}, "", payload);
        },
    }
})

const { setBulks, setBulk, showCreateBulkView, showUpdateBulkView, selectBulk } = bulkSlice.actions;

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
            dispatch(selectBulk(bulk.name));
        })
        .catch(e => dispatch(handleError(e)));
}

export const updateBulk = (bulk: Bulk): AppThunk => async (
    dispatch,
    getState
) => {

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
    var new_title = org_bulk.display_name.replace((year-1).toString(), year.toString());
    if (new_title === org_bulk.display_name) {
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
            new_bulk.display_name = new_empty_bulk.display_name;
            new_bulk.status = new_empty_bulk.status;
            request(new URL(org_bulk.name, BACKEND_BASE), 'PUT', new_bulk);
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

export const getBulkPDFs = (bulk: Bulk): AppThunk => async (
    dispatch,
    getState,
) => {

    const BACKEND_BASE = selectBackendBase(getState());

    request(new URL(bulk.name + ":generate", BACKEND_BASE), 'POST')
        .then(r => {

        })
        .catch(e => dispatch(handleError(e)));
}

export const selectBulks = (state: RootState) => state.bulk.items;
export const selectSelectedBulk = (state: RootState) => state.bulk.selected;
export const selectShowCreateBulkView = (state: RootState) => state.bulk.showCreateBulkView;
export const selectShowUpdateBulkView = (state: RootState) => state.bulk.showUpdateBulkView;

export { showCreateBulkView, showUpdateBulkView, selectBulk };

export default bulkSlice.reducer;
