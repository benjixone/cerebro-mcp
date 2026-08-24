# cerebro-mcp

Government tenders, contract awards and pre-tender pipelines from 21 official sources, served to Claude (or any MCP client) as native tools.

Governments are the biggest customer on Earth: around $13 trillion a year in public procurement (World Bank estimate, roughly 12% of global GDP). They buy cleaning, construction, HVAC, software, consulting, media, catering, security, everything. Most of it is published in fragmented national portals that nobody has time to watch.

Dashboards show everyone the same list. Your agent knows your company. Connect Cerebro and Claude screens the market against your actual capabilities, tells you which contracts you can win, shows you who keeps winning them, and drafts the go/no-go brief.

## Coverage

| Region | Sources |
|---|---|
| EU (all 27 countries) | TED |
| France | BOAMP, DECP awards, APProch pre-tender purchase pipeline |
| Spain | PLACSP |
| Monaco | Journal de Monaco, Mairie de Monaco |
| United States | SAM.gov federal opportunities (~80k active), USAspending awards |
| Multilateral | World Bank, UNDP |
| South America | Brazil PNCP, Colombia SECOP, Chile ChileCompra, Argentina COMPR.AR, Uruguay ARCE, Guyana NPTAB, Peru, Ecuador and Paraguay |

Values are normalized to EUR (ECB rates), cross-portal duplicates are folded, data refreshes daily. A grants/funding lane (EU Funding & Tenders calls) is next.

## Quickstart

1. Get a free API key (20 queries/day), straight from your terminal:

```bash
curl -X POST https://cerebro.benjix.com/api/subscribe -H 'Content-Type: application/json' -d '{"email":"you@company.com"}'
```

2. Clone and connect. Claude Code:

```bash
git clone https://github.com/benjixone/cerebro-mcp
claude mcp add cerebro --env CEREBRO_API_KEY=crb_yourkey -- python3 ./cerebro-mcp/server.py
```

Claude Desktop (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "cerebro": {
      "command": "python3",
      "args": ["/absolute/path/to/cerebro-mcp/server.py"],
      "env": {"CEREBRO_API_KEY": "crb_yourkey"}
    }
  }
}
```

Requires Python 3.8+. No dependencies, nothing to install, no telemetry: the server is one readable file and your key is sent only to cerebro.benjix.com.

## Tools

| Tool | What it does |
|---|---|
| `search_tenders` | Search open tenders, pre-tender pipeline signals or awards by text, country (ISO alpha-3), CPV code, source and deadline status |
| `search_awards` | Who wins which contracts, for how much: competitor and incumbent intelligence, partial winner-name matching |
| `get_tender` | Full detail for one notice, including raw metadata and links to the same contract on other portals |

Prompts that work well:

- "Find open HVAC maintenance tenders in France above 500k EUR closing in the next 30 days"
- "Who keeps winning energy performance contracts in Spain? List the top incumbents"
- "Check the pre-tender pipeline for cleaning services around Paris and brief me on what is coming"
- "Read our capability deck, then screen this week's new tenders and shortlist the 3 we should bid"

## Pricing

| Tier | Price | Included |
|---|---|---|
| Free | 0 | 20 queries/day |
| Founding | 49 EUR/month | Unlimited queries, first 50 seats only, price locked while subscribed |
| Pro | 99 EUR/month | Unlimited queries |

To upgrade: email ben@benjix.com with subject "Cerebro founding". Stripe checkout links land here shortly.

## Data and licensing

All data originates from official government portals and public procurement APIs, each published under its own open-data license (TED reuse policy, French Licence Ouverte, US public domain, national open-data licenses). Cerebro adds aggregation, deduplication, EUR normalization and entity folding. Lanes built on commercial marketplaces (asset auctions, businesses for sale) are visible in the Cerebro dashboard but are not part of the API product.

## Status

Public beta. Best effort, no SLA yet. Issues and feature requests: open a GitHub issue.

## License

MIT.
