import {createSlice} from "@reduxjs/toolkit";

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

