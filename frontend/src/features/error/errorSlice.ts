import {createSlice, PayloadAction} from "@reduxjs/toolkit";
import {RootState} from "../../app/store";

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

export const { addError } = errorSlice.actions;

export const selectErrors = (state: RootState) => state.error.errors;

export default errorSlice.reducer;