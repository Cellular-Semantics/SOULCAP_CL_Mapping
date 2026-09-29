# Setup

Full setup for this repository. The [README](../README.md#quick-start) has the short version.

## Setup

### 1. Clone this repo

### 2. Install UV and create the environment

Install [UV](https://docs.astral.sh/uv/), then use it to create a virtual
environment with the project dependencies:

```bash
# Install UV (macOS / Linux)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create the virtual environment and install dependencies
uv sync
```

### 2. MCP servers (Claude Code)

The MCP servers used by this project — `Asta_semanticscholar` (literature
search), `artl-mcp`, and `ols4` — are defined in the committed
[.mcp.json](../.mcp.json) and enabled for the project in the committed
`.claude/settings.json`. No per-developer action is needed to enable them.

### 3. Configure the Asta API token

The [Asta](https://allenai.org/asta/resources/mcp) tools require a personal API
key. Request one from <https://allenai.org/asta/resources/mcp>, then add it to
your **local, gitignored** Claude Code settings at
`.claude/settings.local.json`:

```json
{
  "env": {
    "ASTA_API_KEY": "{token}"
  }
}
```

Replace `{token}` with your actual key. Claude Code reads this `env` block at
startup and expands `${ASTA_API_KEY}` into the `x-api-key` header in
[.mcp.json](../.mcp.json).

`.claude/settings.local.json` is gitignored and must **never** be committed —
it is the only place the secret lives. Restart Claude Code after editing it so
the key is picked up.

### Optional: PubMed (NCBI E-utilities)

`soulcap-pubmed` (`src/soulcap_cl_mapping/pubmed_search.py`) works keyless,
same as `soulcap-europepmc`. An NCBI API key just raises the rate limit from
3 to 10 requests/second. If you want one, generate it from your
[NCBI account settings](https://www.ncbi.nlm.nih.gov/account/settings/) under
**API Key Management**, then add it to the **local, gitignored** `.env`:

```
PUBMED_API_KEY={token}
```

Unlike `ASTA_API_KEY`, this is read directly by Python (via `python-dotenv`),
not through Claude Code's MCP `env` substitution — it isn't an MCP server key.
