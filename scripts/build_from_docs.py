"""Rebuild Aroosh's Twenty CRM (Retail / INVOQ) from her documentation, on a fresh Twenty workspace.

    TWENTY_URL=https://crm.example.com KEY_FILE=~/aroosh-admin.key python3 scripts/build_from_docs.py

Source: docs/twenty-crm-project-history.md and docs/twenty-crm-retail-api.md (repo aroosh77/twenty-crm-invoq).
Creates (idempotent, safe to re-run): custom fields on People; objects Ticket, Interaction, Service Request,
Catalog Entry with their fields and relations; roles Agent and Supervisor; the records listed in the docs.
Values the docs do not give (some categories, dates, order numbers) follow the docs' own patterns; see
DEPLOYMENT.md "Rebuilt from documentation". Needs an API key with the Admin role. Never prints the key.
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = os.environ.get("TWENTY_URL", "http://localhost:3000").rstrip("/")
KEY = open(os.path.expanduser(os.environ.get("KEY_FILE", "~/aroosh-admin.key"))).read().strip()
COLORS = ["blue", "green", "orange", "red", "purple", "turquoise", "yellow", "gray"]


def call(method, path, body=None, ok404=False):
    req = urllib.request.Request(BASE + path, method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        raise SystemExit(f"{method} {path} -> {e.code}: {e.read().decode()[:600]}")


def gql(query, variables=None):
    out = call("POST", "/metadata", {"query": query, "variables": variables or {}})
    if out.get("errors"):
        raise SystemExit(f"graphql: {out['errors'][0]['message']}")
    return out["data"]


# ---------- schema helpers (pattern tested on Twenty v2.59.2)
def objects():
    return {o["nameSingular"]: o for o in call("GET", "/rest/metadata/objects?limit=200")["data"]}


def fields_of(obj):
    o = call("GET", f"/rest/metadata/objects/{obj['id']}")
    o = o.get("data", o)
    o = o.get("object", o)
    return {f["name"]: f for f in o.get("fields", [])}


def opts(pairs):
    return [{"label": l, "value": v, "color": COLORS[i % len(COLORS)], "position": i} for i, (l, v) in enumerate(pairs)]


def P(*labels):  # labels -> (label, VALUE)
    return [(l, l.upper().replace(" ", "_").replace("-", "_")) for l in labels]


def ensure_object(objs, singular, plural, label, labels, icon, desc):
    if singular not in objs:
        o = call("POST", "/rest/metadata/objects", {"nameSingular": singular, "namePlural": plural,
                                                      "labelSingular": label, "labelPlural": labels,
                                                      "icon": icon, "description": desc})
        print("created object", singular)
        objs.update(objects())
    return objs[singular]


def field(obj, name, label, ftype, icon="IconAbc", options=None, default=None):
    if name in fields_of(obj):
        return
    body = {"objectMetadataId": obj["id"], "name": name, "label": label, "type": ftype, "icon": icon}
    if options:
        body["options"] = opts(options)
    if default is not None:
        body["defaultValue"] = default
    call("POST", "/rest/metadata/fields", body)
    print(f"  field {obj['nameSingular']}.{name}")


def relation(obj, name, label, target, target_label):
    if name in fields_of(obj):
        return
    call("POST", "/rest/metadata/fields", {
        "objectMetadataId": obj["id"], "name": name, "label": label, "type": "RELATION", "icon": "IconLink",
        "relationCreationPayload": {"type": "MANY_TO_ONE", "targetObjectMetadataId": target["id"],
                                    "targetFieldLabel": target_label, "targetFieldIcon": "IconLink"}})
    print(f"  relation {obj['nameSingular']}.{name} -> {target['nameSingular']}")


STATUS = P("Open", "In Progress", "Resolved", "Closed")
PRIORITY = P("Low", "Medium", "High", "Urgent")
SLA = P("On Track", "At Risk", "Breached")
SECTOR = P("Retail", "Health", "Real Estate", "Banking", "Government")


def schema():
    objs = objects()
    person, company, member = objs["person"], objs["company"], objs["workspaceMember"]

    # People: retail fields (section 7.2)
    field(person, "loyaltyId", "Loyalty ID", "TEXT", "IconId")
    field(person, "customerType", "Customer Type", "SELECT", "IconUser", P("Retail", "Wholesale", "VIP"))
    field(person, "preferredChannel", "Preferred Channel", "SELECT", "IconMessage",
          P("Phone", "Email", "Chat", "SMS", "Store"))

    # Tickets (sections 7.3, 21.4, 21.6)
    t = ensure_object(objs, "ticket", "tickets", "Ticket", "Tickets", "IconTicket", "Retail support ticket")
    field(t, "referenceNumber", "Reference Number", "TEXT", "IconHash")
    field(t, "status", "Status", "SELECT", "IconProgress", STATUS)
    field(t, "priority", "Priority", "SELECT", "IconAlertTriangle", PRIORITY)
    field(t, "category", "Category", "SELECT", "IconTag",
          [("Order Issue", "ORDER_ISSUE"), ("Return / Refund", "RETURN_REFUND"), ("Delivery", "DELIVERY"),
           ("Product Inquiry", "PRODUCT_INQUIRY"), ("Complaint", "COMPLAINT")])
    field(t, "channel", "Channel", "SELECT", "IconPhone", P("Phone", "Email", "Chat", "Store"))
    field(t, "orderNumber", "Order Number", "TEXT", "IconShoppingCart")
    field(t, "description", "Description", "TEXT", "IconAlignLeft")
    field(t, "team", "Team", "SELECT", "IconUsersGroup", P("Support", "Billing", "Logistics", "Escalations"))
    field(t, "firstResponseDue", "First Response Due", "DATE_TIME", "IconClock")
    field(t, "resolutionDue", "Resolution Due", "DATE_TIME", "IconCalendarDue")
    field(t, "slaStatus", "SLA Status", "SELECT", "IconGauge", SLA)
    relation(t, "contact", "Contact", person, "Tickets")
    relation(t, "account", "Account", company, "Tickets")
    relation(t, "assignee", "Assignee", member, "Assigned tickets")

    # Service Requests (section 22.3)
    s = ensure_object(objs, "serviceRequest", "serviceRequests", "Service Request", "Service Requests",
                      "IconClipboardList", "Generic ticket for any industry (INVOQ)")
    field(s, "referenceNumber", "Reference Number", "TEXT", "IconHash")
    field(s, "sector", "Sector", "SELECT", "IconBuildingStore", SECTOR)
    field(s, "category", "Category", "TEXT", "IconTag")
    field(s, "subCategory", "Sub Category", "TEXT", "IconTags")
    field(s, "description", "Description", "TEXT", "IconAlignLeft")
    field(s, "status", "Status", "SELECT", "IconProgress", STATUS)
    field(s, "priority", "Priority", "SELECT", "IconAlertTriangle", PRIORITY)
    field(s, "channel", "Channel", "SELECT", "IconPhone", P("Phone", "Email", "Chat", "SMS", "Web", "In Person"))
    field(s, "externalReference", "External Reference", "TEXT", "IconExternalLink")
    field(s, "firstResponseDue", "First Response Due", "DATE_TIME", "IconClock")
    field(s, "resolutionDue", "Resolution Due", "DATE_TIME", "IconCalendarDue")
    field(s, "slaStatus", "SLA Status", "SELECT", "IconGauge", SLA)
    relation(s, "contact", "Contact", person, "Service Requests")
    relation(s, "account", "Account", company, "Service Requests")
    relation(s, "assignee", "Assignee", member, "Assigned service requests")

    # Catalog Entries (section 22.4)
    c = ensure_object(objs, "catalogEntry", "catalogEntries", "Catalog Entry", "Catalog Entries",
                      "IconListTree", "Valid Sector / Category / Sub Category combinations")
    field(c, "sector", "Sector", "SELECT", "IconBuildingStore", SECTOR)
    field(c, "category", "Category", "TEXT", "IconTag")
    field(c, "subCategory", "Sub Category", "TEXT", "IconTags")

    # Interactions (section 21.7; 'type' is reserved, so interactionType)
    i = ensure_object(objs, "interaction", "interactions", "Interaction", "Interactions",
                      "IconMessages", "One call, email, chat or SMS")
    field(i, "interactionType", "Type", "SELECT", "IconCategory", P("Call", "Email", "Chat", "SMS"))
    field(i, "direction", "Direction", "SELECT", "IconArrowsExchange", P("Inbound", "Outbound"))
    field(i, "occurredAt", "Occurred At", "DATE_TIME", "IconCalendar")
    field(i, "durationSeconds", "Duration Seconds", "NUMBER", "IconClock")
    field(i, "summary", "Summary", "TEXT", "IconAlignLeft")
    field(i, "outcome", "Outcome", "SELECT", "IconFlag",
          [("Resolved", "RESOLVED"), ("Follow-up Needed", "FOLLOW_UP_NEEDED"), ("Escalated", "ESCALATED")])
    relation(i, "ticket", "Ticket", t, "Interactions")
    relation(i, "serviceRequest", "Service Request", s, "Interactions")
    relation(i, "contact", "Contact", person, "Interactions")
    relation(i, "handledBy", "Handled By", member, "Handled interactions")
    print("schema ok")


# ---------- records
def find(plural, flt):
    q = urllib.parse.urlencode({"filter": flt, "limit": 1})
    rows = call("GET", f"/rest/{plural}?{q}")["data"][plural]
    return rows[0]["id"] if rows else None


def upsert(plural, singular, flt, body):
    rid = find(plural, flt)
    if rid:
        return rid
    out = call("POST", f"/rest/{plural}", body)
    return out["data"][f"create{singular}"]["id"]


def phone(n):
    return {"primaryPhoneNumber": n, "primaryPhoneCountryCode": "AE", "primaryPhoneCallingCode": "+971"}


def records():
    uw = upsert("companies", "Company", 'name[eq]:"Urban Wear Boutique"', {"name": "Urban Wear Boutique"})

    people = {}
    for key, first, last, extra in [
        ("fatima", "Fatima", "Khan", {"emails": {"primaryEmail": "fatima.khan@example.com"}, "phones": phone("501112222"),
                                      "loyaltyId": "LOY-1002", "customerType": "RETAIL", "companyId": uw}),
        ("yumna", "Yumna", "Khan", {"companyId": uw}),
        ("lena", "Lena", "Tanzil", {"companyId": uw}),
        ("noor", "Noor", "Saleh", {"emails": {"primaryEmail": "noor.saleh@example.com"}, "loyaltyId": "LOY-1004",
                                   "jobTitle": "Store Manager", "customerType": "VIP", "companyId": uw}),
        ("ally", "Ally", "Jayne", {"loyaltyId": "LOY-1005", "customerType": "RETAIL", "companyId": uw}),
        ("sam", "Sam", "Rivers", {"emails": {"primaryEmail": "sam.rivers@example.com"}, "phones": phone("506665555"),
                                  "loyaltyId": "LOY-1006", "customerType": "RETAIL", "companyId": uw}),
        ("qa", "QA", "PermissionTest", {"emails": {"primaryEmail": "qa.permissiontest@example.com"}}),
    ]:
        flt = f'and(name.firstName[eq]:"{first}",name.lastName[eq]:"{last}")'
        people[key] = upsert("people", "Person", flt, {"name": {"firstName": first, "lastName": last}, **extra})
    print(f"people: {len(people)}, company: Urban Wear Boutique")

    tickets = {}
    for ref, name, who, st, pr, cat, ch, extra in [
        ("TKT-0001", "Damaged item received", "fatima", "OPEN", "HIGH", "ORDER_ISSUE", "PHONE", {"orderNumber": "ORD-5001"}),
        ("TKT-0002", "Refund not received", "yumna", "IN_PROGRESS", "MEDIUM", "RETURN_REFUND", "CHAT", {"orderNumber": "ORD-5002"}),
        ("TKT-0003", "Where is my delivery?", "lena", "OPEN", "LOW", "DELIVERY", "STORE", {"orderNumber": "ORD-5003"}),
        ("TKT-0004", "Wrong size delivered", "noor", "OPEN", "HIGH", "ORDER_ISSUE", "PHONE", {"orderNumber": "ORD-5004"}),
        ("TKT-0005", "Missing item in order", "ally", "OPEN", "MEDIUM", "ORDER_ISSUE", "EMAIL", {"orderNumber": "ORD-5005"}),
        ("TKT-0006", "Late delivery (practice)", "sam", "OPEN", "HIGH", "DELIVERY", "PHONE", {"orderNumber": "ORD-5006"}),
        ("TKT-0007", "Workflow email test 2", None, "IN_PROGRESS", "MEDIUM", None, None, {"team": "LOGISTICS"}),
        ("TKT-0013", "Workflow email test", None, "OPEN", None, None, None, {}),
        ("TKT-0014", "Workflow test: high priority", None, "OPEN", "HIGH", None, "PHONE", {}),
        ("TKT-0015", "Workflow test: low priority", None, "OPEN", "LOW", None, "PHONE", {}),
        ("TKT-0016", "Workflow test: urgent priority", None, "OPEN", "URGENT", None, "PHONE", {}),
        ("TKT-0020", "SLA breach test", None, "OPEN", "MEDIUM", "DELIVERY", "PHONE",
         {"description": "Resolution deadline already passed.", "resolutionDue": "2026-11-01T09:00:00.000Z", "slaStatus": "BREACHED"}),
        ("TKT-0030", "Test Ticket to check Interactions working", None, "OPEN", None, None, None, {}),
        ("TKT-QA-002", "Wrong size delivered", "noor", "OPEN", "HIGH", "ORDER_ISSUE", "PHONE",
         {"orderNumber": "ORD-QA-002", "description": "QA test: Customer received size M instead of L."}),
    ]:
        body = {"name": name, "referenceNumber": ref, "status": st, **extra}
        if pr: body["priority"] = pr
        if cat: body["category"] = cat
        if ch: body["channel"] = ch
        if who:
            body["contactId"] = people[who]
            body["accountId"] = uw
        tickets[ref] = upsert("tickets", "Ticket", f'referenceNumber[eq]:"{ref}"', body)
    print(f"tickets: {len(tickets)}")

    for title, body_md, ref in [
        ("Phone follow-up", "Customer called about the wrong size. Exchange being arranged.", "TKT-0004"),
        ("Phone follow-up", "QA test note.", "TKT-QA-002"),
    ]:
        if find("noteTargets", f'targetTicketId[eq]:"{tickets[ref]}"'):
            continue  # this ticket already has its note
        nid = call("POST", "/rest/notes", {"title": title, "bodyV2": {"markdown": body_md}})["data"]["createNote"]["id"]
        call("POST", "/rest/noteTargets", {"noteId": nid, "targetTicketId": tickets[ref]})
    print("notes: 2")

    cat = [("RETAIL", "Order issue", ["Wrong item", "Late delivery"]), ("RETAIL", "Returns and refunds", ["Refund status", "Return request"]),
           ("HEALTH", "Appointments", ["Book or reschedule", "Cancellation"]), ("HEALTH", "Billing", ["Invoice query", "Insurance claim"]),
           ("REAL_ESTATE", "Property enquiry", ["Viewing request", "Pricing"]), ("REAL_ESTATE", "Maintenance", ["Repair request", "Urgent issue"]),
           ("BANKING", "Cards", ["Card blocked", "Lost or stolen"]), ("BANKING", "Account access", ["Password reset", "Locked account"]),
           ("GOVERNMENT", "Applications", ["Status check", "Missing documents"]), ("GOVERNMENT", "Complaints", ["Service delay", "Staff conduct"])]
    n = 0
    for sector, category, subs in cat:
        for sub in subs:
            label = f"{sector} / {category} / {sub}"
            upsert("catalogEntries", "CatalogEntry", f'name[eq]:"{label}"',
                   {"name": label, "sector": sector, "category": category, "subCategory": sub})
            n += 1
    print(f"catalog entries: {n}")

    srs = {}
    for ref, body in [
        ("SR-0001", {"name": "Customer cannot access account", "sector": "BANKING", "category": "Account access",
                     "subCategory": "Password reset", "description": "Caller locked out after three attempts.",
                     "status": "OPEN", "priority": "HIGH", "channel": "PHONE", "externalReference": "INVOQ-INT-48213"}),
        ("SR-0002", {"name": "Wrong item delivered", "sector": "RETAIL", "category": "Order issue", "subCategory": "Wrong item",
                     "status": "OPEN", "priority": "MEDIUM", "channel": "PHONE", "contactId": people["noor"], "accountId": uw}),
        ("SR-0003", {"name": "Card blocked abroad", "sector": "BANKING", "category": "Cards", "subCategory": "Card blocked",
                     "status": "OPEN", "priority": "URGENT", "channel": "PHONE"}),
        ("SR-0000", {"name": "testing record 1", "sector": "HEALTH", "status": "OPEN"}),
    ]:
        srs[ref] = upsert("serviceRequests", "ServiceRequest", f'referenceNumber[eq]:"{ref}"', {"referenceNumber": ref, **body})
    print(f"service requests: {len(srs)}")

    n = 0
    for name, typ, dirn, when, dur, summary, outcome, link in [
        ("Damaged item call", "CALL", "INBOUND", "2026-11-04T06:10:00.000Z", 310, "Customer reported a damaged item.", "FOLLOW_UP_NEEDED", ("ticketId", tickets["TKT-0001"])),
        ("Refund email", "EMAIL", "INBOUND", "2026-11-04T07:00:00.000Z", None, "Customer asked about a refund.", "FOLLOW_UP_NEEDED", ("ticketId", tickets["TKT-0002"])),
        ("Refund call", "CALL", "OUTBOUND", "2026-11-05T08:15:00.000Z", 180, "Refund status explained.", "RESOLVED", ("ticketId", tickets["TKT-0002"])),
        ("Delivery tracking chat", "CHAT", "INBOUND", "2026-11-05T09:30:00.000Z", None, "Customer asked where the delivery is.", "RESOLVED", ("ticketId", tickets["TKT-0003"])),
        ("Wrong size call", "CALL", "INBOUND", "2026-11-06T07:30:00.000Z", 420, "Customer received the wrong size. Exchange arranged.", "FOLLOW_UP_NEEDED", ("ticketId", tickets["TKT-0004"])),
        ("Exchange confirmation email", "EMAIL", "OUTBOUND", "2026-11-06T10:00:00.000Z", None, "Exchange confirmed by email.", "RESOLVED", ("ticketId", tickets["TKT-0004"])),
        ("Missing item email", "EMAIL", "INBOUND", "2026-11-07T06:45:00.000Z", None, "Customer reported a missing item.", "FOLLOW_UP_NEEDED", ("ticketId", tickets["TKT-0005"])),
        ("Late delivery call", "CALL", "INBOUND", "2026-11-07T11:20:00.000Z", 260, "Customer called about a late delivery.", "ESCALATED", ("ticketId", tickets["TKT-0006"])),
        ("Test call", "CALL", "INBOUND", "2026-11-11T08:00:00.000Z", 60, "Test interaction.", "RESOLVED", ("ticketId", tickets["TKT-0030"])),
        ("Account access call", "CALL", "INBOUND", "2026-11-12T07:00:00.000Z", 240, "Caller locked out after three attempts.", "FOLLOW_UP_NEEDED", ("serviceRequestId", srs["SR-0001"])),
        ("Password reset email", "EMAIL", "OUTBOUND", "2026-11-12T07:30:00.000Z", None, "Password reset steps sent.", "RESOLVED", ("serviceRequestId", srs["SR-0001"])),
        ("Wrong item chat", "CHAT", "INBOUND", "2026-11-12T09:00:00.000Z", None, "Customer reported the wrong item.", "FOLLOW_UP_NEEDED", ("serviceRequestId", srs["SR-0002"])),
    ]:
        body = {"name": name, "interactionType": typ, "direction": dirn, "occurredAt": when, "summary": summary,
                "outcome": outcome, link[0]: link[1]}
        if dur:
            body["durationSeconds"] = dur
        upsert("interactions", "Interaction", f'name[eq]:"{name}"', body)
        n += 1
    print(f"interactions: {n}")


# ---------- roles (section 21.5; 'Admin' and 'Member' come with Twenty)
def roles():
    have = {r["label"] for r in gql("{ getRoles { id label } }")["getRoles"]}
    for label, icon, desc, upd, dele in [("Agent", "IconHeadset", "Contact center agent: see and edit, no delete", True, False),
                                         ("Supervisor", "IconUserStar", "Team lead: see, edit and delete", True, True)]:
        if label in have:
            continue
        gql("mutation($i: CreateRoleInput!){ createOneRole(createRoleInput:$i){ id } }", {"i": {
            "label": label, "icon": icon, "description": desc, "canReadAllObjectRecords": True,
            "canUpdateAllObjectRecords": upd, "canSoftDeleteAllObjectRecords": dele, "canDestroyAllObjectRecords": False,
            "canUpdateAllSettings": False, "canBeAssignedToUsers": True, "canBeAssignedToApiKeys": False,
            "canBeAssignedToAgents": False}})
        print("created role", label)
    print("roles ok")


if __name__ == "__main__":
    step = sys.argv[1] if len(sys.argv) > 1 else "all"
    if step in ("schema", "all"):
        schema()
    if step in ("records", "all"):
        records()
    if step in ("roles", "all"):
        roles()
