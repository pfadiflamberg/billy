import {createSlice, PayloadAction} from "@reduxjs/toolkit";
import {AppThunk, RootState} from "../../app/store";
import {handleError} from "../error/errorSlice";
import {selectBackendBase} from "../backend/backendSlice";

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
        createNewBulk: (state) => {
            state.showCreateBulkView = true;
        }
    }
})

const { setBulks, createNewBulk } = bulkSlice.actions;

export const fetchBulks = (): AppThunk => async (
    dispatch,
    getState
) => {
    fetch([selectBackendBase(getState()), API_PATH_BULK].join('/'))
        .then(response => {
            console.log(response)
            console.log(response.json())
            console.log('todo: add to store')
            // let bulks: Bulk[];
            // setBulks(bulks);
        })
        .catch(e => handleError(e))
}

export const storeNewBulk = (newBulk: Bulk): AppThunk => async (
    dispatch,
    getState
) => {
    console.log(newBulk)
}

export const selectBulks = (state: RootState) => state.bulk.items;
export const selectShowCreateBulkView = (state: RootState) => state.bulk.showCreateBulkView;

export { createNewBulk };

export default bulkSlice.reducer;