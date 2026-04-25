# OSINT Skill

A portable, opinionated OSINT skill for AI assistants. Drop into Claude Code, OpenCode, or any agent runtime that loads `SKILL.md` files. Designed as a hardened replacement for [Steffen025's PAI OSINT skill](https://smithery.ai/skills/steffen025/osint), with no PAI dependency.

## What's different from Steffen025's version

| | Steffen025 OSINT | This skill |
|---|---|---|
| **Runtime requirement** | Requires PAI scaffolding | Stand-alone; PAI integration optional |
| **Disambiguation** | Implicit | Explicit gate before any reporting |
| **Confidence grading** | Not formalized | Mandatory A/B/C/D rubric on every claim |
| **Output** | Markdown only | Markdown dossier + structured `findings.json` sidecar |
| **Depth** | One mode | Tiered: Quick / Standard / Deep with budgets |
| **B2B prospecting** | Not covered | First-class workflow (`b2b-account.md`) |
| **Ethics layer** | Separate file | Inline gate + dedicated reference, with decline-it list |
| **Voice notification** | Hard-coded `localhost:8888` hook | Removed |
| **Tool fan-out** | Apify-centric | Graceful degradation: works with `web_search` + `web_fetch` alone, scales up to dig/whois/crt.sh/Shodan/etc. when present |

The two skills are not interchangeable; this one is more disciplined about identity confusion and source independence, and it produces auditable output.

## Layout

```
osint/
├── SKILL.md                       # Orchestrator — this is what the runtime loads
├── README.md                      # You are here
├── references/
│   ├── disambiguation.md          # How to avoid conflating namesakes
│   ├── confidence-grading.md      # A/B/C/D rubric and worked examples
│   ├── ethics-and-scope.md        # What's allowed, what isn't, what to decline
│   └── search-operators.md        # Google / GitHub / DNS / WHOIS / CT cheatsheet
├── workflows/
│   ├── person.md                  # Investigate an individual
│   ├── company.md                 # General company research
│   ├── b2b-account.md             # B2B prospect / account research (sales use)
│   ├── domain.md                  # Domain & infrastructure footprint (passive)
│   └── due-diligence.md           # Investment / partnership / vendor diligence
├── templates/
│   ├── dossier.md                 # Markdown report skeleton
│   └── findings.schema.json       # JSON Schema 2020-12 for the sidecar
└── scripts/
    ├── osint-capabilities.sh      # Probe local env (binaries, env keys, network)
    └── domain-footprint.sh        # Passive recon: whois + DNS + CT + Wayback + stack
```

## Install

### Claude Code

```bash
mkdir -p ~/.claude/skills
cp -r osint ~/.claude/skills/
chmod +x ~/.claude/skills/osint/scripts/*.sh
```

Then in Claude Code, invoke any OSINT-flavored prompt and the skill should auto-load. To verify:

```
You: probe my OSINT environment
```

Claude should run `scripts/osint-capabilities.sh` and report.

### OpenCode

```bash
mkdir -p ~/.config/opencode/skills
cp -r osint ~/.config/opencode/skills/
chmod +x ~/.config/opencode/skills/osint/scripts/*.sh
```

### PAI / Steffen025 replacement

Drop in over the existing OSINT skill directory:

```bash
# back up first
mv ~/.opencode/skills/OSINT ~/.opencode/skills/OSINT.bak.$(date +%Y%m%d)
cp -r osint ~/.opencode/skills/OSINT
chmod +x ~/.opencode/skills/OSINT/scripts/*.sh
```

PAI's voice-notification hook is not invoked. If you want it back, add it to your local `SKILL.md` — it's intentionally not in the portable version.

## Optional API keys

The skill works with zero credentials. These improve reach when present:

| Env var | What it adds |
|---|---|
| `GITHUB_TOKEN` | Higher GitHub search rate limits, code search for tech stack inference |
| `BRAVE_API_KEY` | Independent search engine fan-out |
| `SHODAN_API_KEY` | Read-only host posture for the domain workflow |
| `HUNTER_API_KEY` | Email pattern lookup for B2B account workflow |
| `SECURITYTRAILS_API_KEY` | Historical DNS / passive DNS for domain workflow |
| `VIRUSTOTAL_API_KEY` | Threat reputation pivots |
| `URLSCAN_API_KEY` | Public scan history for domains |
| `APIFY_TOKEN` | Optional — enables PAI-style scraper jobs if you have them |

The skill never sends keys to the model context. Scripts read them from the environment at runtime only.

## Try it

After install, prompts that should route to this skill:

- `Run a Standard OSINT pass on Avenir Senior Living for a B2B vendor pitch.`
- `Quick OSINT: who is the current CTO at Acme Corp?`
- `Domain footprint for example.com — passive only.`
- `Due-diligence-grade research on Acme Corp for a $2M vendor contract.`

The skill will:

1. Walk the Four Gates (scope, disambiguation, source independence, confidence).
2. Pick a workflow.
3. Produce `<target-slug>-dossier.md` and `<target-slug>-findings.json`.

## Philosophy

- **Identity confusion is the #1 OSINT failure.** This skill makes you prove you have the right person/company before reporting anything.
- **Repetition is not corroboration.** Source independence is graded explicitly.
- **Negative findings are findings.** Empty-handed sweeps go in the report.
- **The skill is the orchestrator.** Tools are workers. The agent does the thinking.
- **Public sources only.** No paid breach data. No social engineering. No active probing without authorization.

## License

MIT. Provided as-is. Use it on yourself first to see what it surfaces.
