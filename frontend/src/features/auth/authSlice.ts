import {createSlice} from "@reduxjs/toolkit";
import {RootState} from "../../app/store";

interface AuthState {
    authenticated: boolean;
}

const initialState: AuthState = {
    authenticated: false
}

const authSlice = createSlice({
    name: 'auth',
    initialState,
    reducers: {

    }
})

export const selectAuthenticatedState = (state: RootState) => state.auth.authenticated;

export default authSlice.reducer;