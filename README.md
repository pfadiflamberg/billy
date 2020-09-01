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

#### Run with Docker-Compose

Run: `docker-compose up`