import { BillyError } from "../features/error/errorSlice";

export async function request(url: URL, method: string = 'GET', payload: any = null): Promise<JSON> {
    const response = await fetch(url.toString(), {
        method: method,
        credentials: "include",
        headers: {
            'Accept': '*/*',
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        },
        body: (payload == null) ? null : JSON.stringify(payload)
    })
    const data = await response.json();
    if (response.status !== 200 && response.status !== 201 ) {
        const err = data as BillyError;
        throw err;
    }
    return data;
}