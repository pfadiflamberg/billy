# Billy

## Run with Docker

### Setup

For user authentication and to access hitobito the app needs to be registered as an oauth application on hitobito. The application needs all available scopes and a callback URL of the following form `API_SERVER/oauth/billy/authorized` (e.g. `http://localhost:5000/oauth/billy/authorized `).
The configurations need to be stored in the `env/hitobito.env` file as follows:
```text
HITOBITO_OAUTH_CLIENT_ID=0FS55nbQMphZsDu1nBZQFnuIOclc6ORR7dYYEzvyZjU
HITOBITO_OAUTH_SECRET=U1WMfNWXMMsFUwNHqylu9r0HQK1Z0pxCnorJwLRvjWo
HITOBITO_HOST=https://pbs.puzzle.ch
HITOBITO_LANG=de -- one of: de, fr, it
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


#### Run with Docker-Compose

Run: `docker-compose up`

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

## Requets

### Bulk Invoice

#### Create

```
POST /bulk
```

Create a new bulk invoice.

| Name  | Description | Example | Required |
|-------|-------------|---------|----------|
| title | A title for the bulk invoice. | Membership 2021        | yes |
| mailing_list | The url of the mailing list whose subscribers are added as recipients. | https://db.scout.ch/de/groups/1147/mailing_lists/3518 | yes |

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

| Name  | Description | Example | Required |
|-------|-------------|---------|----------|
| text_invoice | The text of the invoice. |         | no |
| text_reminder | The text of the invoice. |         | no |

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

| Name  | Description | Example | Required |
|-------|-------------|---------|----------|
| status | Update the status of the invoice. | paid, annulled | no |
| status_message | Add a status message. (should not be used yet) | | no |

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
POST /bulk/<id>/invoice/<id>:generate
```

This will generate the invoices as pdf and return it.

#### TODO:
- [ ] Create Frontend
- [ ] make sure we don't run as root