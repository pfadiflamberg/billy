import { Popup } from "../features/popup/popupSlice";

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
        const err = data as Popup;
        throw err;
    }
    return data;
}

// will execute the request but only return an error if one occurs and no result
export async function checkRequest(url: URL, method: string = 'GET', payload: any = null) {
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
    if (response.status !== 200 && response.status !== 201 ) {
        const data = await response.json();
        const err = data as Popup;
        throw err;
    }
}