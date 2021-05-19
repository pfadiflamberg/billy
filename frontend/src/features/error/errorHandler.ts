import {addError} from "./errorSlice";
import {AppDispatch} from "../../app/store";

export function handleError(dispatch: AppDispatch, error: any) {
    // TODO: catch auth errors
    console.log('handleError called')
    if (error instanceof Error) {
        console.log('with error')
    } else if (typeof error === 'string' || error instanceof String) {
        console.log('with string')
        error = new Error(error.toString())
    } else {
        console.log('with something else ARGGGG!!!!')
        // unexpected error type
        throw(error);
    }
    dispatch(addError(error));
}