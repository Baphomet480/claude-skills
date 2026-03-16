# Visual Editing

## Server-Client Page Pattern

TinaCMS visual editing requires a two-component architecture:

1. **Server Component** -- fetches `{ data, query, variables }` from the Tina GraphQL client
2. **Client Component** -- calls `useTina()` to enable live editing, renders with `tinaField()` data attributes

```tsx
// app/[slug]/page.tsx -- Server Component
import { client } from '@/tina/__generated__/client'
import { PageClient } from './PageClient'

export default async function Page({
  params,
}: {
  params: Promise<{ slug: string }>  // Next.js 16: params is a Promise
}) {
  const { slug } = await params
  const result = await client.queries.page({ relativePath: `${slug}.md` })
  return (
    <PageClient
      query={result.query}
      variables={result.variables}
      data={result.data}
    />
  )
}
```

```tsx
// app/[slug]/PageClient.tsx -- Client Component
'use client'
import { useTina, tinaField } from 'tinacms/dist/react'
import { BlockRenderer } from '@/components/blocks/BlockRenderer'

export function PageClient(props: { query: string; variables: Record<string, any>; data: any }) {
  const { data } = useTina(props)
  const page = data.page

  return (
    <main>
      <h1 data-tina-field={tinaField(page, 'title')}>{page.title}</h1>
      {page.blocks && <BlockRenderer blocks={page.blocks} />}
    </main>
  )
}
```

**Key points:**
- No global `TinaProvider` needed (TinaCMS v2+)
- `useTina()` returns props.data unchanged in production -- zero overhead
- `useTina()` only subscribes to live updates in edit mode
- `tinaField()` must target DOM elements, not React wrapper components

## Draft Mode

Enable visual editing in deployed environments via Next.js Draft Mode:

```typescript
// app/api/preview/route.ts
import { draftMode } from 'next/headers'
import { redirect } from 'next/navigation'

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const slug = searchParams.get('slug') || '/'
  ;(await draftMode()).enable()  // Must await in Next.js 16
  redirect(slug)
}
```

Draft mode bypasses all caches. When `cacheComponents` is enabled, `"use cache"` directives are automatically skipped in draft mode.

## Contextual Editing Preview

Add `ui.router` on every content collection so editors see the live page alongside the form:

```typescript
ui: {
  router: ({ document }) => {
    if (document._sys.filename === 'home') return '/'
    return `/${document._sys.filename}`
  },
}
```

## Block Renderer

```tsx
import { tinaField } from 'tinacms/dist/react'

const blockComponentMap: Record<string, React.ComponentType<any>> = {
  PageBlocksHero: Hero,
  PageBlocksFeatures: Features,
  PageBlocksContent: Content,
  PageBlocksCtaBanner: CTABanner,
  PageBlocksFaq: FAQ,
}

export function BlockRenderer({ blocks }: { blocks: any[] }) {
  if (!blocks) return null
  return (
    <>
      {blocks.map((block, index) => {
        const Component = blockComponentMap[block.__typename]
        if (!Component) {
          console.warn(`Unknown block type: ${block.__typename}`)
          return null
        }
        return (
          <section key={index} data-tina-field={tinaField(block)}>
            <Component {...block} />
          </section>
        )
      })}
    </>
  )
}
```

**`__typename` format:** `{CollectionName}Blocks{TemplateName}` in PascalCase.

## Debugging Checklist

If click-to-edit is not working, check in order:

| # | Check | Fix |
|---|-------|-----|
| 1 | Draft mode enabled? | Visit `/api/preview` |
| 2 | Component is `"use client"`? | Add directive at top of file |
| 3 | `useTina()` called with `{ data, query, variables }`? | Pass all three from server component |
| 4 | `data-tina-field` on DOM elements? | Must be on HTML elements, not wrapper components |
| 5 | Tina dev server running? | Use `tinacms dev -c "next dev"`, not `next dev` alone |
| 6 | Types generated and current? | Run `tinacms build` to regenerate `tina/__generated__/` |
| 7 | `ui.router` set on collection? | Required for contextual editing preview |

## Caching with Visual Editing

Next.js 16 uses `"use cache"` (requires `cacheComponents: true` in `next.config.ts`):

```typescript
import { cacheLife } from 'next/cache'

async function getPage(slug: string) {
  'use cache'
  cacheLife('hours')
  const { data } = await client.queries.page({ relativePath: `${slug}.md` })
  return data
}
```

**Preset profiles:**

| Profile | Stale | Revalidate | Expire |
|---------|-------|-----------|--------|
| `seconds` | 30s | 1s | 1 min |
| `minutes` | 5 min | 1 min | 1 hour |
| `hours` | 5 min | 1 hour | 1 day |
| `days` | 5 min | 1 day | 1 week |
| `weeks` | 5 min | 1 week | 30 days |
| `max` | 5 min | 30 days | 1 year |

**Custom profile** in `next.config.ts`:
```typescript
const nextConfig: NextConfig = {
  cacheComponents: true,
  cacheLife: {
    editorial: { stale: 600, revalidate: 3600, expire: 86400 },
  },
}
```

**Constraints:** Cannot access `cookies()`, `headers()`, or `searchParams` inside a cached scope. Read them outside and pass as arguments.

**Vercel Data Cache warning:** Vercel can cache TinaCloud API responses for up to 1 year, causing stale content. Add `revalidate` to queries:

```typescript
const result = await client.queries.page(
  { relativePath: `${slug}.md` },
  { fetchOptions: { next: { revalidate: 60 } } }
)
```

**On-demand revalidation:**
- `revalidateTag(tag, profile)` -- SWR behavior (new in 16: requires cacheLife profile as second arg)
- `updateTag(tag)` -- Server Actions only, read-your-writes (user sees changes immediately)

## proxy.ts (replaces middleware.ts)

Lives at project root. Runs Node.js runtime only (no Edge).

```typescript
// proxy.ts
import type { NextRequest } from 'next/server'
import { NextResponse } from 'next/server'

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Protect admin in production
  if (pathname.startsWith('/admin') && process.env.NODE_ENV === 'production') {
    // Add auth check here
  }

  // Redirect old URLs
  if (pathname === '/old-page') {
    return NextResponse.redirect(new URL('/new-page', request.url), 301)
  }
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
}
```

**Migrate:** `npx @next/codemod@canary middleware-to-proxy .`

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| `useTina` in Server Components | Client Component wrapper |
| Generic wrapper components | Purpose-built components accepting Tina types |
| `tinaField` on React components | `tinaField` on HTML DOM elements |
| Sync `params` access | `await params` everywhere |
| `next dev` alone | `tinacms dev -c "next dev"` |
| Edit `tina/__generated__/` files | Run `tinacms build` to regenerate |
