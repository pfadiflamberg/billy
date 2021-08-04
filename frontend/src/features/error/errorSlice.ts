import {createSlice, PayloadAction} from "@reduxjs/toolkit";
import {AppThunk, RootState} from "../../app/store";
import { unauthenticated } from "../auth/authSlice";

export type BillyError = {
    title: string,
    description: string,
    details: any,
    link: string,
}

interface ErrorState {
    errors: BillyError[];
}

const initialState: ErrorState = {
    errors: []
}

export const errorSlice = createSlice({
    name: 'error',
    initialState,
    reducers: {
        addError: (state, action: PayloadAction<BillyError>) => {
            state.errors.push(action.payload);
        },
        clearErrors: (state) => {
            state.errors = []
        }
    }
})

const { addError, clearErrors } = errorSlice.actions;

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
    dispatch(addError(error));
}

export { clearErrors };

export const selectErrors = (state: RootState) => state.error.errors;

export default errorSlice.reducer;