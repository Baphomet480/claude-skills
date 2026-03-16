# SEO & Metadata

## Metadata Architecture

Every page needs `generateMetadata()`. Next.js 16 streams metadata -- it no longer blocks page rendering.

```typescript
import type { Metadata } from 'next'
import { client } from '@/tina/__generated__/client'

type Props = { params: Promise<{ slug: string }> }

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params  // Must await in Next.js 16
  const { data } = await client.queries.page({ relativePath: `${slug}.md` })
  const seo = data.page.seo
  const global = (await client.queries.global({ relativePath: 'settings.json' })).data.global

  return {
    title: seo?.metaTitle || data.page.title,
    description: resolveDescription(seo, data.page, global),
    openGraph: {
      images: resolveOgImage(seo, global),
      type: 'website',
      siteName: global.siteName,
    },
    robots: { index: !seo?.noIndex, follow: !seo?.noFollow },
    alternates: { canonical: seo?.canonical || `${global.siteUrl}/${slug}` },
  }
}
```

## Description Waterfall

Always implement a fallback chain -- never leave descriptions empty:

1. `metaDescription` (explicitly set per-page)
2. `excerpt` / `summary` (if present)
3. Auto-truncated first paragraph of content
4. `siteDescription` (global fallback)

Same pattern for titles (`metaTitle` -> `pageTitle` -> `siteName`) and OG images (`ogImage` -> collection default -> global `defaultOgImage`).

## SEO Schema Fields

Add to every content collection as a collapsible group:

```typescript
const seoFields = [
  {
    name: 'metaTitle', label: 'Meta Title', type: 'string' as const,
    description: 'Overrides page title in search results. Keep under 60 chars.',
    ui: { validate: (val: string) => val && val.length > 60 ? `${val.length}/60 -- too long` : undefined },
  },
  {
    name: 'metaDescription', label: 'Meta Description', type: 'string' as const,
    description: '120-160 characters.',
    ui: { component: 'textarea', validate: (val: string) => val && val.length > 160 ? `${val.length}/160 -- too long` : undefined },
  },
  { name: 'ogImage', label: 'Social Share Image', type: 'image' as const, description: '1200x630px recommended.' },
  { name: 'noIndex', label: 'Hide from Search Engines', type: 'boolean' as const },
  { name: 'noFollow', label: 'No Follow Links', type: 'boolean' as const, description: 'Independent of noIndex.' },
  { name: 'canonicalUrl', label: 'Canonical URL', type: 'string' as const },
]
```

Attach to collections:
```typescript
{ name: 'seo', label: 'SEO & Social', type: 'object', ui: { component: 'group' }, fields: seoFields }
```

## Global Settings Fields

The `global` singleton should include:

| Field | Purpose |
|-------|---------|
| `siteName` | `og:site_name`, JSON-LD, title template |
| `siteDescription` | Fallback description for all meta |
| `siteUrl` | Base URL for `og:url`, canonical, sitemap |
| `defaultOgImage` | Fallback social image (with alt, width, height) |
| `logo` / `logoDark` | JSON-LD Organization logo |
| `favicon` / `appleTouchIcon` | Discovery |
| `themeColor` | `<meta name="theme-color">` |
| `twitterHandle` | `twitter:site` |
| `socialLinks` | JSON-LD `sameAs` |
| `titleTemplate` | e.g. `%s \| Site Name` |
| `locale` | `og:locale` (e.g. `en_US`) |
| `defaultRobots` | Site-wide robots directive |

## Open Graph Tags

**Required per page:**

| Tag | Source |
|-----|--------|
| `og:title` | Title waterfall |
| `og:description` | Description waterfall |
| `og:image` | OG image waterfall (absolute URL) |
| `og:image:width` / `og:image:height` | From image metadata |
| `og:image:alt` | Required when image set |
| `og:url` | Canonical URL |
| `og:site_name` | Global settings |
| `og:type` | `website` for pages, `article` for posts |
| `og:locale` | Global settings |

**Article-specific** (blog posts only): `article:published_time`, `article:modified_time`, `article:author`, `article:tag`, `article:section`.

**Twitter/X Cards:** `twitter:card` (`summary_large_image`), `twitter:title`, `twitter:description`, `twitter:image`, `twitter:image:alt`, `twitter:site`, `twitter:creator`.

## JSON-LD Structured Data

Add per page type:

| Schema | Where |
|--------|-------|
| `Organization` | Every page (logo, name, url, sameAs) |
| `WebSite` | Homepage (name, url, potentialAction for sitelinks search) |
| `WebPage` | All pages (name, description, dateModified) |
| `Article` / `BlogPosting` | Blog posts (headline, author, dates, image) |
| `BreadcrumbList` | Pages with depth > 1 |
| `FAQPage` | Pages using FAQ blocks (Google rich results) |

## Dynamic OG Images

Import from `next/og` (not `@vercel/og`):

```tsx
// app/[slug]/opengraph-image.tsx
import { ImageResponse } from 'next/og'
import { client } from '@/tina/__generated__/client'

export const size = { width: 1200, height: 630 }
export const contentType = 'image/png'

export default async function OGImage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params  // Next.js 16: Promise
  const { data } = await client.queries.page({ relativePath: `${slug}.md` })

  return new ImageResponse(
    <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center',
      alignItems: 'center', width: '100%', height: '100%',
      backgroundColor: '#0a0a0a', color: '#fff', padding: '60px' }}>
      <div style={{ fontSize: 64, fontWeight: 700 }}>{data.page.title}</div>
    </div>,
    { ...size }
  )
}
```

**Limitations:** Max 500KB bundle (includes fonts, images). Only flexbox layout. Only ttf/otf/woff fonts.

## Discovery Files

**Sitemap** (`app/sitemap.ts`):
```typescript
import type { MetadataRoute } from 'next'
import { client } from '@/tina/__generated__/client'

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const pages = await client.queries.pageConnection()
  return pages.data.pageConnection.edges?.map((edge) => ({
    url: `https://yourdomain.com/${edge?.node?._sys.filename === 'home' ? '' : edge?.node?._sys.filename}`,
    lastModified: edge?.node?._sys.lastModified ? new Date(edge.node._sys.lastModified) : new Date(),
    changeFrequency: 'weekly' as const,
  })) || []
}
```

Respect `noIndex` (exclude pages) and `draft` (exclude drafts).

**Robots** (`app/robots.ts`):
```typescript
export default function robots(): MetadataRoute.Robots {
  return {
    rules: { userAgent: '*', allow: '/', disallow: ['/admin/', '/api/'] },
    sitemap: 'https://yourdomain.com/sitemap.xml',
  }
}
```

**RSS Feed** (`app/feed.xml/route.ts`): Generate from blog collection with title, description, link, pubDate per item.

## Manifest Warning

Do NOT use `"display": "standalone"` in `manifest.json` unless building a true PWA -- it breaks iOS Safari share sheet (iMessage, AirDrop, Notes). Use `"display": "browser"` or omit manifest entirely. `<meta name="theme-color">` handles address bar tinting without a manifest.
