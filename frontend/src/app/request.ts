
interface ErrorResponse {
    code: number,
    message: string
}

export async function request(url: URL, method: string, payload?: any): Promise<JSON> {
    const response = await fetch(url.toString(), {
        method: method,
        headers: {
            'Accept': '*/*',
            'Content-Type': 'application/json'
        },
        body: (payload == null) ? null : JSON.stringify(payload)
    })
    const data = await response.json();
    if (!(response.status in [200, 201])) {
        const err = data as ErrorResponse;
        throw new Error(err.message);
    }
    return data;
}