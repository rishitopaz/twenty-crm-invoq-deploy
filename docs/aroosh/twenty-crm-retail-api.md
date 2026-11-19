# Twenty CRM (Retail) - API Documentation

**Prepared by:** Aroosh Ahmed, Topaz PS-II internship
**Date:** 5 November 2026 (updated 16 November 2026: sections 13 to 18 added)
**Environment:** self-hosted Twenty CRM (Docker Compose) at `http://localhost:3000`; from outside the laptop through a temporary tunnel address (section 18)

---

## 1. Overview

This document describes how to use the REST API of the Twenty CRM deployment configured for the **Retail** domain. It covers the building blocks that were set up. The first four were set up first; the last three rows were added later and are described in sections 13 to 18:

| Module | Twenty object | Type | REST endpoint |
|---|---|---|---|
| Contacts | People | Built-in, extended with retail fields | `/rest/people` |
| Accounts / Organizations | Companies | Built-in | `/rest/companies` |
| Ticketing | Tickets | **Custom object** created for Retail | `/rest/tickets` |
| Notes | Notes and Note Targets | Built-in | `/rest/notes`, `/rest/noteTargets` |
| Interactions | Interaction | **Custom object**: calls, emails and chats linked to tickets, contacts and agents | `/rest/interactions` |
| Service Requests | Service Request | **Custom object**: a generic ticket for any industry | `/rest/serviceRequests` |
| Category catalog | Catalog Entry | **Custom object**: sector, category and sub-category lists | `/rest/catalogEntries` |

Twenty generates the REST API automatically from the workspace data model. When the custom **Tickets** object was created, its `/rest/tickets` endpoint appeared without any extra coding.

**Test status labels used in this document**

- **Tested** means the call was run against this deployment and the sample output comes from a real response (trimmed for readability, and some ids and timestamps in them are illustrative).
- **Not yet tested** means the call follows the same pattern as the tested ones, but was not run in this deployment. Check it in the REST playground first (Settings → Developers → Launch).

---

## 2. Authentication

Every request needs an API key, sent as a Bearer token.

1. In Twenty, go to **Settings → Developers → API Keys → Create API key**.
2. Give it a name (for example `Retail CRM`), choose a role and an expiry.
3. Copy the key immediately. It is shown only once. If it is lost, regenerate it (the old key stops working).

Header on every request:

```
Authorization: Bearer <API_KEY>
```

In the examples below the key is stored in a shell variable:

```bash
export TWENTY_API_KEY="PASTE_KEY_HERE"
```

Notes:

- The key inherits the permissions of its role. Testing used an **Admin** role. For production, assign a least-privilege role (for example read-only for reporting systems).
- A missing or wrong key returns **401 Unauthorized** (or `403 Missing authentication token` when no key is sent at all).
- A key whose role does not allow a call returns `PERMISSION_DENIED` (section 17.3). A key given to another system should use a limited role (section 17.2).
- Never share the key or commit it to a file or repository.

---

## 3. Conventions

### 3.1 Base URL

```
http://localhost:3000/rest
```

From outside the laptop, use the temporary tunnel address instead of `http://localhost:3000` (section 18).

### 3.2 HTTP methods

| Method | Use |
|---|---|
| `GET /rest/{object}` | List or search records |
| `GET /rest/{object}/{id}` | Get one record by id |
| `POST /rest/{object}` | Create a record |
| `PATCH /rest/{object}/{id}` | Update only the fields sent |
| `DELETE /rest/{object}/{id}` | Delete a record (returns the deleted id) |

Requests with a body must send `Content-Type: application/json`.

### 3.3 Filtering

Format: `filter=field[comparator]:value`

| Comparator | Meaning |
|---|---|
| `eq`, `neq` | equals, not equal |
| `gt`, `gte`, `lt`, `lte` | greater than, greater or equal, less than, less or equal |
| `in` | value is in a list |
| `like`, `ilike`, `startsWith` | text matching |
| `is` | null checks |

- Fields made of parts use a dot: `emails.primaryEmail`, `phones.primaryPhoneNumber`.
- Combine conditions with `and(...)` or `or(...)`, for example:
  `filter=and(createdAt[gte]:"2026-10-27T00:00:00.000Z",createdAt[lt]:"2026-10-28T00:00:00.000Z")`
- When using `curl`, pass the filter with `-G --data-urlencode 'filter=...'` so the quotes and brackets are encoded.

For readable terminal output, see Appendix A.

### 3.4 Ordering

`order_by=createdAt[DescNullsLast]` returns the newest records first (tested). Without `order_by` the results are **not** in creation order, so always add `order_by` when the order matters.

### 3.5 Pagination

- `limit` sets the page size (maximum 60).
- Every list response includes `totalCount` and `pageInfo`.
- Use `starting_after=<endCursor>` for the next page and `ending_before=<startCursor>` for the previous page.

```json
"totalCount": 4,
"pageInfo": {
  "startCursor": "eyJpZCI6IjY0OGRiNTFh...",
  "endCursor": "eyJpZCI6IjY0OGRiNTFh...",
  "hasNextPage": true,
  "hasPreviousPage": false
}
```

Tested: a request with `limit=2` returned two tickets, and repeating it with `starting_after=<endCursor>` returned the next two. Treat the cursor as an opaque value (in these responses it is a base64-encoded record id). Without `order_by`, pages follow the record id, not the creation date.

### 3.6 Response shapes

| Operation | Shape |
|---|---|
| List | `{ "data": { "<plural>": [ ... ] }, "totalCount": n, "pageInfo": { ... } }` |
| Create | `{ "data": { "create<Object>": { ... } } }` |
| Update | `{ "data": { "update<Object>": { ... } } }` |
| Get one | `{ "data": { "<singular>": { ... } } }`, for example `data.person` |
| Delete | `{ "data": { "delete<Object>": { "id": "..." } } }` with HTTP 200 |

### 3.7 Value formats

- **Ids** are UUIDs.
- **Timestamps** are ISO 8601 in **UTC** (the trailing `Z`). Dubai is UTC+4, so a record created at 02:00 in Dubai carries the previous day's date in UTC. Date filters must use UTC.
- **Composite fields** are objects: `name`, `emails`, `phones`.
- **Select fields** use uppercase values with underscores (for example `IN_PROGRESS`), which differ from the labels shown in the UI. A select value can be filtered without quotes, for example `filter=sector[eq]:BANKING`.
- **Created by / Updated by** record who made the change, for example `"source": "MANUAL"` (UI) or `"source": "API"`.

---

## 4. Data model

```
Company (Account) 1 ────< Person (Contact) 1 ────< Ticket >──── 1 Company (Account)
                                                     │
                                                     └────< NoteTarget >──── Note
```

| Relation | Description |
|---|---|
| Person → Company | A contact belongs to one company (`companyId`) |
| Ticket → Person | A ticket belongs to one contact (`contactId`); a person has many tickets |
| Ticket → Company | A ticket belongs to one account (`accountId`); a company has many tickets |
| Note ↔ record | A note attaches to any record through a **note target** (`noteTargets`), so one note can attach to several records |

**Relations added after 5 November**

| Relation | Description |
|---|---|
| Ticket → Workspace Member | A ticket has one assignee (`assigneeId`) |
| Interaction → Ticket | An interaction belongs to one ticket (`ticketId`); a ticket lists its interactions |
| Interaction → Service Request | An interaction can belong to one service request (`serviceRequestId`) |
| Interaction → Person | The contact in the interaction (`contactId`) |
| Interaction → Workspace Member | The agent who handled it (`handledById`) |
| Service Request → Person | The contact (`contactId`) |
| Service Request → Company | The account (`accountId`) |
| Service Request → Workspace Member | The assignee (`assigneeId`) |
| Catalog Entry | Stands alone: it lists valid sector, category and sub-category combinations (section 15) |

---

## 5. Contacts (People)

**Endpoint:** `/rest/people`

### 5.1 Fields

| Field | Type | Notes |
|---|---|---|
| `id` | UUID | Generated |
| `name` | object | `{ "firstName": "...", "lastName": "..." }` |
| `emails` | object | `{ "primaryEmail": "...", "additionalEmails": [] }` |
| `phones` | object | `primaryPhoneNumber` (without country code), `primaryPhoneCountryCode` (e.g. `AE`), `primaryPhoneCallingCode` (e.g. `+971`), `additionalPhones` |
| `jobTitle` | text | |
| `companyId` | UUID | Link to the account |
| `loyaltyId` | text | **Custom.** Unique customer identifier used for lookups |
| `customerType` | select | **Custom.** `RETAIL`, `WHOLESALE`, `VIP` |
| `preferredChannel` | select | **Custom.** Preferred contact channel |
| `createdAt`, `updatedAt`, `deletedAt` | timestamp | UTC |
| `createdBy`, `updatedBy` | object | Who made the change |

### 5.2 Search a contact by email (Tested)

Request:

```bash
curl -s -G -H "Authorization: Bearer $TWENTY_API_KEY" \
  "http://localhost:3000/rest/people" \
  --data-urlencode 'filter=emails.primaryEmail[eq]:"fatima.khan@example.com"'
```

Response (trimmed: avatar, linkedinLink, position and searchVector omitted):

```json
{
  "data": {
    "people": [
      {
        "id": "3cf131cd-3a39-445f-96c8-925b4dbc51b4",
        "createdAt": "2026-10-27T11:37:53.789Z",
        "updatedAt": "2026-10-27T11:45:41.345Z",
        "deletedAt": null,
        "name": { "firstName": "Fatima", "lastName": "Khan" },
        "emails": { "primaryEmail": "fatima.khan@example.com", "additionalEmails": [] },
        "jobTitle": "",
        "phones": {
          "primaryPhoneNumber": "501112222",
          "primaryPhoneCountryCode": "AE",
          "primaryPhoneCallingCode": "+971",
          "additionalPhones": []
        },
        "createdBy": { "source": "MANUAL", "name": "Aroosh Ahmed" },
        "companyId": "b4da1657-30ab-4afc-ac60-b8a997b1613f",
        "loyaltyId": "LOY-1002",
        "customerType": "RETAIL",
        "preferredChannel": null
      }
    ]
  },
  "totalCount": 1,
  "pageInfo": {
    "startCursor": "eyJpZCI6IjNjZjEzMWNkLTNhMzktNDQ1Zi05NmM4LTkyNWI0ZGJjNTFiNCJ9",
    "endCursor": "eyJpZCI6IjNjZjEzMWNkLTNhMzktNDQ1Zi05NmM4LTkyNWI0ZGJjNTFiNCJ9",
    "hasNextPage": false,
    "hasPreviousPage": false
  }
}
```

If nothing matches, `people` is an empty list and `totalCount` is `0`.

### 5.3 Search a contact by phone (Tested)

The number is stored without the country code, so search for the number only.

```bash
curl -s -G -H "Authorization: Bearer $TWENTY_API_KEY" \
  "http://localhost:3000/rest/people" \
  --data-urlencode 'filter=phones.primaryPhoneNumber[eq]:"501112222"'
```

The response has the same shape as 5.2.

### 5.4 Search a contact by unique identifier (Tested)

The loyalty ID is the unique identifier used for lookups.

```bash
curl -s -G -H "Authorization: Bearer $TWENTY_API_KEY" \
  "http://localhost:3000/rest/people" \
  --data-urlencode 'filter=loyaltyId[eq]:"LOY-1002"'
```

The response has the same shape as 5.2.

### 5.5 Add a contact (Tested)

Request:

```bash
curl -s -X POST -H "Authorization: Bearer $TWENTY_API_KEY" \
  -H "Content-Type: application/json" \
  "http://localhost:3000/rest/people" -d '{
  "name": { "firstName": "Abby", "lastName": "Moore" },
  "emails": { "primaryEmail": "abby.moore@example.com" },
  "phones": {
    "primaryPhoneNumber": "508887777",
    "primaryPhoneCountryCode": "AE",
    "primaryPhoneCallingCode": "+971"
  },
  "loyaltyId": "LOY-1007",
  "customerType": "RETAIL"
}'
```

Response (trimmed):

```json
{
  "data": {
    "createPerson": {
      "id": "8d2c5b6a-4f1e-4c7a-9b3d-2e6f1a0c9d11",
      "createdAt": "2026-11-05T09:12:41.220Z",
      "updatedAt": "2026-11-05T09:12:41.220Z",
      "deletedAt": null,
      "name": { "firstName": "Abby", "lastName": "Moore" },
      "emails": { "primaryEmail": "abby.moore@example.com", "additionalEmails": [] },
      "phones": {
        "primaryPhoneNumber": "508887777",
        "primaryPhoneCountryCode": "AE",
        "primaryPhoneCallingCode": "+971",
        "additionalPhones": []
      },
      "createdBy": { "source": "API", "name": "Retail CRM" },
      "loyaltyId": "LOY-1007",
      "customerType": "RETAIL"
    }
  }
}
```

To avoid duplicates, search by email or loyalty ID before creating (duplicate prevention was not tested).

### 5.6 Update a contact (Tested)

Find the contact's id by searching (5.2), then send only the fields that change.

```bash
curl -s -X PATCH -H "Authorization: Bearer $TWENTY_API_KEY" \
  -H "Content-Type: application/json" \
  "http://localhost:3000/rest/people/<PERSON_ID>" \
  -d '{ "jobTitle": "Store Manager", "customerType": "VIP" }'
```

Response (trimmed):

```json
{
  "data": {
    "updatePerson": {
      "id": "52aaad0a-aaaf-4990-8d05-79fce6a9a914",
      "updatedAt": "2026-10-27T12:05:03.311Z",
      "name": { "firstName": "Noor", "lastName": "Saleh" },
      "jobTitle": "Store Manager",
      "customerType": "VIP"
    }
  }
}
```

### 5.7 Get one contact by id (Tested)

```bash
curl -s -H "Authorization: Bearer $TWENTY_API_KEY" \
  "http://localhost:3000/rest/people/<PERSON_ID>"
```

The record comes back under `data.person` (singular), not in a list:

```json
{
  "data": {
    "person": {
      "id": "5a7ad307-5959-4c19-98b5-dc370f850ff4",
      "createdAt": "2026-11-05T06:28:05.827Z",
      "updatedAt": "2026-11-05T06:28:14.380Z",
      "deletedAt": null,
      "name": { "firstName": "Test", "lastName": "Contact" },
      "emails": { "primaryEmail": "test.contact@example.com", "additionalEmails": [] }
    }
  }
}
```

(Trimmed; the remaining fields match section 5.1.)

### 5.8 Delete a contact (Tested)

```bash
curl -s -X DELETE -H "Authorization: Bearer $TWENTY_API_KEY" \
  "http://localhost:3000/rest/people/<PERSON_ID>"
```

Response (HTTP 200):

```json
{ "data": { "deletePerson": { "id": "5a7ad307-5959-4c19-98b5-dc370f850ff4" } } }
```

The same pattern works for notes, tickets and companies (`deleteNote`, `deleteTicket`, `deleteCompany`).

---

## 6. Accounts (Companies)

**Endpoint:** `/rest/companies`

> **Status:** every call in this section was **tested** against this deployment, and the field names come from real responses.

### 6.1 Main fields

| Field | Type | Notes |
|---|---|---|
| `id` | UUID | Generated |
| `name` | text | Company name |
| `domainName` | object | `primaryLinkLabel`, `primaryLinkUrl` (e.g. `notion.com`), `secondaryLinks` |
| `address` | object | `addressStreet1`, `addressStreet2`, `addressCity`, `addressPostcode`, `addressState`, `addressCountry`, `addressLat`, `addressLng` |
| `linkedinLink` | object | `primaryLinkLabel`, `primaryLinkUrl`, `secondaryLinks` |
| `annualRevenue` | object | `amountMicros`, `currencyCode` |
| Account Owner | relation | Workspace member responsible for the account (shown as Account Owner in the UI) |
| `createdAt`, `updatedAt`, `deletedAt` | timestamp | UTC |
| `createdBy`, `updatedBy` | object | Who made the change |

### 6.2 List accounts (Tested)

Request:

```bash
curl -s -H "Authorization: Bearer $TWENTY_API_KEY" \
  "http://localhost:3000/rest/companies?limit=1"
```

Response (trimmed):

```json
{
  "data": {
    "companies": [
      {
        "id": "06290608-8bf0-4806-99ae-a715a6a93fad",
        "createdAt": "2026-10-27T11:02:43.290Z",
        "updatedAt": "2026-10-27T11:02:43.290Z",
        "deletedAt": null,
        "name": "Notion",
        "domainName": {
          "primaryLinkLabel": "",
          "primaryLinkUrl": "notion.com",
          "secondaryLinks": []
        },
        "address": {
          "addressStreet1": "2300 Harrison St",
          "addressStreet2": "",
          "addressCity": "San Francisco",
          "addressPostcode": "94110",
          "addressState": "CA",
          "addressCountry": "United States",
          "addressLat": null,
          "addressLng": null
        },
        "linkedinLink": { "primaryLinkLabel": "", "primaryLinkUrl": "", "secondaryLinks": [] },
        "annualRevenue": { "amountMicros": null, "currencyCode": null },
        "createdBy": { "source": "SYSTEM", "name": "System" }
      }
    ]
  }
}
```

### 6.3 Search an account by name (Tested)

```bash
curl -s -G -H "Authorization: Bearer $TWENTY_API_KEY" \
  "http://localhost:3000/rest/companies" \
  --data-urlencode 'filter=name[eq]:"Test Retail Co"'
```

Result: the matching company is returned in `data.companies` (same record shape as 6.2) with `totalCount` of `1`.

### 6.4 Add an account (Tested)

```bash
curl -s -X POST -H "Authorization: Bearer $TWENTY_API_KEY" \
  -H "Content-Type: application/json" \
  "http://localhost:3000/rest/companies" \
  -d '{ "name": "Test Retail Co" }'
```

Response (trimmed to the verified field):

```json
{ "data": { "createCompany": { "id": "2a09fff1-5d72-462a-b531-99e3a31fc12c" } } }
```

### 6.5 Update an account (Tested)

```bash
curl -s -X PATCH -H "Authorization: Bearer $TWENTY_API_KEY" \
  -H "Content-Type: application/json" \
  "http://localhost:3000/rest/companies/<COMPANY_ID>" \
  -d '{ "name": "Test Retail Co LLC" }'
```

Response (trimmed): `data.updateCompany.name` is `"Test Retail Co LLC"`.

### 6.6 Link a contact to an account (Tested)

Set `companyId` on the person:

```bash
curl -s -X PATCH -H "Authorization: Bearer $TWENTY_API_KEY" \
  -H "Content-Type: application/json" \
  "http://localhost:3000/rest/people/<PERSON_ID>" \
  -d '{ "companyId": "<COMPANY_ID>" }'
```

Response (trimmed): `data.updatePerson.companyId` is the company's id.

To link a ticket to an account, set `accountId` on the ticket (see section 7).

---

## 7. Tickets (custom object)

**Endpoint:** `/rest/tickets`

Tickets are a custom object created for the Retail domain. Each ticket belongs to one contact and one account.

### 7.1 Fields

| Field | Type | Values / notes |
|---|---|---|
| `id` | UUID | Generated |
| `name` | text | Ticket subject |
| `referenceNumber` | text | Business reference, e.g. `TKT-0007`. Supplied by the caller; not auto-generated, and no uniqueness rule is configured |
| `status` | select | `OPEN`, `IN_PROGRESS`, `RESOLVED`, `CLOSED` |
| `priority` | select | `LOW`, `MEDIUM`, `HIGH`, `URGENT` |
| `category` | select | `ORDER_ISSUE`, `RETURN_REFUND`, `DELIVERY`, `PRODUCT_INQUIRY`, `COMPLAINT` |
| `channel` | select | `PHONE`, `EMAIL`, `CHAT`, `STORE` |
| `orderNumber` | text | e.g. `ORD-5007` |
| `description` | text | Free text |
| `contactId` | UUID | The contact (person) the ticket belongs to |
| `accountId` | UUID | The account (company) the ticket belongs to |
| `assigneeId` | UUID | The assigned workspace member (added after 5 November) |
| `team` | select | `SUPPORT`, `BILLING`, `LOGISTICS`, `ESCALATIONS` (added after 5 November; `LOGISTICS` was read back, the others follow the same pattern) |
| `firstResponseDue`, `resolutionDue` | timestamp | UTC; used by the SLA workflow (section 16) |
| `slaStatus` | select | `ON_TRACK`, `AT_RISK`, `BREACHED` (`ON_TRACK` was read back) |
| `createdAt`, `updatedAt`, `deletedAt` | timestamp | UTC |
| `createdBy`, `updatedBy` | object | Who made the change |

### 7.2 Create a ticket (Tested)

Request:

```bash
curl -s -X POST -H "Authorization: Bearer $TWENTY_API_KEY" \
  -H "Content-Type: application/json" \
  "http://localhost:3000/rest/tickets" -d '{
  "name": "Late delivery complaint",
  "referenceNumber": "TKT-0007",
  "status": "OPEN",
  "priority": "HIGH",
  "category": "DELIVERY",
  "channel": "PHONE",
  "orderNumber": "ORD-5007",
  "description": "Order has not arrived on the promised date.",
  "contactId": "<PERSON_ID>"
}'
```

Response (trimmed):

```json
{
  "data": {
    "createTicket": {
      "id": "93992522-2354-4975-9d8a-56870a010274",
      "name": "Late delivery complaint",
      "createdAt": "2026-11-05T09:20:05.114Z",
      "createdBy": { "source": "API", "name": "Retail CRM" },
      "deletedAt": null,
      "updatedAt": "2026-11-05T09:20:05.114Z",
      "referenceNumber": "TKT-0007",
      "status": "OPEN",
      "priority": "HIGH",
      "category": "DELIVERY",
      "channel": "PHONE",
      "orderNumber": "ORD-5007",
      "description": "Order has not arrived on the promised date.",
      "contactId": "8d2c5b6a-4f1e-4c7a-9b3d-2e6f1a0c9d11",
      "accountId": null
    }
  }
}
```

To link the account at creation time, add `"accountId": "<COMPANY_ID>"` to the body (tested). Use the exact uppercase select values from 7.1; an unrecognised value is expected to be rejected (not tested).

### 7.3 Search tickets by reference number (Tested)

```bash
curl -s -G -H "Authorization: Bearer $TWENTY_API_KEY" \
  "http://localhost:3000/rest/tickets" \
  --data-urlencode 'filter=referenceNumber[eq]:"TKT-0002"'
```

Response (trimmed):

```json
{
  "data": {
    "tickets": [
      {
        "id": "648db51a-1698-43d3-a877-f77411b5d30c",
        "name": "Refund not received",
        "createdAt": "2026-10-27T11:48:25.468Z",
        "updatedAt": "2026-10-30T02:22:00.000Z",
        "referenceNumber": "TKT-0002",
        "status": "IN_PROGRESS",
        "priority": "MEDIUM",
        "category": "RETURN_REFUND",
        "channel": "CHAT",
        "orderNumber": "ORD-5002",
        "description": "",
        "contactId": "bbfba160-160d-4a6b-840b-5a51f20b51ea",
        "accountId": "b4da1657-30ab-4afc-ac60-b8a997b1613f"
      }
    ]
  },
  "totalCount": 1,
  "pageInfo": { "hasNextPage": false, "hasPreviousPage": false }
}
```

### 7.4 Search tickets by date (Tested)

Tickets created on or after a date:

```bash
curl -s -G -H "Authorization: Bearer $TWENTY_API_KEY" \
  "http://localhost:3000/rest/tickets" \
  --data-urlencode 'filter=createdAt[gte]:"2026-10-27T00:00:00.000Z"'
```

Tickets created on one specific day (date range):

```bash
curl -s -G -H "Authorization: Bearer $TWENTY_API_KEY" \
  "http://localhost:3000/rest/tickets" \
  --data-urlencode 'filter=and(createdAt[gte]:"2026-10-27T00:00:00.000Z",createdAt[lt]:"2026-10-28T00:00:00.000Z")'
```

Both return the same shape as 7.3, with one entry per matching ticket and `totalCount` set to the number of matches. Dates are in UTC (see 3.7).

### 7.5 Other ticket searches (Tested)

All tickets for one contact:

```bash
curl -s -G -H "Authorization: Bearer $TWENTY_API_KEY" \
  "http://localhost:3000/rest/tickets" \
  --data-urlencode 'filter=contactId[eq]:"<PERSON_ID>"'
```

Result: only that contact's tickets, with `totalCount` set to how many matched.

Combined filter (resolved and urgent):

```bash
curl -s -G -H "Authorization: Bearer $TWENTY_API_KEY" \
  "http://localhost:3000/rest/tickets" \
  --data-urlencode 'filter=and(status[eq]:"RESOLVED",priority[eq]:"URGENT")'
```

Result: only tickets that satisfy both conditions.

### 7.6 Update a ticket (Tested)

```bash
curl -s -X PATCH -H "Authorization: Bearer $TWENTY_API_KEY" \
  -H "Content-Type: application/json" \
  "http://localhost:3000/rest/tickets/<TICKET_ID>" \
  -d '{ "status": "RESOLVED" }'
```

Response (trimmed): `data.updateTicket.status` is `"RESOLVED"`.

### 7.7 Newest first, and paging (Tested)

Newest tickets first, three at a time:

```bash
curl -s -G -H "Authorization: Bearer $TWENTY_API_KEY" \
  "http://localhost:3000/rest/tickets" \
  --data-urlencode 'order_by=createdAt[DescNullsLast]' \
  --data-urlencode 'limit=3'
```

Next page: take `pageInfo.endCursor` from a response and pass it as `starting_after`:

```bash
curl -s -G -H "Authorization: Bearer $TWENTY_API_KEY" \
  "http://localhost:3000/rest/tickets" \
  --data-urlencode 'limit=2' \
  --data-urlencode 'starting_after=<endCursor>'
```

---

## 8. Notes

Notes are separate records. Adding a note to a ticket takes **two calls**: create the note, then link it to the ticket with a note target. One note can be linked to several records (contacts, accounts, tickets).

### 8.1 Create a note (Tested)

```bash
curl -s -X POST -H "Authorization: Bearer $TWENTY_API_KEY" \
  -H "Content-Type: application/json" \
  "http://localhost:3000/rest/notes" -d '{
  "title": "Phone follow-up",
  "bodyV2": { "markdown": "Customer called about the delay. New delivery date confirmed." }
}'
```

Response (trimmed):

```json
{
  "data": {
    "createNote": {
      "id": "66bf4c72-c75e-47f5-92eb-716e1a045709",
      "title": "Phone follow-up",
      "createdAt": "2026-11-05T09:24:10.000Z"
    }
  }
}
```

### 8.2 Link the note to a ticket (Tested)

```bash
curl -s -X POST -H "Authorization: Bearer $TWENTY_API_KEY" \
  -H "Content-Type: application/json" \
  "http://localhost:3000/rest/noteTargets" \
  -d '{ "noteId": "<NOTE_ID>", "targetTicketId": "<TICKET_ID>" }'
```

Response (trimmed):

```json
{
  "data": {
    "createNoteTarget": {
      "id": "09fc0733-f52e-4e8f-bf57-fda304b426a1",
      "createdAt": "2026-10-29T22:31:27.435Z",
      "deletedAt": null,
      "createdBy": { "source": "API", "name": "Retail CRM" }
    }
  }
}
```

The note now appears in the **Notes** section of the ticket in the Twenty UI.

To attach a note to a contact or an account instead, use `targetPersonId` or `targetCompanyId` in place of `targetTicketId` (both tested). One note can have several targets, so the same note can be linked to a contact, an account and a ticket by creating one note target for each.

---

## 9. End-to-end example

A customer, Abby Moore, calls about a late delivery.

1. **Find her** by phone or email (5.2 or 5.3). Not found, so:
2. **Add the contact** (5.5) and keep the returned `id` as `<PERSON_ID>`.
3. **Create a ticket** (7.2) with `contactId` set to `<PERSON_ID>`, and keep the ticket `id` as `<TICKET_ID>`.
4. **Add a note** (8.1), then **link it** to the ticket (8.2).
5. **Later, an agent looks the ticket up** by reference number (7.3) or lists the day's tickets (7.4).
6. **Update the status** when resolved (7.6).

---

## 10. Errors and troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `401 Unauthorized` | Key missing, wrong or regenerated | Send the current key in the `Authorization` header |
| Connection refused | Twenty is not running | Run `docker compose up -d` in the Twenty folder and wait for the server to be healthy |
| Empty list, `totalCount` 0 | No match | Check spelling, and that a phone search omits the country code |
| Date search misses a record | Dates are stored in UTC, four hours behind Dubai | Use the UTC date (a record made after midnight Dubai time can still be on the previous UTC day) |
| Create or update is rejected (expected; not tested) | Select value does not match an option | Use the exact uppercase values listed in sections 5.1 and 7.1 |
| Possible duplicate contacts | Duplicate prevention was not tested | Search by email or loyalty ID before creating |
| `PERMISSION_DENIED` (HTTP 400) | The key's role does not allow that object or action | Ask for an object-level rule on the role (section 17) |
| `403 Missing authentication token` | No `Authorization` header (this also proves a tunnel address reaches Twenty) | Send the key |
| `Object interaction doesn't have any "type" field` | The field is called `interactionType` | Use `interactionType` (section 13) |
| The tunnel address stopped working | The tunnel was restarted or the laptop slept; the address changes each time | Ask for the new address (section 18) |

The REST playground (Settings → Developers → Launch) shows the exact endpoints and field names for this workspace, including any fields added later.

---

## 11. Current limits and planned next steps

- **Reference numbers** are supplied by the caller. Twenty does not generate them, and no uniqueness rule is configured.
- **Assignment, SLA and alerts** now exist: assignee and team on tickets, SLA fields, and workflows for the priority alert and the SLA breach escalation (section 16). There is **no built-in routing or round-robin assignment**.
- **The INVOQ modules exist:** Interactions (section 13), the generic Service Requests (section 14) and the Category catalog (section 15). There is no separate Agent object: agents are workspace members (`assigneeId`, `handledById`).
- **Dependent dropdowns are not native to Twenty.** The catalog supplies the lists and the client builds the dropdowns; the values are not enforced.
- **Local deployment only.** One workspace on a laptop, reached from outside by a temporary tunnel whose address changes (section 18). Not production hosting.
- **Not built yet:** a first-response SLA warning, automatic assignment, and creating a ticket from an incoming email.

---

## 12. Verification summary

Every call below was run against this deployment on 5 November 2026 and returned the expected result.

| Area | Search and read | Create | Update and link | Delete |
|---|---|---|---|---|
| Contacts | Search by email, phone or loyalty ID, and get one contact by id | Add a contact | Update fields and link to a company | Yes |
| Accounts | List accounts and search by name | Add an account | Update the name | Yes |
| Tickets | Search by reference number, by date or date range, by contact, and with a combined filter, in newest-first order and in pages | Create a ticket linked to a contact and an account | Update the status | Yes |
| Notes | Not tested | Create a note | Link it to a ticket, a contact or a company | Yes |

Not yet tested: preventing duplicate records, how the API responds to an invalid select value, and reading back the notes attached to a record.

**Added after 5 November** (run on 9 to 13 November 2026)

| Area | Verified |
|---|---|
| Tickets (new fields) | Set and read back the assignee, team and SLA fields; create a ticket with `resolutionDue` and `slaStatus` |
| Interactions | Create for a ticket and for a service request; read back |
| Service Requests | Create with every field, a contact, an account and an assignee; search by reference number |
| Category catalog | Create 20 entries; read the categories and sub categories for a sector |
| Automations | Priority alert (tickets and service requests); SLA breach escalation (tickets) |
| Permissions | With the limited role: reading the catalog and tickets and creating a service request worked; creating a ticket and reading opportunities were refused |

Not yet tested: updating or deleting service requests, interactions and catalog entries; filters on service requests other than the reference number; the SLA breach workflow for service requests; creating interactions with a key that has no edit rule on them.

---

## 13. Interactions (calls, emails, chats)

**Endpoint:** `/rest/interactions`

An Interaction is one call, email, chat or SMS. It links to a **ticket** (Retail) or a **service request** (generic module), to a contact, and to the agent (workspace member) who handled it. Use whichever of `ticketId` and `serviceRequestId` applies.

### 13.1 Fields

| Field | Type | Values / notes |
|---|---|---|
| `id` | UUID | Generated |
| `name` | text | Label, for example `Wrong size call` |
| `interactionType` | select | `CALL`, `EMAIL`, `CHAT`, `SMS`. Twenty reserves the name `type`, so this field is `interactionType` (it was `typeCustom` before 11 November) |
| `direction` | select | `INBOUND`, `OUTBOUND` |
| `occurredAt` | timestamp | UTC |
| `durationSeconds` | number | Calls only |
| `summary` | text | Free text |
| `outcome` | select | `RESOLVED`, `FOLLOW_UP_NEEDED`, `ESCALATED` |
| `ticketId` | UUID | The Retail ticket |
| `serviceRequestId` | UUID | The generic service request |
| `contactId` | UUID | The contact (person); optional |
| `handledById` | UUID | The agent: a workspace member id; optional |
| `createdAt`, `updatedAt`, `deletedAt`, `createdBy`, `updatedBy` | | As on other objects |

### 13.2 Create an interaction for a ticket (Tested)

```bash
curl -s -X POST -H "Authorization: Bearer $TWENTY_API_KEY" \
  -H "Content-Type: application/json" \
  "http://localhost:3000/rest/interactions" -d '{
  "name": "Wrong size call",
  "interactionType": "CALL",
  "direction": "INBOUND",
  "occurredAt": "2026-11-06T07:30:00.000Z",
  "durationSeconds": 420,
  "summary": "Customer received the wrong size. Exchange arranged.",
  "outcome": "FOLLOW_UP_NEEDED",
  "ticketId": "<TICKET_ID>",
  "handledById": "<WORKSPACE_MEMBER_ID>"
}'
```

The response has the same shape as other creates (`data.createInteraction`). A ticket's record page then lists the interaction under **Interactions**.

### 13.3 Create an interaction for a service request (Tested)

Same call with `"serviceRequestId": "<SERVICE_REQUEST_ID>"` instead of `ticketId`, for example `"interactionType": "EMAIL"`, `"direction": "OUTBOUND"` and `"outcome": "RESOLVED"`.

### 13.4 List the interactions of a ticket (Not yet tested)

Expected to follow the usual filter pattern, for example `filter=ticketId[eq]:"<TICKET_ID>"`, with `order_by=occurredAt[DescNullsLast]`. Check it in the REST playground first.

---

## 14. Service Requests (generic module)

**Endpoint:** `/rest/serviceRequests`

A separate, industry-neutral ticket module, so one system can serve Retail, Health, Real Estate, Banking and Government. The Retail Tickets (section 7) are unchanged.

### 14.1 Fields

| Field | Type | Values / notes |
|---|---|---|
| `id` | UUID | Generated |
| `name` | text | Subject |
| `referenceNumber` | text | Supplied by the caller, for example `SR-0001`; no uniqueness rule is configured |
| `sector` | select | `RETAIL`, `HEALTH`, `REAL_ESTATE`, `BANKING`, `GOVERNMENT` |
| `category` | text | Free text (the catalog in section 15 supplies suggested values) |
| `subCategory` | text | Free text |
| `description` | text | Free text |
| `status` | select | `OPEN`, `IN_PROGRESS`, `RESOLVED`, `CLOSED` |
| `priority` | select | `LOW`, `MEDIUM`, `HIGH`, `URGENT` |
| `channel` | select | Phone, Email, Chat, SMS, Web, In person (`PHONE` and `EMAIL` were used in tests) |
| `externalReference` | text | Optional; for example the INVOQ interaction id |
| `contactId` | UUID | The contact (person) |
| `accountId` | UUID | The account (company) |
| `assigneeId` | UUID | The assigned workspace member |
| `firstResponseDue`, `resolutionDue` | timestamp | UTC |
| `slaStatus` | select | `ON_TRACK`, `AT_RISK`, `BREACHED` (see section 16) |
| `createdAt`, `updatedAt`, `deletedAt`, `createdBy`, `updatedBy` | | As on other objects |

### 14.2 Create a service request (Tested)

```bash
curl -s -X POST -H "Authorization: Bearer $TWENTY_API_KEY" \
  -H "Content-Type: application/json" \
  "http://localhost:3000/rest/serviceRequests" -d '{
  "name": "Customer cannot access account",
  "referenceNumber": "SR-0001",
  "sector": "BANKING",
  "category": "Account access",
  "subCategory": "Password reset",
  "description": "Caller locked out after three attempts.",
  "status": "OPEN",
  "priority": "HIGH",
  "channel": "PHONE",
  "assigneeId": "<WORKSPACE_MEMBER_ID>",
  "externalReference": "INVOQ-INT-48213"
}'
```

Response (trimmed):

```json
{
  "data": {
    "createServiceRequest": {
      "id": "<ID>",
      "name": "Customer cannot access account",
      "createdBy": { "source": "API", "name": "<KEY_NAME>" },
      "referenceNumber": "SR-0001",
      "sector": "BANKING",
      "category": "Account access",
      "subCategory": "Password reset",
      "description": "Caller locked out after three attempts.",
      "status": "OPEN",
      "priority": "HIGH",
      "accountId": null
    }
  }
}
```

To attach a contact and an account, add `"contactId": "<PERSON_ID>"` and `"accountId": "<COMPANY_ID>"` (Tested; both links were saved and displayed). Any select value must use the exact uppercase values above.

### 14.3 Search service requests by reference number (Tested)

```bash
curl -s -H "Authorization: Bearer $TWENTY_API_KEY" \
  "http://localhost:3000/rest/serviceRequests?filter=referenceNumber%5Beq%5D:SR-0001"
```

Returns `data.serviceRequests` with the matching record and `totalCount` 1. Other searches (by date, sector, contact) follow the patterns in section 3.3 but were not run on this object.

### 14.4 Update a service request (Not yet tested)

Expected to work like the other objects: `PATCH /rest/serviceRequests/{id}` with only the fields to change.

### 14.5 What changed compared with creating a Retail ticket

| | Retail Tickets (`POST /rest/tickets`) | Service Requests (`POST /rest/serviceRequests`) |
|---|---|---|
| Endpoint | `/rest/tickets` | `/rest/serviceRequests` |
| Industry | Not present | `sector` (new) |
| `category` | Select: `ORDER_ISSUE`, `RETURN_REFUND`, `DELIVERY`, `PRODUCT_INQUIRY`, `COMPLAINT` | Free text |
| `subCategory` | Not present | Free text (new) |
| `orderNumber` | Present | Removed (retail specific) |
| `channel` | `PHONE`, `EMAIL`, `CHAT`, `STORE` | Generic list; no `STORE` |
| `externalReference` | Not present | Optional (new) |
| `name`, `referenceNumber`, `description`, `status`, `priority`, `contactId`, `accountId`, `assigneeId` | Present | The same |

---

## 15. Category catalog (dependent lists by sector)

**Endpoint:** `/rest/catalogEntries`

Twenty has no dependent dropdowns, so the valid Sector / Category / SubCategory combinations are stored as records. A client such as INVOQ reads them to build a Category list that depends on the sector and a SubCategory list that depends on the category, then saves the chosen values as text on the service request. Twenty does **not** reject a category that is not in the catalog.

### 15.1 Fields

| Field | Type | Notes |
|---|---|---|
| `name` | text | A readable label, for example `BANKING / Cards / Card blocked` |
| `sector` | select | The same five values as on service requests |
| `category` | text | |
| `subCategory` | text | |

### 15.2 Categories and sub categories (the 20 sample entries)

| Sector | Category | Sub categories |
|---|---|---|
| `RETAIL` | Order issue | Wrong item, Late delivery |
| `RETAIL` | Returns and refunds | Refund status, Return request |
| `HEALTH` | Appointments | Book or reschedule, Cancellation |
| `HEALTH` | Billing | Invoice query, Insurance claim |
| `REAL_ESTATE` | Property enquiry | Viewing request, Pricing |
| `REAL_ESTATE` | Maintenance | Repair request, Urgent issue |
| `BANKING` | Cards | Card blocked, Lost or stolen |
| `BANKING` | Account access | Password reset, Locked account |
| `GOVERNMENT` | Applications | Status check, Missing documents |
| `GOVERNMENT` | Complaints | Service delay, Staff conduct |

### 15.3 Get the lists for a sector (Tested)

```bash
curl -s -H "Authorization: Bearer $TWENTY_API_KEY" \
  "http://localhost:3000/rest/catalogEntries?filter=sector%5Beq%5D:BANKING&limit=200"
```

The response is a list under `data.catalogEntries`. The client takes the distinct `category` values for the first dropdown (for Banking: Account access, Cards) and filters the same rows by the chosen category for the second dropdown (for Account access: Locked account, Password reset). In a terminal:

```bash
curl -s -H "Authorization: Bearer $TWENTY_API_KEY" "http://localhost:3000/rest/catalogEntries?filter=sector%5Beq%5D:BANKING&limit=200" \
  | python3 -c "import sys,json; rows=json.load(sys.stdin)['data']['catalogEntries']; print(sorted({r['category'] for r in rows}))"
```

### 15.4 Add or change catalog entries (Tested)

New entries are created with `POST /rest/catalogEntries`, for example:

```json
{
  "name": "BANKING / Cards / Card blocked",
  "sector": "BANKING",
  "category": "Cards",
  "subCategory": "Card blocked"
}
```

This is how the sample catalog was loaded. Update and delete follow the standard pattern (not tested on this object).

---

## 16. Automations (workflows)

These run inside Twenty. Emails are sent from a mailbox connected under Settings, Accounts, so the sender is that mailbox. Times and schedules are in UTC.

### 16.1 High and Urgent priority alert

- **Retail Tickets:** workflow **High priority ticket email**. Trigger: a ticket is created with priority High or Urgent. Action: an email to a supervisor with the reference number and name. Tested with HIGH, URGENT and LOW tickets created through the API (LOW sent nothing).
- **Service Requests:** workflow **High priority service request email**, the same logic on service requests (subject `Service request URGENT - SR-0003`, body with the reference, name, sector and priority). Tested with an Urgent request.
- **Tickets created by hand in the Twenty screen do not trigger these.** The screen creates the record first and fills the fields afterwards, so the priority is empty when the trigger runs. Records created through the API, which arrive complete, do trigger them.

### 16.2 SLA breach escalation

- **Retail Tickets:** workflow **SLA breach escalation**, scheduled every 15 minutes. It finds tickets whose `resolutionDue` is in the past, whose `slaStatus` is `ON_TRACK` or `AT_RISK`, and whose status is `OPEN` or `IN_PROGRESS`; it sets `slaStatus` to `BREACHED` and emails a supervisor. Because it only picks up tickets that are not yet `BREACHED`, a ticket is emailed once.
- **Service Requests:** a copy for service requests was set up as part of the module (see the project history for its status).

A ticket that triggers it (Tested; priority MEDIUM so the priority alert does not also fire):

```bash
curl -s -X POST -H "Authorization: Bearer $TWENTY_API_KEY" \
  -H "Content-Type: application/json" \
  "http://localhost:3000/rest/tickets" -d '{
  "name": "SLA breach test",
  "referenceNumber": "TKT-0020",
  "status": "OPEN",
  "priority": "MEDIUM",
  "category": "DELIVERY",
  "channel": "PHONE",
  "description": "Resolution deadline already passed.",
  "resolutionDue": "2026-11-01T09:00:00.000Z",
  "slaStatus": "ON_TRACK"
}'
```

After the next scheduled run, or when the workflow is run with its Test button, the ticket's `slaStatus` is `BREACHED` and one email is sent.

### 16.3 Other notes

- A workflow must be **Activated** to run on its own; the **Test** button runs it once.
- The schedule only runs while Twenty is running.
- Every execution is listed under Workflows, Workflow Runs, with the status of each step.

---

## 17. Roles and API key permissions

### 17.1 Roles for people (Twenty web interface)

| Role | Records | Settings |
|---|---|---|
| Agent | See and edit all objects; cannot delete | None |
| Supervisor | See, edit and delete all objects | None |
| Admin | Everything, including permanent delete | Everything |

These roles apply to every object, including Service Requests, Interactions and Catalog Entries. They are meant for people.

### 17.2 Role for an external integration key

A key given to another system should use a narrow role, not Admin. The role created for the INVOQ integration test is **API Integration**:

| Object | Access |
|---|---|
| Service Requests, People, Companies | See and edit |
| Catalog Entries, Tickets, Interactions | See only |
| Everything else | None |

All other permissions (layout, logic, workspace settings) are off. To let the integration create interactions, add an edit rule on Interactions.

### 17.3 Permission errors (Tested)

A call the role does not allow returns HTTP 400 with `"Entity performing the request does not have permission"` and `"code": "PERMISSION_DENIED"`. With this role: reading the catalog, reading tickets and creating a service request with an `assigneeId` worked, while creating a ticket and reading opportunities were refused. A call with no key at all returns 403 `Missing authentication token`.

### 17.4 Key lifetime

Keys carry an expiry. When one expires, create a new key (Settings, Developers, API keys) under the same role and send it privately. Regenerating a key stops the old one working immediately.

---

## 18. Using the API from outside the laptop

Twenty runs on a laptop, so `http://localhost:3000` only works on that computer. For testing from another machine, a temporary **Cloudflare Quick Tunnel** gives a public HTTPS address that forwards to the local Twenty.

- Replace `http://localhost:3000` in every example with the tunnel address, for example `https://<tunnel-address>.trycloudflare.com/rest/serviceRequests`. Authentication is the same (`Authorization: Bearer <KEY>`).
- The address **changes each time the tunnel is restarted** (for example after the laptop sleeps), and the old one stops working. The new one is sent by message.
- The tunnel only works while the laptop is awake, Docker is running and Twenty is healthy.
- Test it first without a key: `403 Missing authentication token` means the address reached Twenty. Then test with the key.
- Keys and tunnel addresses are not stored in this document.

---

## Appendix A: Optional helpers for readable output

The API returns JSON. These two shell functions print one clean line per record instead. Paste them once into the terminal window you are using (they only last for that window), then add `| show_people` or `| show_tickets` to the end of a search command.

```bash
show_people() { python3 -c "import sys,json; [print(p['name']['firstName'], p['name']['lastName'], '|', p['emails']['primaryEmail'], '|', p['loyaltyId'], '|', p['customerType']) for p in json.load(sys.stdin)['data']['people']]"; }
show_tickets() { python3 -c "import sys,json; d=json.load(sys.stdin); [print(t['referenceNumber'], '|', t['name'], '|', t['status'], '|', t['priority'], '|', t['channel']) for t in d['data']['tickets']]; print('Total:', d['totalCount'])"; }
```

Example:

```bash
curl -s -G -H "Authorization: Bearer $TWENTY_API_KEY" \
  "http://localhost:3000/rest/people" \
  --data-urlencode 'filter=loyaltyId[eq]:"LOY-1002"' | show_people
```

Output:

```
Fatima Khan | fatima.khan@example.com | LOY-1002 | RETAIL
```

Notes:

- They need `python3` installed.
- They only work on search and list responses (people or tickets). Do not use them on create, update or delete responses, which have a different shape.
