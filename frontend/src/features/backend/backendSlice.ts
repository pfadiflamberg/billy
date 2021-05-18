import { createSlice } from "@reduxjs/toolkit"
import {RootState} from "../../app/store";

export interface BackendState {
    url: string;
}

const initialState: BackendState = {
    url: 'https://api.billy.flamberg.ch'
}

export const backendSlice = createSlice({
    name: 'backend',
    initialState,
    reducers: {
        selfConfigure: (state) => {
            // if the frontend is served from localhost, we expect the backend to be on localhost
            const isLocalhost = Boolean(
                window.location.hostname === 'localhost' ||
                  // [::1] is the IPv6 localhost address.
                  window.location.hostname === '[::1]' ||
                  // 127.0.0.0/8 are considered localhost for IPv4.
                  window.location.hostname.match(
                    /^127(?:\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}$/
                  )
            );
            if (isLocalhost) {
                state.url = 'http://localhost:5000'
            }
        }
    }
})

export const { selfConfigure } = backendSlice.actions;

export const selectBackendURL = (state: RootState) => state.backend.url;

export default backendSlice.reducer;