import React from "react";
import {selectBackendBase} from "../backend/backendSlice";
import {useAppSelector} from "../../app/hooks";

export function AuthView() {

    const BACKEND_BASE = useAppSelector(selectBackendBase);

    console.log(BACKEND_BASE)

    return (
        <button onClick={e => window.location.replace(new URL('oauth/login', BACKEND_BASE).toString())}>Login</button>
    )

}