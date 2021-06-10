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
    text_invoice: string,
    text_reminder: string,
    text_mail: string,
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
        },
        selectBulk: (state, { payload }: PayloadAction<string>) => {
            state.selected = payload;
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

export const duplicateBulk = (orgBulk: Bulk): AppThunk => async (
    dispatch,
    getState
) => {

    const BACKEND_BASE = selectBackendBase(getState());

    // create new title (if possible change year)
    var year: number = new Date().getFullYear()
    var newTitle = orgBulk.display_name.replace((year-1).toString(), year.toString());
    if (newTitle === orgBulk.display_name) {
        newTitle += ' (copy)';
    }

    var createBulkForm = {
        'title': newTitle,
    };

    request(new URL(API_PATH_BULK, BACKEND_BASE), 'POST', createBulkForm)
        .then(r => {
            console.log('created')
            var newEmptyBulk: Bulk = r as unknown as Bulk;
            var newBulk = JSON.parse(JSON.stringify(orgBulk));
            newBulk.name = newEmptyBulk.name;
            newBulk.display_name = newEmptyBulk.display_name;
            request(new URL(orgBulk.name, BACKEND_BASE), 'PUT', newBulk);
            dispatch(setBulk(newBulk));
        })
        .catch(e => dispatch(handleError(e)));
}

export const selectBulks = (state: RootState) => state.bulk.items;
export const selectSelectedBulk = (state: RootState) => state.bulk.selected;
export const selectShowCreateBulkView = (state: RootState) => state.bulk.showCreateBulkView;
export const selectShowUpdateBulkView = (state: RootState) => state.bulk.showUpdateBulkView;

export { showCreateBulkView, showUpdateBulkView, selectBulk };

export default bulkSlice.reducer;
