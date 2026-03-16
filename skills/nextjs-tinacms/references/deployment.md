# Deployment & Hosting

This skill is opinionated for **Vercel + Tina Cloud**. Use Tina Cloud unless you have a specific reason not to. Self-hosted with Vercel KV is documented below as a secondary option.

## Development vs Production

| Mode | Backend | Content Storage | How |
|------|---------|----------------|-----|
| **Local dev** | Local GraphQL server | Filesystem (direct read/write) | `pnpm dev` (runs `tinacms dev -c "next dev"`) |
| **Production** | Tina Cloud | Git repo via Tina Cloud API | Vercel deployment with env vars |

Local dev needs no Tina Cloud credentials. The TinaCMS local server reads/writes content files directly. Production connects to Tina Cloud, which manages content through the GitHub API.

## Vercel Deployment

### Setup

1. Import repo in Vercel, set Framework to Next.js
2. Build command: `tinacms build && next build`
3. Add environment variables (see below)
4. Deploy

### Required Vercel Packages

Every Vercel project must include:

```bash
pnpm add @vercel/analytics @vercel/speed-insights
```

In root layout:
```tsx
import { Analytics } from '@vercel/analytics/next'
import { SpeedInsights } from '@vercel/speed-insights/next'

export default function RootLayout({ children }) {
  return (
    <html><body>
      {children}
      <Analytics />
      <SpeedInsights />
    </body></html>
  )
}
```

### Deploy Hooks

Create a Deploy Hook in Vercel project settings. Wire it to TinaCMS so content changes trigger rebuilds. Useful for static sites that don't use ISR.

### Preview Deployments

Vercel creates preview URLs for every branch. TinaCMS editorial workflow (Team Plus+) creates branches per editor, so each editor's draft gets its own preview URL.

Use Vercel Team Environment Variables to share common keys (`NEXT_PUBLIC_TINA_CLIENT_ID`, `TINA_TOKEN`) across preview and production environments.

## Tina Cloud (Default Backend)

Managed backend at `app.tina.io`. All tiers include unlimited repos and documents.

| Tier | Price | Users | Key Features |
|------|-------|-------|-------------|
| Free | $0 | 2 | Community support |
| Team | $29/mo | 3 (up to 10) | Team support |
| Team Plus | $49/mo | 5 (up to 20) | Editorial Workflow, AI Features |
| Business | $299/mo | 20 (unlimited) | 3 roles, API access |
| Enterprise | Custom | Custom | SSO, GitHub Enterprise |

**Vercel environment variables:**

```bash
NEXT_PUBLIC_TINA_CLIENT_ID=<from app.tina.io>
TINA_TOKEN=<read-only token>
NEXT_PUBLIC_TINA_BRANCH=main
```

**Editorial Workflow** (Team Plus+): Branch-based. Editors create branches from protected branches, a draft PR is auto-created, edits save to the branch, merging the PR publishes content. Pairs well with Vercel preview deployments.

**Content Search** (Tina Cloud only): Enable with `search.tina.indexerToken` from the dashboard. Fuzzy search enabled by default (Damerau-Levenshtein). Set `searchable: false` on fields to exclude from indexing.

## Self-Hosted Alternative (Vercel KV)

For full control over the backend. Uses three pluggable components:

1. **Database adapter:** Vercel KV (Upstash Redis) via `upstash-redis-level`
2. **Git provider:** GitHub via `tinacms-gitprovider-github`
3. **Auth provider:** AuthJS (NextAuth) via `tinacms-authjs` (seed credentials: admin/admin)

Scaffold: `npx @tinacms/cli@latest init backend`

```typescript
// tina/database.ts
import { createDatabase, createLocalDatabase } from '@tinacms/datalayer'
import { GitHubProvider } from 'tinacms-gitprovider-github'
import { RedisLevel } from 'upstash-redis-level'
import { Redis } from '@upstash/redis'

const isLocal = process.env.TINA_PUBLIC_IS_LOCAL === 'true'
const branch = process.env.GITHUB_BRANCH || process.env.VERCEL_GIT_COMMIT_REF || 'main'

export default isLocal
  ? createLocalDatabase()
  : createDatabase({
      gitProvider: new GitHubProvider({
        branch,
        owner: process.env.GITHUB_OWNER!,
        repo: process.env.GITHUB_REPO!,
        token: process.env.GITHUB_PERSONAL_ACCESS_TOKEN!,
      }),
      databaseAdapter: new RedisLevel<string, Record<string, any>>({
        redis: new Redis({
          url: process.env.KV_REST_API_URL!,
          token: process.env.KV_REST_API_TOKEN!,
        }),
        debug: process.env.DEBUG === 'true',
      }),
    })
```

**Self-hosted Vercel environment variables:**
```bash
TINA_PUBLIC_IS_LOCAL=false
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxx
GITHUB_OWNER=<owner>
GITHUB_REPO=<repo>
GITHUB_BRANCH=main
NEXTAUTH_SECRET=<random-secret>
KV_REST_API_URL=https://xxx.kv.vercel-storage.com
KV_REST_API_TOKEN=xxx
```

**Limitations:** No editorial workflow. No content search. Does NOT work in Edge Runtime (wontfix).

## Media Providers

One provider active at a time.

| Provider | Package | Best For |
|----------|---------|----------|
| **Repo-based** (default) | None (built-in) | Small sites, blogs |
| **Cloudinary** | `next-tinacms-cloudinary` | Media-heavy production sites |
| **Vercel Blob / S3** | `next-tinacms-s3` | Vercel-native or AWS infrastructure |

**Default (repo-based):**
```typescript
media: {
  tina: {
    mediaRoot: 'uploads',
    publicFolder: 'public',
  },
}
```

For Cloudinary or S3, add an API route and configure `images.remotePatterns` in `next.config.ts` for `next/image`.

## Build & Scripts

```json
{
  "scripts": {
    "dev": "tinacms dev -c \"next dev\"",
    "build": "tinacms build && next build",
    "start": "next start"
  }
}
```

## Dependency Management

Use RenovateBot or Dependabot with package grouping to keep TinaCMS versions synced:

```json
{
  "extends": ["config:recommended"],
  "packageRules": [
    { "matchPackagePatterns": ["tinacms", "@tinacms/*"], "groupName": "TinaCMS" },
    { "matchPackageNames": ["next"], "groupName": "Next.js" },
    { "matchPackageNames": ["react", "react-dom", "@types/react", "@types/react-dom"], "groupName": "React" }
  ]
}
```

## Official Starters

Use `npx create-tina-app@latest` or scaffold manually. The old `tina-cloud-starter` was archived (Oct 2025).

| Starter | Notes |
|---------|-------|
| **Tina NextJS Starter** | Full-featured: Tailwind, blocks, visual editing |
| **Barebones** | Minimal: `.md`/`.mdx`, no styling |
| **Self-Hosted Demo** | Vercel KV + Auth.js + GitHub |
