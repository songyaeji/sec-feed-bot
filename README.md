# sec-feed-bot

Security-news Discord notification bot. GitHub Actions runs `main.py`
every ~10 minutes (an external cron-job.org trigger calls
`workflow_dispatch` — see `docs/external-trigger.md`; the `*/20` cron
stays on as a fallback, since GitHub's scheduled cron is routinely
delayed by 1-3 hours): it fetches from CISA KEV, NVD, and RSS sources,
dedups against `state/seen.json`, and posts to a Discord channel via
webhook.

> Note: `config.yaml` has a comment at the top marking its source URLs
> as design-time candidates pending verification — see that file before
> relying on any specific feed URL.

## Hybrid notification mode

**Urgent** = national/global-impact incidents only (쿠팡·SKT급 대량 유출,
전국 통신망 마비 수준). Judged in two stages by `judge.py`:

1. **Keyword gate** (free) — only items whose title/summary matches an
   incident keyword in `config.yaml`'s `urgent_gate` become candidates.
2. **LLM judge** (headless Claude, sonnet) — a 3-question checklist
   (actual ongoing incident? household-name victim? mass scale?) plus a
   1-5 impact `scale` self-rating; code drops anything below
   `urgent_min_scale` (default 5) as a second gate. Recently sent alerts
   (`state/urgent_history.json`, 14-day window) are fed back into the
   prompt so follow-up coverage of the same incident doesn't re-ring.
   Failures (no token, timeout, bad output) fail **quiet**: nothing is
   urgent, everything waits for the digest — in the urgent channel a
   false alarm at 3am is worse than hearing about it at 7am.

Urgent items go out immediately as an individual red Discord card with
the judge's one-line reason. Sources flagged `breaking: true` (HN,
Reddit, 국내 사건 속보) exist only to feed this pipeline: their
non-urgent items are dropped, not queued.

- **realtime** (every ~10 min): non-urgent items are queued into
  `state/pending.json` instead of being sent.
- **digest** (daily cron, KST 07:00): non-urgent items from this run are
  merged with everything queued in `pending.json`, run through the wiki
  librarian (kind + importance 1-5 rating + wiki ingest), and sent as the
  "Trend of Security" card-news carousel plus source links; then
  `pending.json` is emptied except unjudged items carried over.
  - News cards: incidents, law/policy changes and institution reports only
    (librarian `kind` incident/policy/institution, importance >= 3), at most
    7. The count varies by day: there is no backfill with raw feed items,
    so a slow day ships fewer cards (decision 2026-11-20).
  - Plain vulnerability advisories (librarian `kind` vuln, and the
    `vuln_advisory_sources` in `config.yaml`) go to the "오늘의 CVE" card,
    never to news cards.
  - Every card's Korean title, summary, SO WHAT line, term and tags are
    rewritten from the article body by `card_editor.py` and validated in
    code (Korean ratio, sentence style, term must be a security term and
    not a company or agency name, tags must be backed by the article).
    Items that fail validation are dropped, not sent in English.

`RUN_MODE` (env var, default `realtime`) selects the mode; the workflow
sets it automatically based on which cron fired (or the `workflow_dispatch`
input).

## Duplicate suppression

Three layers sit in front of notification, on top of the id-based dedup
against `state/seen.json`:

1. **Cross-source heuristic dedup** (`dedup.py`, always on) — catches the
   same event reported by a different outlet: an item is a duplicate if
   every CVE it mentions was already alerted, or (when it has no CVE) its
   normalized title is >=0.6 Jaccard-similar to a title alerted in the last
   7 days. State lives in `state/seen.json`'s `alerted_cves` (90-day TTL)
   and `recent_titles` (7-day TTL) fields.
2. **LLM wiki librarian** (`librarian.py`, digest mode only) — a headless
   Claude Code call that maintains `wiki/` (see `wiki/CLAUDE.md` for the
   page format) and flags in-batch and already-covered duplicates. Any
   failure (missing `CLAUDE_CODE_OAUTH_TOKEN`, timeout, bad output) does not
   stop the digest: candidates go straight to the rewrite and validation
   step.
3. **Published ledger** (`published_ledger.py`, `state/published.json`) —
   every card actually sent is recorded for 30 days. Before a digest, each
   news candidate is compared with the ledger: same event with no new fact
   is dropped, same event with a new fact is labelled 후속 (follow-up).
   URL matches are dropped deterministically; the rest is judged by an LLM
   call, and if that call fails, anything similar to a ledger entry is
   dropped (fail-closed). The CVE card drops URLs and CVE ids already sent.

## Wiki

The wiki is an event archive (incidents, law/policy, institution
reports). Pages under `wiki/topics/` are written by `librarian.py`;
`wiki_guard.py` then checks every new/update verdict has its page and a
timeline line with the item URL (and writes a minimal one if the librarian
did not), deletes stray files the run created outside the page format,
and rewrites `[[slug]]` links to `[[file-name]]` so the folder opens as an
Obsidian vault. `wiki/INDEX.md` (last 60 days) and `wiki/INDEX-archive.md`
are regenerated from the pages by `wiki_index.py` on every digest; see
`wiki/CLAUDE.md` for the frontmatter/timeline format if editing by hand.

## Trend pick

`category: trend` sources feed a separate daily message sent right after
the card news. `trend_lane._select_trend` builds a candidate pool and
`trend_enrich.pick` (one LLM call) chooses at most 2 items worth reading
that day, writing a Korean title and a one-line Korean reason. If the call
fails nothing is sent and the candidates are retried the next morning;
English titles are never shown.

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

4. **(Recommended) External realtime trigger**
   - GitHub's scheduled cron is delayed 1-3 hours in practice, which kills
     urgent-alert latency. Set up cron-job.org to call `workflow_dispatch`
     every 10 minutes with a fine-grained PAT — full steps in
     `docs/external-trigger.md`.

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
