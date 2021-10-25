import {createSlice, PayloadAction} from "@reduxjs/toolkit";
import {AppThunk, RootState} from "../../app/store";
import { unauthenticated } from "../auth/authSlice";

export type PopupAction = {
    label: string,
    func: (dispatch: any) => void,
}

export type Popup = {
    title: string,
    description: string,
    details: any,
    details_type: string,
    link: string,
    action: PopupAction,
}

interface ErrorState {
    popups: Popup[];
}

const initialState: ErrorState = {
    popups: []
}

export const popupSlice = createSlice({
    name: 'popup',
    initialState,
    reducers: {
        newPopup: (state, action: PayloadAction<Popup>) => {
            state.popups.push(action.payload);
        },
        clearPopups: (state) => {
            state.popups = []
        }
    }
})

const { newPopup, clearPopups } = popupSlice.actions;

export const handleError = (error: any): AppThunk => async (
    dispatch
) => {
    if (error.message) {
        error = {title: 'Error', description: error.message};
    }
    if (error.description === 'Unauthorized') {
        dispatch(unauthenticated());
        return
    }
    dispatch(newPopup(error));
}

export { newPopup, clearPopups };

export const selectPopups = (state: RootState) => state.popup.popups;

export default popupSlice.reducer;