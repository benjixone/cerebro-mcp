#!/usr/bin/env python3
"""cerebro-mcp: government tenders, awards and funding as an MCP server.

Stdio MCP server, pure Python stdlib, no dependencies. Backed by the Cerebro
aggregation API (21 official procurement feeds, EU + US + Latin America + MFIs).

Config via environment:
  CEREBRO_API_KEY   required, get a free key: see README
  CEREBRO_API_URL   optional, defaults to https://cerebro.benjix.com
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

API_URL = os.environ.get("CEREBRO_API_URL", "https://cerebroradar.com").rstrip("/")
API_KEY = os.environ.get("CEREBRO_API_KEY", "")
VERSION = "0.1.0"
SUPPORTED_PROTOCOLS = {"2024-11-05", "2025-03-26", "2025-06-18"}
GET_KEY_HINT = ("No CEREBRO_API_KEY set. Get your key at " + API_URL + "/connect "
                "(subscription, issued right after checkout), or email ben@benjix.com "
                "for a 20-query demo key.")

KEEP_FIELDS = ("id", "source", "kind", "country", "buyer", "title", "title_en",
               "category", "cpv", "value_eur", "value_amount", "value_currency",
               "deadline", "published", "url", "city", "winner", "procedure_type",
               "tenders_received")

TOOLS = [
    {
        "name": "search_tenders",
        "description": (
            "Search government procurement notices across the EU (all 27 countries via TED, "
            "plus French and Spanish national portals), US federal (SAM.gov), World Bank, UNDP, "
            "Monaco and 8 South American countries. kind='tender' finds open/announced calls "
            "for bids, 'pipeline' finds pre-tender signals (buyer purchase plans), 'award' "
            "finds concluded contracts. Values are normalized to EUR in value_eur. "
            "Start broad with query alone, then narrow."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Full-text search over title, buyer and winner. A bare numeric string is treated as a CPV code prefix."},
                "kind": {"type": "string", "enum": ["tender", "award", "pipeline", "modification"], "description": "Notice type, default tender."},
                "country": {"type": "string", "description": "ISO alpha-3 country code, e.g. FRA, ESP, USA, BRA, COL."},
                "source": {"type": "string", "description": "Restrict to one feed: ted, boamp, decp, approch, placsp, jdm, mairiemc, sam, usaspending, worldbank, undp, pncp, colombia, chile, argentina, uruguay, guyana, peru, ecuador, paraguay."},
                "cpv": {"type": "string", "description": "CPV code prefix (EU procurement taxonomy), e.g. 71314 for energy services."},
                "open_only": {"type": "boolean", "description": "Only tenders still open for bidding (deadline in the future, or recent MFI notices without a published deadline)."},
                "sort": {"type": "string", "enum": ["newest", "deadline", "value", "published"], "description": "Sort order, default newest (first seen)."},
                "limit": {"type": "integer", "description": "Max results, 1-50, default 20."},
                "offset": {"type": "integer", "description": "Pagination offset."},
            },
        },
    },
    {
        "name": "search_awards",
        "description": (
            "Contract-award intelligence: who won which government contracts, for how much. "
            "Use to research competitors, find winning incumbents before bidding, size a "
            "market, or find likely partners/subcontractors in a niche. winner accepts a "
            "partial company name."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Full-text search over title, buyer and winner."},
                "winner": {"type": "string", "description": "Partial winner company name, e.g. 'Dalkia'."},
                "country": {"type": "string", "description": "ISO alpha-3 country code."},
                "cpv": {"type": "string", "description": "CPV code prefix."},
                "sort": {"type": "string", "enum": ["newest", "value", "published"], "description": "Default published (most recent awards first)."},
                "limit": {"type": "integer", "description": "Max results, 1-50, default 20."},
                "offset": {"type": "integer", "description": "Pagination offset."},
            },
        },
    },
    {
        "name": "get_tender",
        "description": "Fetch one notice by its Cerebro id (from a search result), including the raw extra metadata and links to the same contract on other portals.",
        "inputSchema": {
            "type": "object",
            "properties": {"id": {"type": "integer", "description": "Cerebro notice id."}},
            "required": ["id"],
        },
    },
]


def api_get(params):
    if not API_KEY:
        raise RuntimeError(GET_KEY_HINT)
    clean = {k: v for k, v in params.items() if v not in (None, "", False)}
    url = API_URL + "/api/notices?" + urllib.parse.urlencode(clean)
    req = urllib.request.Request(url, headers={"X-API-Key": API_KEY,
                                               "User-Agent": f"cerebro-mcp/{VERSION}"})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            msg = json.loads(e.read().decode("utf-8")).get("error", "")
        except Exception:
            msg = ""
        raise RuntimeError(f"Cerebro API error {e.code}: {msg or e.reason}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Cerebro API unreachable: {e.reason}")


def trim(row):
    out = {}
    for k in KEEP_FIELDS:
        v = row.get(k)
        if k != "id" and v in (None, "", 0):
            continue
        if k == "value_eur" and isinstance(v, (int, float)):
            v = round(v)
        out[k] = v
    return out


def t_search_tenders(a):
    p = {"q": a.get("query"), "kind": a.get("kind") or "tender",
         "country": (a.get("country") or "").upper(), "source": a.get("source"),
         "cpv": a.get("cpv"), "sort": a.get("sort") or "newest",
         "offset": a.get("offset")}
    if a.get("open_only"):
        p["open"] = "1"
    data = api_get(p)
    limit = max(1, min(int(a.get("limit") or 20), 50))
    rows = [trim(r) for r in data.get("notices", [])[:limit]]
    out = {"total_matches": data.get("total"), "returned": len(rows), "results": rows}
    if data.get("total") == -1:
        out["total_matches"] = "unchanged (see first page)"
    return out


def t_search_awards(a):
    a = dict(a or {})
    a["kind"] = "award"
    a.setdefault("sort", "published")
    p = {"q": a.get("query"), "kind": "award", "country": (a.get("country") or "").upper(),
         "cpv": a.get("cpv"), "sort": a.get("sort"), "offset": a.get("offset"),
         "winner_like": a.get("winner")}
    data = api_get(p)
    limit = max(1, min(int(a.get("limit") or 20), 50))
    rows = [trim(r) for r in data.get("notices", [])[:limit]]
    return {"total_matches": data.get("total"), "returned": len(rows), "results": rows}


def t_get_tender(a):
    data = api_get({"id": int(a["id"]), "dupes": "1"})
    rows = data.get("notices", [])
    if not rows:
        return {"error": f"no notice with id {a['id']}"}
    row = rows[0]
    out = trim(row)
    if row.get("extra"):
        out["extra"] = str(row["extra"])[:1500]
    if row.get("alts"):
        out["also_published_on"] = row["alts"]
    return out


HANDLERS = {"search_tenders": t_search_tenders,
            "search_awards": t_search_awards,
            "get_tender": t_get_tender}


def rpc_result(mid, result):
    return {"jsonrpc": "2.0", "id": mid, "result": result}


def rpc_error(mid, code, message):
    return {"jsonrpc": "2.0", "id": mid, "error": {"code": code, "message": message}}


def handle(msg):
    method, mid = msg.get("method", ""), msg.get("id")
    if method == "initialize":
        proto = msg.get("params", {}).get("protocolVersion", "")
        return rpc_result(mid, {
            "protocolVersion": proto if proto in SUPPORTED_PROTOCOLS else "2025-06-18",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "cerebro", "version": VERSION},
            "instructions": (
                "Cerebro searches government tenders, contract awards and pre-tender "
                "pipelines across the EU, US, Latin America and MFIs (World Bank, UNDP). "
                "Values are normalized to EUR (value_eur), countries are ISO alpha-3. "
                "Typical flow: search_tenders with a broad query, narrow by country/cpv/"
                "open_only, then get_tender for detail and search_awards to see who wins "
                "similar contracts."),
        })
    if method == "ping":
        return rpc_result(mid, {})
    if method == "tools/list":
        return rpc_result(mid, {"tools": TOOLS})
    if method == "tools/call":
        params = msg.get("params", {})
        fn = HANDLERS.get(params.get("name", ""))
        if not fn:
            return rpc_error(mid, -32602, f"unknown tool: {params.get('name')}")
        try:
            out = fn(params.get("arguments") or {})
            return rpc_result(mid, {"content": [{"type": "text",
                                                 "text": json.dumps(out, ensure_ascii=False)}]})
        except Exception as e:
            return rpc_result(mid, {"content": [{"type": "text", "text": f"Error: {e}"}],
                                    "isError": True})
    if mid is None:
        return None  # unknown notification, ignore
    return rpc_error(mid, -32601, f"method not found: {method}")


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except ValueError:
            sys.stdout.write(json.dumps(rpc_error(None, -32700, "parse error")) + "\n")
            sys.stdout.flush()
            continue
        try:
            resp = handle(msg)
        except Exception as e:
            resp = rpc_error(msg.get("id"), -32603, f"internal error: {e}")
        if resp is not None:
            sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
