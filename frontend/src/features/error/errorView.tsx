import {useAppSelector} from "../../app/hooks";
import {selectErrors} from "./errorSlice";
import React from "react";

export function ErrorView() {

    const errors = useAppSelector(selectErrors);

    if (errors.length) {
        return (
            <div>Error: {errors[0].message}</div>
        )
    } else {
        return (
            <div></div>
        )
    }

}