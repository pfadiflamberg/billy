import {useAppSelector} from "../../app/hooks";
import {selectBackendURL} from "../../features/backend/backendSlice";

export function useBackendURL(): string {
    return useAppSelector(selectBackendURL);
}

export function useBackendAPI(path: string): string {
    return new URL(path, useBackendURL()).toString();
}