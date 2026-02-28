# FamilySearch API Quick Reference

## Base URLs

| Environment   | URL                                       |
| ------------- | ----------------------------------------- |
| Integration   | `https://integration.familysearch.org`    |
| Production    | `https://api.familysearch.org`            |

## Authentication

All requests require an `Authorization` header:

```
Authorization: Bearer {access_token}
```

Tokens expire after **2 hours**. Use the refresh token to get a new access token without re-authenticating.

### OAuth2 Endpoints

| Endpoint          | URL                                                    |
| ----------------- | ------------------------------------------------------ |
| Authorization     | `{base}/cis-web/oauth2/v3/authorization`               |
| Token             | `{base}/cis-web/oauth2/v3/token`                       |

### Token Request (Authorization Code Grant)

```
POST /cis-web/oauth2/v3/token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code
&code={auth_code}
&client_id={app_key}
&redirect_uri={redirect_uri}
```

### Token Refresh

```
POST /cis-web/oauth2/v3/token
Content-Type: application/x-www-form-urlencoded

grant_type=refresh_token
&refresh_token={refresh_token}
&client_id={app_key}
```

## Content Types

| Type                                    | Usage                              |
| --------------------------------------- | ---------------------------------- |
| `application/x-gedcomx-v1+json`        | Person, relationship, source data  |
| `application/x-gedcomx-atom+json`      | Search results                     |
| `application/json`                      | General responses                  |

Request header:

```
Accept: application/x-gedcomx-v1+json
```

## Person ID Format

Person IDs follow the pattern `XXXX-XXX` (e.g., `KWCJ-RN4`). These are globally unique within FamilySearch.

## Core Endpoints

### Identity

| Method | Endpoint                                    | Description              |
| ------ | ------------------------------------------- | ------------------------ |
| GET    | `/platform/tree/current-person`             | Current user's person    |
| GET    | `/platform/users/current`                   | Current user profile     |

### Persons

| Method | Endpoint                                    | Description                        |
| ------ | ------------------------------------------- | ---------------------------------- |
| GET    | `/platform/tree/persons/{pid}`              | Read person (names, facts, gender) |
| GET    | `/platform/tree/persons/{pid}?relatives`    | Person + immediate family          |

### Pedigree

| Method | Endpoint                                         | Description                       |
| ------ | ------------------------------------------------ | --------------------------------- |
| GET    | `/platform/tree/ancestry?person={pid}`           | Ascending pedigree (ancestors)    |
| GET    | `/platform/tree/descendancy?person={pid}`        | Descending pedigree (descendants) |

Query parameters:
- `generations` — number of generations (default 4, max 8 for ancestry)
- `personDetails` — include full person details (default false)

### Search

| Method | Endpoint                                    | Description              |
| ------ | ------------------------------------------- | ------------------------ |
| GET    | `/platform/tree/search`                     | Search persons in tree   |

Query parameters (prefix Q to embed in `q` param):
- `givenName:{name}` — given name
- `surname:{name}` — surname
- `birthDate:{year}` — birth year (+/- range)
- `birthPlace:{place}` — birth place
- `deathDate:{year}` — death year
- `deathPlace:{place}` — death place
- `sex:{M|F}` — sex filter

Example:

```
GET /platform/tree/search?q=givenName:George+surname:Goodman+birthDate:1870~+birthPlace:Arizona
```

### Relationships

| Method | Endpoint                                              | Description              |
| ------ | ----------------------------------------------------- | ------------------------ |
| GET    | `/platform/tree/persons/{pid}/parents`                | Parents of a person      |
| GET    | `/platform/tree/persons/{pid}/spouses`                | Spouses of a person      |
| GET    | `/platform/tree/persons/{pid}/children`               | Children of a person     |
| GET    | `/platform/tree/path?from={pid1}&to={pid2}`          | Relationship path        |

### Sources

| Method | Endpoint                                              | Description                |
| ------ | ----------------------------------------------------- | -------------------------- |
| GET    | `/platform/tree/persons/{pid}/sources`                | Sources attached to person |

### Memories

| Method | Endpoint                                              | Description                 |
| ------ | ----------------------------------------------------- | --------------------------- |
| GET    | `/platform/tree/persons/{pid}/memories`               | Memories for a person       |
| GET    | `/platform/memories/memories/{mid}`                   | Read a specific memory      |

### Matches / Hints

| Method | Endpoint                                              | Description                |
| ------ | ----------------------------------------------------- | -------------------------- |
| GET    | `/platform/tree/persons/{pid}/matches`                | Research hints for person  |

## Rate Limiting

FamilySearch enforces rate limits per app key. Typical thresholds:
- **Reads**: ~1000 requests/minute
- **Searches**: ~100 requests/minute

The API returns `429 Too Many Requests` when throttled. Retry after the `Retry-After` header value (seconds).

## Error Responses

| Status | Meaning                                                |
| ------ | ------------------------------------------------------ |
| 401    | Token expired or invalid — re-authenticate             |
| 403    | App key not authorized for this environment/endpoint   |
| 404    | Person/resource not found                              |
| 429    | Rate limited — wait and retry                          |
| 503    | FamilySearch service temporarily unavailable           |

## GEDCOM X Data Model

The API uses the [GEDCOM X](https://github.com/FamilySearch/gedcomx) data model:

- **Person**: Has `names[]`, `gender`, `facts[]` (birth, death, etc.)
- **Name**: Has `nameForms[]`, each with `fullText`, `parts[]`
- **Fact**: Has `type` (URI like `http://gedcomx.org/Birth`), `date`, `place`
- **Relationship**: Connects two persons with a `type` (couple, parent-child)
- **SourceDescription**: Citation with `titles[]`, `citations[]`, `about` URI

Common fact type URIs:

| URI                                  | Meaning    |
| ------------------------------------ | ---------- |
| `http://gedcomx.org/Birth`           | Birth      |
| `http://gedcomx.org/Death`           | Death      |
| `http://gedcomx.org/Marriage`        | Marriage   |
| `http://gedcomx.org/Burial`          | Burial     |
| `http://gedcomx.org/Residence`       | Residence  |
| `http://gedcomx.org/Immigration`     | Immigration|
| `http://gedcomx.org/Naturalization`  | Naturalization |
| `http://gedcomx.org/MilitaryService` | Military   |
| `http://gedcomx.org/Occupation`      | Occupation |
