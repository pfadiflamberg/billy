# Billy

## Run with Docker

### Setup

To access hitobito you need to provide some environment variables in the `env/hitobito.env` file, like so:

```txt
HITOBITO_EMAIL=pfnörch@flamberg.ch
HITOBITO_TOKEN=*******************
HITOBITO_SERVER=https://db.scout.ch
HITOBITO_LANG=de -- one of: de, fr, it
```

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

MAIL_TEST_RECIPIENT=testrecipient@examplemailerver.org
```

The last variable is only used during testing, when you don't want to send emails to real people.


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

This will generate all pending invoices as pdf and return a link to download them.

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

This will generate the invoices as pdf and return a link to download it.

#### TODO:
- [ ] Create Frontend
- [ ] make sure we don't run as root