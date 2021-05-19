# Billy

## Run with Docker

### Setup

To access hitobito you need to provide some environment variables in the `env/hitobito.env` file, like so:

```txt
HITOBITO_EMAIL=pfnörch@flamberg.ch
HITOBITO_TOKEN=*******************
HITOBITO_SERVER=https://db.scout.ch
HITOBITO_LANG=de -- one of: de, fr, it
HITOBITO_SENDER=1234
```
`HITOBITO_SENDER` is the personal number of the person who will be the sender of the invoice, and is only used for testing when not provided by auth token.

You can generate or lookup your toke using `curl`:

```bash
curl -d "person[email]=pfnörch@flamberg.ch" \
     -d "person[password]=****************" \
     https://db.scout.ch/users/sign_in.json
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
| group | The group (and its children) that are added as recipients. |         | yes |

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
  list: [
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

```
POST /bulk/<id>:generate
```

This will generate all pending invoices as pdf and return a a zip file containing all of them.

### Invoice

#### Get

```
GET /bulk/<id>/invoices/<id>
```

#### Put

```
GET /bulk/<id>/invoices/<id>
```

Update an indivual invoice.

| Name  | Description | Example | Required |
|-------|-------------|---------|----------|
| status | Update the status of the invoice. | paid, annulled | no |
| status_message | Add a status message. (should not be used yet) | | no |

#### List

```
GET /bulk/<id>/invoices
```

This will return a list of invoice resources that are associated with a bulk:

```json
{
  list: [
    ...
  ]
}
```

#### Generate

```
POST /bulk/<id>/invocies/<id>:generate
```

This will generate the invoices as pdf and return it.

#### TODO:
- [ ] Create Frontend
- [ ] make sure we don't run as root