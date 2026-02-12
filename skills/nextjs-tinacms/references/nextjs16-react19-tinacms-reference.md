# Next.js 16 + React 19 + TinaCMS — Complete Reference

## Table of Contents

1. Schema Design Patterns
2. TinaCMS Field Type Reference
3. Blocks Pattern Deep Dive
4. SEO & Meta Configuration
5. React 19 Patterns for TinaCMS
6. Cache Components & `"use cache"`
7. proxy.ts Configuration
8. Self-Hosted TinaCMS
9. Media Management
10. Deployment Configurations
11. Common Gotchas
12. RenovateBot / Dependabot Config

---

## 1. Schema Design Patterns

### Collection Types

**Pages (folder collection):**
```typescript
{
  name: 'page',
  label: 'Pages',
  path: 'content/pages',
  format: 'md',
  ui: {
    router: ({ document }) => {
      if (document._sys.filename === 'home') return '/'
      return `/${document._sys.filename}`
    },
  },
  fields: [
    { name: 'title', label: 'Title', type: 'string', isTitle: true, required: true },
    { name: 'draft', label: 'Draft', type: 'boolean' },
    {
      name: 'blocks',
      label: 'Page Sections',
      type: 'object',
      list: true,
      ui: { visualSelector: true },
      templates: [
        // block templates here
      ],
    },
    // SEO object (see §4)
  ],
}
```

**Blog posts (folder collection):**
```typescript
{
  name: 'post',
  label: 'Blog Posts',
  path: 'content/posts',
  format: 'mdx',
  ui: {
    router: ({ document }) => `/blog/${document._sys.filename}`,
  },
  fields: [
    { name: 'title', label: 'Title', type: 'string', isTitle: true, required: true },
    { name: 'date', label: 'Date', type: 'datetime', required: true },
    { name: 'author', label: 'Author', type: 'reference', collections: ['author'] },
    { name: 'excerpt', label: 'Excerpt', type: 'string', ui: { component: 'textarea' } },
    { name: 'featuredImage', label: 'Featured Image', type: 'image' },
    {
      name: 'tags',
      label: 'Tags',
      type: 'string',
      list: true,
      options: ['featured', 'news', 'tutorial', 'case-study', 'announcement'],
    },
    { name: 'draft', label: 'Draft', type: 'boolean' },
    { name: 'body', label: 'Body', type: 'rich-text', isBody: true },
    // SEO object
  ],
}
```

**Singleton (global settings):**
```typescript
{
  name: 'settings',
  label: 'Site Settings',
  path: 'content/settings',
  format: 'json',
  ui: {
    global: true,
    allowedActions: { create: false, delete: false },
  },
  fields: [
    { name: 'siteName', label: 'Site Name', type: 'string', required: true },
    { name: 'siteUrl', label: 'Site URL', type: 'string' },
    { name: 'logo', label: 'Logo', type: 'image' },
    { name: 'favicon', label: 'Favicon', type: 'image' },
    {
      name: 'social',
      label: 'Social Links',
      type: 'object',
      fields: [
        { name: 'twitter', label: 'Twitter/X', type: 'string' },
        { name: 'linkedin', label: 'LinkedIn', type: 'string' },
        { name: 'github', label: 'GitHub', type: 'string' },
      ],
    },
    {
      name: 'analytics',
      label: 'Analytics',
      type: 'object',
      ui: { component: 'group' },
      fields: [
        { name: 'googleAnalyticsId', label: 'GA4 ID', type: 'string' },
        { name: 'plausibleDomain', label: 'Plausible Domain', type: 'string' },
      ],
    },
  ],
}
```

**Navigation (singleton):**
```typescript
{
  name: 'navigation',
  label: 'Navigation',
  path: 'content/navigation',
  format: 'json',
  ui: {
    global: true,
    allowedActions: { create: false, delete: false },
  },
  fields: [
    {
      name: 'mainNav',
      label: 'Main Navigation',
      type: 'object',
      list: true,
      ui: {
        itemProps: (item) => ({ label: item?.label || 'Nav Item' }),
      },
      fields: [
        { name: 'label', label: 'Label', type: 'string', required: true },
        { name: 'url', label: 'URL', type: 'string', required: true },
        {
          name: 'children',
          label: 'Dropdown Items',
          type: 'object',
          list: true,
          ui: { itemProps: (item) => ({ label: item?.label || 'Sub Item' }) },
          fields: [
            { name: 'label', label: 'Label', type: 'string', required: true },
            { name: 'url', label: 'URL', type: 'string', required: true },
            { name: 'description', label: 'Description', type: 'string' },
          ],
        },
      ],
    },
    {
      name: 'footerNav',
      label: 'Footer Navigation',
      type: 'object',
      list: true,
      ui: { itemProps: (item) => ({ label: item?.title || 'Column' }) },
      fields: [
        { name: 'title', label: 'Column Title', type: 'string' },
        {
          name: 'links',
          label: 'Links',
          type: 'object',
          list: true,
          ui: { itemProps: (item) => ({ label: item?.label || 'Link' }) },
          fields: [
            { name: 'label', label: 'Label', type: 'string', required: true },
            { name: 'url', label: 'URL', type: 'string', required: true },
          ],
        },
      ],
    },
  ],
}
```

---

## 2. TinaCMS Field Type Reference

| TinaCMS Type | Widget/Component | Notes |
|-------------|-----------------|-------|
| `string` | Text input | Add `isTitle: true` for list display |
| `string` + `list: true` | Tag input | With `options` array = select dropdown |
| `string` + `ui.component: 'textarea'` | Textarea | Multi-line text |
| `number` | Number input | Set `ui: { parse: (val) => Number(val) }` if needed |
| `boolean` | Toggle | Defaults to false |
| `datetime` | Date picker | ISO format stored |
| `image` | Image picker | Uses configured media store |
| `rich-text` | Markdown editor | Set `isBody: true` for document body |
| `rich-text` + `templates` | MDX editor | Custom embedded components |
| `object` | Field group | Nested fields |
| `object` + `list: true` | Repeatable group | Add `ui.itemProps` for labels |
| `object` + `list: true` + `templates` | Block selector | The "blocks pattern" |
| `reference` | Document picker | `collections: ['collectionName']` |

### Field UI Customizations

```typescript
// Validation
ui: {
  validate: (value) => {
    if (!value) return 'Required'
    if (value.length > 60) return 'Keep under 60 characters'
    return undefined // valid
  },
}

// Custom list item labels
ui: {
  itemProps: (item) => ({
    label: item?.title || item?.name || 'Untitled',
  }),
}

// Default values for new items
ui: {
  defaultItem: {
    title: 'New Item',
    style: 'default',
  },
}

// Collapsible group
ui: { component: 'group' }

// Hidden from editor
ui: { component: () => null }

// Conditional field visibility (via custom component)
ui: {
  component: (props) => {
    // Return null to hide, or render custom UI
  },
}
```

---

## 3. Blocks Pattern Deep Dive

The blocks pattern is TinaCMS's primary architecture for page-builder-style editing.

### Block Template Structure

```typescript
// Each block template
{
  name: 'hero',
  label: 'Hero Section',
  ui: {
    previewSrc: '/admin/blocks/hero.png',   // thumbnail in visual selector
    defaultItem: {
      heading: 'Your Heading Here',
      subheading: 'A compelling subheading',
      ctaText: 'Get Started',
      ctaUrl: '#',
      style: 'centered',
    },
  },
  fields: [
    { name: 'heading', label: 'Heading', type: 'string', required: true },
    { name: 'subheading', label: 'Subheading', type: 'string' },
    { name: 'backgroundImage', label: 'Background Image', type: 'image' },
    {
      name: 'style',
      label: 'Layout Style',
      type: 'string',
      options: [
        { value: 'centered', label: 'Centered' },
        { value: 'left-aligned', label: 'Left Aligned' },
        { value: 'split', label: 'Split (Text + Image)' },
      ],
    },
    {
      name: 'cta',
      label: 'Call to Action',
      type: 'object',
      fields: [
        { name: 'text', label: 'Button Text', type: 'string' },
        { name: 'url', label: 'Button URL', type: 'string' },
        {
          name: 'style',
          label: 'Button Style',
          type: 'string',
          options: ['primary', 'secondary', 'outline'],
        },
      ],
    },
  ],
}
```

### Common Block Templates

A production site typically needs these blocks:

1. **Hero** — Full-width with heading, subheading, CTA, background image
2. **Features** — Grid of feature cards (icon, title, description)
3. **Content** — Rich text section with optional image
4. **CTA Banner** — Call to action strip
5. **Testimonials** — Carousel or grid of quotes
6. **FAQ** — Accordion of questions/answers
7. **Gallery** — Image grid
8. **Stats** — Number highlights
9. **Team** — People grid with photos, bios
10. **Pricing** — Pricing table or cards
11. **Contact** — Form embed or contact info
12. **Logos** — Partner/client logo strip
13. **Video** — Embedded video section

### Block Renderer Pattern

```tsx
// components/blocks/BlockRenderer.tsx
import { tinaField } from 'tinacms/dist/react'
import { BlockErrorBoundary } from './BlockErrorBoundary'

// Import all block components
import { Hero } from './Hero'
import { Features } from './Features'
import { Content } from './Content'
import { CTABanner } from './CTABanner'
import { FAQ } from './FAQ'

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
          <BlockErrorBoundary key={index} blockName={block.__typename}>
            <section data-tina-field={tinaField(block)}>
              <Component {...block} />
            </section>
          </BlockErrorBoundary>
        )
      })}
    </>
  )
}
```

---

## 4. SEO & Meta Configuration

### Complete SEO Field Object

```typescript
const seoFields = {
  name: 'seo',
  label: 'SEO & Social Sharing',
  type: 'object' as const,
  ui: { component: 'group' },
  fields: [
    {
      name: 'metaTitle',
      label: 'Meta Title',
      type: 'string' as const,
      description: 'Overrides the page title in search results. Keep under 60 characters.',
      ui: {
        validate: (val: string) => val && val.length > 60 ? `${val.length}/60 — too long` : undefined,
      },
    },
    {
      name: 'metaDescription',
      label: 'Meta Description',
      type: 'string' as const,
      description: 'Shown below the title in search results. Aim for 120-160 characters.',
      ui: {
        component: 'textarea',
        validate: (val: string) => val && val.length > 160 ? `${val.length}/160 — too long` : undefined,
      },
    },
    {
      name: 'ogImage',
      label: 'Social Share Image',
      type: 'image' as const,
      description: 'Recommended: 1200×630px. Used for Facebook, LinkedIn, Twitter cards.',
    },
    {
      name: 'ogTitle',
      label: 'OG Title Override',
      type: 'string' as const,
      description: 'Optional. Defaults to Meta Title if empty.',
    },
    {
      name: 'ogDescription',
      label: 'OG Description Override',
      type: 'string' as const,
      ui: { component: 'textarea' },
      description: 'Optional. Defaults to Meta Description if empty.',
    },
    {
      name: 'twitterCard',
      label: 'Twitter Card Type',
      type: 'string' as const,
      options: [
        { value: 'summary_large_image', label: 'Large Image' },
        { value: 'summary', label: 'Summary' },
      ],
    },
    {
      name: 'noIndex',
      label: 'Hide from Search Engines',
      type: 'boolean' as const,
      description: 'Check to prevent this page from appearing in search results.',
    },
    {
      name: 'canonicalUrl',
      label: 'Canonical URL',
      type: 'string' as const,
      description: 'Set if this content also exists at another URL.',
    },
  ],
}
```

### Complete Metadata Generation

```tsx
// lib/metadata.ts — Reusable metadata generator
import type { Metadata } from 'next'

interface TinaPage {
  title: string
  seo?: {
    metaTitle?: string
    metaDescription?: string
    ogImage?: string
    ogTitle?: string
    ogDescription?: string
    twitterCard?: 'summary_large_image' | 'summary'
    noIndex?: boolean
    canonicalUrl?: string
  }
}

export function generatePageMetadata(page: TinaPage, siteUrl: string): Metadata {
  const seo = page.seo
  const title = seo?.metaTitle || page.title
  const description = seo?.metaDescription || ''

  return {
    title,
    description,
    robots: seo?.noIndex
      ? { index: false, follow: false }
      : { index: true, follow: true },
    alternates: seo?.canonicalUrl
      ? { canonical: seo.canonicalUrl }
      : undefined,
    openGraph: {
      title: seo?.ogTitle || title,
      description: seo?.ogDescription || description,
      images: seo?.ogImage ? [{ url: seo.ogImage, width: 1200, height: 630 }] : undefined,
      type: 'website',
      siteName: 'Your Site Name',
    },
    twitter: {
      card: seo?.twitterCard || 'summary_large_image',
      title: seo?.ogTitle || title,
      description: seo?.ogDescription || description,
      images: seo?.ogImage ? [seo.ogImage] : undefined,
    },
  }
}
```

### robots.ts and sitemap.ts

```typescript
// app/robots.ts
import type { MetadataRoute } from 'next'

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: '*',
      allow: '/',
      disallow: ['/admin/', '/api/'],
    },
    sitemap: 'https://yourdomain.com/sitemap.xml',
  }
}
```

```typescript
// app/sitemap.ts
import type { MetadataRoute } from 'next'
import { client } from '@/tina/__generated__/client'

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const pages = await client.queries.pageConnection()
  const posts = await client.queries.postConnection()

  const pageEntries = pages.data.pageConnection.edges?.map((edge) => ({
    url: `https://yourdomain.com/${edge?.node?._sys.filename === 'home' ? '' : edge?.node?._sys.filename}`,
    lastModified: new Date(),
    changeFrequency: 'weekly' as const,
    priority: edge?.node?._sys.filename === 'home' ? 1.0 : 0.8,
  })) || []

  const postEntries = posts.data.postConnection.edges?.map((edge) => ({
    url: `https://yourdomain.com/blog/${edge?.node?._sys.filename}`,
    lastModified: new Date(),
    changeFrequency: 'monthly' as const,
    priority: 0.6,
  })) || []

  return [...pageEntries, ...postEntries]
}
```

---

## 5. React 19 Patterns for TinaCMS

### Server Components as Data Fetchers

The primary pattern: Server Components fetch from Tina's GraphQL API, then hand data to Client Components for editing.

```tsx
// Server Component — fetches data
// app/[slug]/page.tsx
import { client } from '@/tina/__generated__/client'
import { PageClient } from './PageClient'

export default async function Page({
  params,
}: {
  params: Promise<{ slug: string }>
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
// Client Component — enables editing
// app/[slug]/PageClient.tsx
'use client'
import { useTina, tinaField } from 'tinacms/dist/react'
import { TinaMarkdown } from 'tinacms/dist/rich-text'
import { BlockRenderer } from '@/components/blocks/BlockRenderer'

export function PageClient(props: {
  query: string
  variables: Record<string, any>
  data: any
}) {
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

### Actions for Content Operations

React 19 Server Actions can be used alongside Tina for operations like contact forms, newsletter signups, etc.:

```tsx
// app/actions.ts
'use server'

export async function submitContactForm(formData: FormData) {
  const name = formData.get('name') as string
  const email = formData.get('email') as string
  const message = formData.get('message') as string

  // Validate, send email, save to DB, etc.
  // This runs on the server, never exposed to client
}
```

```tsx
// components/blocks/ContactForm.tsx
'use client'
import { useActionState } from 'react'
import { submitContactForm } from '@/app/actions'

export function ContactForm() {
  const [state, formAction, isPending] = useActionState(submitContactForm, null)

  return (
    <form action={formAction}>
      <input name="name" required />
      <input name="email" type="email" required />
      <textarea name="message" required />
      <button type="submit" disabled={isPending}>
        {isPending ? 'Sending...' : 'Send Message'}
      </button>
    </form>
  )
}
```

### The `use()` Hook for Conditional Data

```tsx
'use client'
import { use, Suspense } from 'react'

function RelatedPosts({ postsPromise }: { postsPromise: Promise<any[]> }) {
  const posts = use(postsPromise)
  return (
    <ul>
      {posts.map((post) => (
        <li key={post._sys.filename}>{post.title}</li>
      ))}
    </ul>
  )
}
```

---

## 6. Cache Components & `"use cache"`

Next.js 16 replaces implicit caching with explicit `"use cache"` directives.

### Page-Level Caching

```tsx
// app/blog/[slug]/page.tsx
import { cacheLife } from 'next/cache'

export default async function BlogPost({
  params,
}: {
  params: Promise<{ slug: string }>
}) {
  'use cache'
  cacheLife('hours') // 'seconds' | 'minutes' | 'hours' | 'days' | 'weeks' | 'max'

  const { slug } = await params
  const result = await client.queries.post({ relativePath: `${slug}.mdx` })

  return <PostClient {...result} />
}
```

### Function-Level Caching

```tsx
import { cache } from 'react'

const getSettings = cache(async () => {
  const result = await client.queries.settings({ relativePath: 'settings.json' })
  return result.data.settings
})
```

### Important: Visual Editing + Caching

When using Tina's visual editing (draft mode), caching must be bypassed:

```tsx
import { draftMode } from 'next/headers'

export default async function Page({ params }: { params: Promise<{ slug: string }> }) {
  const { isEnabled } = await draftMode()

  if (!isEnabled) {
    // Only cache in production mode, not during editing
    // Cache logic here
  }

  // ... render
}
```

---

## 7. proxy.ts Configuration

`proxy.ts` replaces `middleware.ts` in Next.js 16. It runs on Node.js runtime and defines the network boundary.

```typescript
// proxy.ts (project root)
import type { NextRequest } from 'next/server'

export function proxy(request: NextRequest) {
  // Redirect /admin to Tina admin
  // Handle auth, redirects, rewrites

  const { pathname } = request.nextUrl

  // Example: Protect admin route in production
  if (pathname.startsWith('/admin') && process.env.NODE_ENV === 'production') {
    // Add auth check here if needed
  }

  // Example: Redirect old URLs
  if (pathname === '/old-page') {
    return Response.redirect(new URL('/new-page', request.url), 301)
  }
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
}
```

---

## 8. Self-Hosted TinaCMS

For deployments without Tina Cloud (Cloudflare Pages, self-hosted, etc.):

### Architecture Options

| Option | Auth | Database | Git Provider |
|--------|------|----------|-------------|
| **Tina Cloud** | Tina Cloud | Tina Cloud | GitHub |
| **Vercel Self-Hosted** | AuthJS / NextAuth | Vercel KV | GitHub |
| **Custom Self-Hosted** | AuthJS / Clerk | MongoDB | GitHub |

### Vercel KV Self-Hosted Setup

```typescript
// tina/database.ts
import { createDatabase, createLocalDatabase } from '@tinacms/datalayer'
import { GitHubProvider } from 'tinacms-gitprovider-github'
import { Redis } from '@upstash/redis'

const isLocal = process.env.TINA_PUBLIC_IS_LOCAL === 'true'

const branch = process.env.GITHUB_BRANCH || 
               process.env.VERCEL_GIT_COMMIT_REF || 'main'

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

---

## 9. Media Management

### Repo-Based (Simplest)

Images stored in `public/uploads/`, committed to Git.

```typescript
media: {
  tina: {
    mediaRoot: 'uploads',
    publicFolder: 'public',
  },
}
```

**Pros:** Zero external dependencies, version controlled.
**Cons:** Bloats repo with binary files. Fine for small sites.

### Cloudinary

```typescript
media: {
  loadCustomStore: async () => {
    const pack = await import('next-tinacms-cloudinary')
    return pack.TinaCloudCloudinaryMediaStore
  },
}
```

Requires API route:
```typescript
// app/api/cloudinary/[...media]/route.ts
import { createMediaHandler } from 'next-tinacms-cloudinary/dist/handlers'

const handler = createMediaHandler({
  cloud_name: process.env.CLOUDINARY_CLOUD_NAME!,
  api_key: process.env.CLOUDINARY_API_KEY!,
  api_secret: process.env.CLOUDINARY_API_SECRET!,
})

export { handler as GET, handler as POST, handler as DELETE }
```

---

## 10. Deployment Configurations

### Vercel + Tina Cloud (Recommended)

```json
// package.json scripts
{
  "dev": "tinacms dev -c \"next dev\"",
  "build": "tinacms build && next build",
  "start": "tinacms build && next start"
}
```

Vercel env vars:
- `TINA_PUBLIC_CLIENT_ID` — from app.tina.io
- `TINA_TOKEN` — read token from app.tina.io
- `NEXT_PUBLIC_TINA_BRANCH` — usually `main`

### Vercel + Self-Hosted

Additional env vars:
- `GITHUB_OWNER`
- `GITHUB_REPO`
- `GITHUB_PERSONAL_ACCESS_TOKEN`
- `GITHUB_BRANCH`
- `KV_REST_API_URL`
- `KV_REST_API_TOKEN`
- `NEXTAUTH_SECRET`

---

## 11. Common Gotchas

### Next.js 16 Specific

1. **Forgot to await params** — Runtime error. Every `params` and `searchParams` is now a Promise.
2. **Still using `middleware.ts`** — Must rename to `proxy.ts` and rename the exported function.
3. **Turbopack incompatibilities** — Some webpack plugins don't work. Use `next dev --webpack` to fallback.
4. **`draftMode()` is now async** — Must `await draftMode()` in Next.js 16.

### TinaCMS Specific

5. **`tina/__generated__/` not found** — Run `tinacms dev` or `tinacms build` to generate.
6. **Visual editing not working** — Check `data-tina-field` attributes, ensure Client Component with `useTina()`.
7. **List items showing "Item 0, Item 1"** — Add `ui.itemProps` with label mapping.
8. **Blocks have no visual selector** — Set `ui: { visualSelector: true }` on the blocks field.
9. **Content not updating in production** — Check Tina Cloud webhook or ISR revalidation.
10. **GraphQL errors on build** — Schema mismatch. Run `tinacms build` to regenerate types.
11. **Media not loading** — Check `media_folder` / `publicFolder` config matches actual directory structure.

### React 19 Specific

12. **`forwardRef` deprecation warnings** — React 19 supports ref as a regular prop. Remove `forwardRef` wrappers.
13. **Context as JSX element** — `<Context>` now works directly, no need for `<Context.Provider>`.
14. **Suspense boundary needed for `use()`** — Wrap in `<Suspense>` when using `use()` with promises.

---

## 12. RenovateBot / Dependabot Config

TinaCMS packages must be grouped to avoid version drift:

### Renovate

```json
// renovate.json
{
  "extends": ["config:recommended"],
  "packageRules": [
    {
      "groupName": "TinaCMS",
      "matchPackagePatterns": ["^tinacms", "^@tinacms/"],
      "matchUpdateTypes": ["minor", "patch"],
      "automerge": true
    },
    {
      "groupName": "Next.js",
      "matchPackageNames": ["next"],
      "matchUpdateTypes": ["minor", "patch"]
    },
    {
      "groupName": "React",
      "matchPackageNames": ["react", "react-dom", "@types/react", "@types/react-dom"],
      "matchUpdateTypes": ["minor", "patch"]
    }
  ]
}
```

### Dependabot

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: npm
    directory: /
    schedule:
      interval: weekly
    groups:
      tinacms:
        patterns:
          - "tinacms*"
          - "@tinacms/*"
      react:
        patterns:
          - "react"
          - "react-dom"
          - "@types/react*"
      nextjs:
        patterns:
          - "next"
```
