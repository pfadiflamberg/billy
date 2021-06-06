import {createSlice, PayloadAction} from "@reduxjs/toolkit";
import {AppThunk, RootState} from "../../app/store";
import { unauthenticated } from "../auth/authSlice";

interface ErrorState {
    errors: Error[];
}

const initialState: ErrorState = {
    errors: []
}

export const errorSlice = createSlice({
    name: 'error',
    initialState,
    reducers: {
        addError: (state, action: PayloadAction<Error>) => {
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
    if (error instanceof Error) {
    } else if (typeof error === 'string' || error instanceof String) {
        error = new Error(error.toString())
    } else {
        // unexpected error type
        throw(error);
    }
    console.log(error.toString());
    if (error.toString() === 'Error: Unauthorized') {
        dispatch(unauthenticated());
        return
    }
    dispatch(addError(error));
}

export { clearErrors };

export const selectErrors = (state: RootState) => state.error.errors;

export default errorSlice.reducer;