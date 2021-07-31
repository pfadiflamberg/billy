# Billy

## Run with Docker

### Setup

For user authentication and to access hitobito the app needs to be registered as an oauth application on hitobito. The application needs all available scopes and a callback URL (REDIRECT_URL_LOGIN) of the following form `API_SERVER/oauth/billy/authorized` (e.g. `http://localhost:5000/oauth/billy/authorized `).

In `env/hitobito.env` the following variables need to be defined:

```text
HITOBITO_OAUTH_CLIENT_ID=0FS55nbQMphZsDu1nBZQFnuIOclc6ORR7dYYEzvyZjU
HITOBITO_OAUTH_SECRET=U1WMfNWXMMsFUwNHqylu9r0HQK1Z0pxCnorJwLRvjWo
HITOBITO_HOST=https://pbs.puzzle.ch
HITOBITO_LANG=de -- one of: de, fr, it
HITOBITO_GROUP=1 -- the group allowed to login to the application

-- the following environment variables are required until pbs.scout.ch will support the API scope
HITOBITO_ALLOWED_USERS=2 -- list of users allowed to access the application
HITOBITO_TOKEN_USER=hussein_kohlmann@hitobito.example.com
HITOBITO_TOKEN=Tu7aVJWyLYYMyCnZv2bz -- test system token
```

#### Hitobito API Token

Until the `api` scope is supported by `db.scout.ch` a API access token and user needs to be provided. (Users are required as an additional level of security - as users don't use their own token).

```
curl -X POST --data "person[email]=<USERNAME>&person[password]=<PASSWORD>" https://db.scout.ch/de/users/sign_in.json
```

For the test system:
```
curl -X POST --data "person[email]=hussein_kohlmann@hitobito.example.com&person[password]=hito42bito" https://pbs.puzzle.ch/de/users/sign_in.json
```

In `env/server.env` the following variables need to be defined:

```
CLIENT_ORIGIN=http://localhost:3000
REDIRECT_URL_LOGIN=http://localhost:3000
```

To run locally you must add the following environment variable as well:
```
OAUTHLIB_INSECURE_TRANSPORT=true
```

To use mail functionality, you need to provide the server details for the mail server in `env/mail.env`:

```txt
MAIL_SERVER=mail.examplemailserver.org --smtp address
MAIL_PORT=25 --smpt port
MAIL_USE_TLS=0 --0 or 1
MAIL_USE_SSL=1 --0 or 1
MAIL_USERNAME=exampleaddress@examplemailserver.org
MAIL_DEFAULT_SENDER=exampleaddress@examplemailserver.org
MAIL_PASSWORD=***********
```
For the banking functionality, the enivronment variables need to be set, either via `.env/bank.env` or via docker-compose.yml:

```txt
BANK_IBAN=CH40...
BANK_REF_PREFIX=123456
```

### Run with NGINX

To deploy billy you need to run it behind a proxy to add TLS. To make sure the API magic works your conf file should look something like this:

```
# redirect https to the frontend
server {

  server_name billy.flamberg.ch; # managed by Certbot

	location / {
		proxy_pass http://127.0.0.1:3000/;
	}

  listen [::]:443 ssl ipv6only=on; # managed by Certbot
  listen 443 ssl; # managed by Certbot
  # ssl stuff by Certbot...
}

# redirect api port to api
server {
    server_name billy.flamberg.ch; # managed by Certbot

    location / {
		proxy_pass http://127.0.0.1:5000/;

		proxy_set_header Host $host:1921;
		proxy_set_header X-Forwarded-Proto https;
	}

  listen [::]:1921 ssl ipv6only=on; # managed by Certbot
  listen 1921 ssl; # managed by Certbot
  # ssl stuff by Certbot...
}
```

### Data

All data stored in the database are volume mapped inside `./var/mysql`. If you like to remove all data you can simply delete this directory.

#### Run with Docker-Compose

Run: `docker compose --profile billy up`

The following profiles are available:
- billy: run the complete application
- backend: run the backend (db + server)
- db: to only run the db
- frontend: run only the frontend
- migrations: to create new **migrations** (see documentation)


## Resources


### Bulk Invoice

```json
{
  "name": "bulk/<id>",
  "issuing_date": "2020-06-023T00:00:00.000Z",
  "due_date": "2020-07-30T00:00:00.000Z",
  "display_name" : "...",
  "text_invoice": "...",
  "text_reminder": "...",
}
```

## Requests

### Bulk Invoice

#### Create

```
POST /bulk
```

Create a new bulk invoice.

| Name         | Description                                                            | Example                                               | Required |
| ------------ | ---------------------------------------------------------------------- | ----------------------------------------------------- | -------- |
| title        | A title for the bulk invoice.                                          | Membership 2021                                       | yes      |
| mailing_list | The url of the mailing list whose subscribers are added as recipients. | https://db.scout.ch/de/groups/1147/mailing_lists/3518 | yes      |

#### Get

```
GET /bulk/<id>
```

This will return the bulk invoice resource.

#### List

```
GET /bulk/
```

This will return a list of bulk invoice resources:

```json
{
  "items": [
    ...
  ]
}
```

#### Update

```
PUT /bulk/<id>
```

| Name          | Description              | Example | Required |
| ------------- | ------------------------ | ------- | -------- |
| text_invoice  | The text of the invoice. |         | no       |
| text_reminder | The text of the invoice. |         | no       |

This will return the updated bulk invoice resource.

#### Issue

```
POST /bulk/<id>:issue
```

#### Close

```
POST /bulk/<id>:close
```

#### Send

```
POST /bulk/<id>:send
```

This will send all pending invoices of this bulk via email.

#### Generate
****
```
POST /bulk/<id>:generate
```

This will generate all pending invoices as pdf and return a a zip file containing all of them.

### Invoice

#### Get

```
GET /bulk/<id>/invoice/<id>
```

#### Put

```
GET /bulk/<id>/invoice/<id>
```

Update an indivual invoice.

| Name           | Description                                    | Example        | Required |
| -------------- | ---------------------------------------------- | -------------- | -------- |
| status         | Update the status of the invoice.              | paid, annulled | no       |
| status_message | Add a status message. (should not be used yet) |                | no       |

#### List

```
GET /bulk/<id>/invoice
```

This will return a list of invoice resources that are associated with a bulk:

```json
{
  "items": [
    ...
  ]
}
```

#### Generate

```
GET /bulk/<id>/invoice/<id>.pdf
```

This will generate the invoices as pdf and return it.

## Development


### Migrations

When the model in `model.py` has been changed, an alembic
revision script must be generated to upgrade the database accordingly. This is done as follows:

1. Run `docker-compose --profile migration up`

2. Inside the container `billy-migration`, run the command `alembic revision
   --autogenerate -m "message"`, where "message" should be a short description
   of the changes.  This can be done either by attaching a shell to the
   container or running the following command on the host: `docker container
   exec -it billy-migration alembic revision --autogenerate -m "message"`

   This will have created a new revision inside the folder `migrations/versions`.
   This revision is automatically copied to the host machine, and you can stop
   the containers now and do the following steps on the host.

3. Manually check the newly created revision: Some changes cannot automatically
   be detected by alembic, see the
   [documentation](https://alembic.sqlalchemy.org/en/latest/autogenerate.html#what-does-autogenerate-detect-and-what-does-it-not-detect).
   Fix any issues you discover.

4. Done. Rebuild the container with `docker-compose up --build`, and the new
   revision will automatically be applied before the first request is answered.