# Research Heuristics

Reference guide for source evaluation, query refinement, and format-specific extraction.

## Source Authority Tiers

Use this rubric when scoring candidate sources during Phase 1.

| Tier | Source Type | Examples | Trust Level |
|------|-----------|----------|-------------|
| **S** | Official docs, specs, RFCs, primary data | MDN, W3C, IETF RFCs, language specs, framework official docs, academic papers, original benchmarks | Cite directly. Highest confidence. |
| **A** | Expert practitioner content | Smashing Magazine, CSS-Tricks, Martin Fowler, Kent C. Dodds, Dan Abramov, Julia Evans, framework core team blogs, major conference talks | Strong signal. Cross-reference when possible. |
| **B** | Quality community content | Top dev.to posts, accepted Stack Overflow answers, well-maintained GitHub discussions, popular YouTube tutorials with code | Good supporting evidence. Verify claims independently. |
| **C** | General blogs, tutorials | Medium posts, random tutorials, older articles (2+ years), self-promotional content | Use sparingly. Never as sole source for a claim. |
| **D** | AI-generated, aggregator, filler | Content farms, SEO-optimized posts with no original analysis, "Top 10 Best" listicles | **Discard immediately.** Do not cite. |

**Minimum bar**: Every report should cite at least **1 S-tier** and **2 A-tier** sources. If this isn't achievable, explicitly flag it: "No official documentation found for this topic."

## Query Refinement Patterns

When initial searches don't yield quality results, apply these transformations:

### Too Broad → Narrow Down
```
Before: "React state management"
After:  "React state management 2026 comparison benchmark"
After:  site:github.com "react state" stars:>1000
After:  "zustand vs jotai vs valtio" performance
```

### Too Narrow → Open Up
```
Before: "Next.js 16.2.3 app router middleware caching edge"
After:  "Next.js app router middleware caching"
After:  "Next.js edge middleware patterns"
```

### All Marketing → Find Signal
```
Before: "Supabase features"
After:  "Supabase production issues" OR "Supabase postmortem"
After:  "migrating from Supabase" lessons learned
After:  site:news.ycombinator.com "supabase"
```

### No Results → Try Adjacent Terms
```
Before: "CSS container queries responsive"
After:  "CSS containment layout" OR "@container" real-world examples
After:  site:codepen.io "container queries"
```

### Dev-Specific Queries
```
# GitHub ecosystem health
repo:{owner}/{name} stars issues contributors "last commit"
# npm package evaluation
"{package}" bundle size downloads weekly
site:bundlephobia.com "{package}"
# Migration experience
"migrating from {A} to {B}" OR "switched from {A} to {B}" experience
# Performance benchmarks
"{framework}" benchmark throughput latency 2025 2026
```

## Dev-Specific Research Angles

When evaluating frameworks, libraries, or tools, always investigate:

| Angle | What to Look For | How to Find It |
|-------|-----------------|----------------|
| **Ecosystem health** | Stars, commit frequency, open issues, contributor count | `search_repositories`, GitHub repo page |
| **Bundle impact** | Package size, tree-shaking support, dependency count | bundlephobia.com, `package.json` inspection |
| **TypeScript support** | Native TS, @types package, type quality | GitHub source inspection, DefinitelyTyped |
| **DX signals** | Error messages quality, docs quality, editor integration | Try it / read issues labeled "DX" |
| **Migration stories** | Real-world adoption experiences, pain points | HN, Reddit, dev.to "migrating from X" |
| **Performance data** | Benchmarks, Lighthouse scores, cold start times | Official benchmarks, independent comparisons |
| **Community signals** | Discord/Slack activity, SO answer rate, conference presence | Community links, SO tag stats |

## Binary & Protected Format Extraction

### DOCX Files
```bash
# Quick text extraction via unzip + sed
unzip -p document.docx word/document.xml | sed -e 's/<[^>]*>//g'
```

For complex layouts, use a Python script:
```python
import zipfile
from xml.etree import ElementTree

def extract_docx(path):
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml")
    tree = ElementTree.fromstring(xml)
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    return "\n".join(t.text for t in tree.iter(f'{{{ns["w"]}}}t') if t.text)
```

### PDF Files
- `read_url_content` handles many PDFs natively
- For local PDFs, use `pdftotext` if available

### Cloudflare-Protected Sites
- Use `browser_subagent` to render and screenshot
- Extract text content via the browser's DOM reading tools
- As a fallback, `tavily_extract` with `extract_depth: "advanced"` often works

### Always Verify
After any binary extraction, check the first 20 lines of output to confirm quality before proceeding with analysis.
