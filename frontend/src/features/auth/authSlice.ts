import {createSlice} from "@reduxjs/toolkit";
import {RootState} from "../../app/store";

interface AuthState {
    authenticated: boolean;
}

const initialState: AuthState = {
    authenticated: true
}

const authSlice = createSlice({
    name: 'auth',
    initialState,
    reducers: {
        unauthenticated: (state) => {
            state.authenticated = false;
        }
    }
})

const { unauthenticated } = authSlice.actions;

export { unauthenticated };

export const selectAuthenticatedState = (state: RootState) => state.auth.authenticated;

export default authSlice.reducer;