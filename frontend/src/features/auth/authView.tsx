import React from "react";
import {selectBackendBase} from "../backend/backendSlice";
import {useAppSelector} from "../../app/hooks";

export function AuthView() {

    const BACKEND_BASE = useAppSelector(selectBackendBase);

    function redirect2Auth() {
        const url = new URL('oauth/login', BACKEND_BASE);
        window.location.replace(url.toString());
    }

    redirect2Auth();

    return (
        <div></div>
        // nice for debugging <button onClick={e => redirect2Auth()}>Login</button>
    )

}