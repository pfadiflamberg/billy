
const AUTH_BASE = 'https://pbs.puzzle.ch'
const CLIENT_ID = '0FS55nbQMphZsDu1nBZQFnuIOclc6ORR7dYYEzvyZjU'

export function AuthView() {

    // TODO: check if authenticated
    if (window.location.hash) {
        let groups = window.location.hash.match('access_token=(?<access_token>[^&]+)')?.groups;
        console.log(groups?.access_token);
    }

    const AUTH_URL = AUTH_BASE + '/oauth/authorize?' +
        ['client_id=' + CLIENT_ID,
            '&redirect_uri=' + window.location.origin + '/oauth/callback',
            'response_type=' + ['code'].join('%20'),
            'scope=' + ['email', 'with_roles', 'api'].join('%20'),
        ].join('&');

    return (
        <button onClick={e => window.location.replace(AUTH_URL)}>Login</button>
    )

}