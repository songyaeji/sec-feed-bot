# sec-feed-bot

Security-news Discord notification bot. A GitHub Actions cron job runs
`main.py` every 20 minutes: it fetches from CISA KEV, NVD, and RSS
sources, dedups against `state/seen.json`, and posts new items to a
Discord channel via webhook.

> Note: `config.yaml` has a comment at the top marking its source URLs
> as design-time candidates pending verification — see that file before
> relying on any specific feed URL.

## Hybrid notification mode

Every run classifies each new item as **urgent** or not
(`main.is_urgent`): urgent if its source is flagged `urgent: true` in
`config.yaml` (CISA KEV, KISA 보안공지), or CVSS >= 9.0, or KEV
(known-exploited). Urgent items always go out immediately as an
individual Discord card.

- **realtime** (`*/20 * * * *` cron): non-urgent items are queued into
  `state/pending.json` instead of being sent.
- **digest** (daily cron, KST 07:00): non-urgent items from this run are
  merged with everything queued in `pending.json` and sent as one
  category-grouped digest embed, then `pending.json` is emptied.

`RUN_MODE` (env var, default `realtime`) selects the mode; the workflow
sets it automatically based on which cron fired (or the `workflow_dispatch`
input).

## Duplicate suppression

Two layers sit in front of notification, on top of the id-based dedup
against `state/seen.json`:

1. **Cross-source heuristic dedup** (`dedup.py`, always on) — catches the
   same event reported by a different outlet: an item is a duplicate if
   every CVE it mentions was already alerted, or (when it has no CVE) its
   normalized title is >=0.6 Jaccard-similar to a title alerted in the last
   7 days. State lives in `state/seen.json`'s `alerted_cves` (90-day TTL)
   and `recent_titles` (7-day TTL) fields.
2. **LLM wiki librarian** (`librarian.py`, digest mode only) — a headless
   Claude Code call that maintains `wiki/` (see `wiki/CLAUDE.md` for the
   page format) and flags items that are already covered there so they're
   dropped from the digest. This layer is a nice-to-have: any failure
   (missing `CLAUDE_CODE_OAUTH_TOKEN`, timeout, bad output) fails **open**
   — the digest still sends everything, it just skips the wiki dedup pass.

## Wiki

`wiki/INDEX.md` lists every topic the librarian has created, each linking
to a page under `wiki/topics/`. Pages are auto-maintained by
`librarian.py` during digest runs; see `wiki/CLAUDE.md` for the
frontmatter/timeline format if editing by hand.

Requires the `CLAUDE_CODE_OAUTH_TOKEN` repo secret (see Setup below).
That token is valid for 1 year — re-issue it around 2027-07 or the
librarian will start fail-opening silently.

## Setup

1. **Create a Discord webhook**
   - In your target Discord server: Server Settings -> Integrations -> Webhooks -> New Webhook.
   - Pick the channel, copy the webhook URL.

2. **Register repo secrets**
   - In the GitHub repo: Settings -> Secrets and variables -> Actions -> New repository secret.
   - Add `DISCORD_WEBHOOK_URL` with the URL from step 1.
   - (Optional) Add `NVD_API_KEY` if you have an NVD API key — without it,
     the NVD source runs much slower due to public rate limits.
   - (Optional) Add `CLAUDE_CODE_OAUTH_TOKEN` to enable the wiki librarian
     (digest mode only; see Wiki section above). Without it, the librarian
     fails open and digests just skip the wiki dedup pass.

3. **Enable the workflow**
   - The workflow at `.github/workflows/collect.yml` runs on a `*/20 * * * *`
     cron schedule and can also be triggered manually via
     "Run workflow" (`workflow_dispatch`) in the Actions tab.

## Local testing

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# DRY_RUN prints collected/filtered items to stdout instead of posting
# to Discord, and does not write state/seen.json or state/pending.json
DRY_RUN=1 RUN_MODE=realtime python main.py
DRY_RUN=1 RUN_MODE=digest python main.py
```

To test an actual Discord post locally, export `DISCORD_WEBHOOK_URL`
and run `RUN_MODE=realtime python main.py` (or `RUN_MODE=digest`)
without `DRY_RUN`.
