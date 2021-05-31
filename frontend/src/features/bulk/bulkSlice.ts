import {createSlice, PayloadAction} from "@reduxjs/toolkit";
import {AppThunk, RootState} from "../../app/store";
import {handleError} from "../error/errorSlice";
import {selectBackendBase} from "../backend/backendSlice";
import { request } from "../../app/request";
import { unauthenticated } from "../auth/authSlice";

const API_PATH_BULK = 'bulk'

export type Bulk = {
    name: string
}

export type BulkDict = {
    [Key: string]: Bulk
}

export interface BulkState {
    items: BulkDict;
    showCreateBulkView: boolean;
}

const initialState: BulkState = {
    items: {},
    showCreateBulkView: false,
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
        showCreateBulkView: (state, { payload }: PayloadAction<boolean>) => {
            state.showCreateBulkView = payload;
        },
    }
})

const { setBulks, showCreateBulkView } = bulkSlice.actions;

export const fetchBulks = (): AppThunk => async (
    dispatch,
    getState
) => {

    const BACKEND_BASE = selectBackendBase(getState());

    // request(new URL('bulk', BACKEND_BASE), 'GET', null)
    // .catch(e => dispatch(handleError(e)));
    fetch(new URL(API_PATH_BULK, BACKEND_BASE).toString(), {
        credentials: "include",
        headers: {
            'Access-Control-Allow-Origin': '*', // TODO: make this dynamic
        }
    })
        .then(response => {
            if (response.status == 401) {
                dispatch(unauthenticated());
            }
            // catchErrors(r);
            console.log(response);
            console.log(response.json());
            console.log('todo: add to store');
            // let bulks: Bulk[];
            // setBulks(bulks);
        })
        .catch(e => dispatch(handleError(e)))
}

export const storeNewBulk = (newBulk: Bulk): AppThunk => async (
    dispatch,
    getState
) => {
    console.log(newBulk)
}

export const selectBulks = (state: RootState) => state.bulk.items;
export const selectShowCreateBulkView = (state: RootState) => state.bulk.showCreateBulkView;

export { showCreateBulkView };

export default bulkSlice.reducer;
