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

## Quickstart (nothing to install)

1. Pick a seat at **[cerebroradar.com/connect](https://cerebroradar.com/connect)**: Stripe checkout, your personal link is issued right after payment. Want a test drive first? Email ben@benjix.com for a 20-query demo key.
2. Connect it:

```bash
claude mcp add --transport http cerebro https://cerebroradar.com/mcp/YOUR_KEY
```

On claude.ai or Claude Desktop: Settings, Connectors, "Add custom connector", name it Cerebro, paste your link. Cursor, Copilot, Gemini CLI and any MCP client: add a remote MCP server with your link as the URL.

## Run it locally instead (optional)

This repo is the identical server as a local stdio process, one stdlib Python file, no dependencies, no telemetry, your key is sent only to cerebroradar.com:

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
| Demo | 0 | 20 queries, one time, by request: ben@benjix.com |
| Founding | [7 days free, then 49 EUR every 4 weeks](https://buy.stripe.com/bJe4gzcQb47wfKk9671RC00) | Unlimited queries, first 50 seats only, price locked while subscribed |
| Pro | [7 days free, then 99 EUR every 4 weeks](https://buy.stripe.com/00w28rdUf33sfKk9671RC01) | Unlimited queries |

Pay with the same email your key is registered to and the same connection link upgrades instantly, nothing to reinstall. Questions: ben@benjix.com.

## Data and licensing

All data originates from official government portals and public procurement APIs, each published under its own open-data license (TED reuse policy, French Licence Ouverte, US public domain, national open-data licenses). Cerebro adds aggregation, deduplication, EUR normalization and entity folding. Lanes built on commercial marketplaces (asset auctions, businesses for sale) are visible in the Cerebro dashboard but are not part of the API product.

## Status

Public beta. Best effort, no SLA yet. Issues and feature requests: open a GitHub issue.

## License

MIT.
