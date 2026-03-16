# Setup Checklist

Three phases. **MVP** gets a working site with editing. **Polish** adds production quality. **Comprehensive** covers enterprise concerns.

## Prerequisites

- Node.js >= 20.9.0
- pnpm (recommended for TinaCMS projects)
- Tina Cloud account at `app.tina.io` (free tier: 2 users)
- Vercel account for deployment
- `npm view next version && npm view tinacms version && npm view @tinacms/cli version` -- check latest before pinning

## Phase 1: MVP (~40 tasks)

A working site with visual editing, basic SEO, and deployable to Vercel.

### Scaffold

- [ ] `npx create-next-app@latest` with TypeScript, Tailwind, App Router, src directory
- [ ] `npx @tinacms/cli@latest init` -- installs TinaCMS, creates `tina/config.ts`
- [ ] Verify: `tinacms dev` loads `/admin`
- [ ] Add `tina/__generated__/` to `.gitignore`; commit only `tina-lock.json`
- [ ] Verify `tinacms` and `@tinacms/cli` are >= minimum version floors
- [ ] Verify `@tinacms/cli` >= 2.1.8 (CVE-2026-28792)
- [ ] Local dev works without Tina Cloud credentials (local-only mode)
- [ ] Register project at `app.tina.io` and note `TINA_PUBLIC_CLIENT_ID` and `TINA_TOKEN` for Vercel deployment

### Tailwind & shadcn/ui

- [ ] Tailwind CSS 4: `@import "tailwindcss"` in CSS (or v3 with `tailwind.config.js`)
- [ ] `npx shadcn@latest init` -- generates `components.json`
- [ ] Install baseline components: `button`, `card`, `navigation-menu`, `sheet`
- [ ] Note: `tw-animate-css` replaces deprecated `tailwindcss-animate`

### Schema -- Core Collections

- [ ] `pages` collection with blocks pattern (`type: 'object', list: true, templates: [...]`)
- [ ] `global` singleton with `siteName`, `siteUrl`, `logo`, `defaultSeo`
- [ ] `navigation` singleton with `mainNav` list (label, url, children)
- [ ] `ui: { visualSelector: true }` on blocks field
- [ ] `ui.defaultItem` on every block template
- [ ] `isTitle: true` on title fields, `required: true` on mandatory fields
- [ ] `ui.itemProps` on every list field with meaningful labels
- [ ] `seo` object group on pages collection (see `references/seo-meta.md`)

### Schema -- Blocks (minimum 3)

- [ ] Hero block (heading, subheading, CTA, background image, layout enum)
- [ ] Content block (heading, rich-text body, optional image, image position enum)
- [ ] CTA Banner block (heading, button text, button URL, style enum)
- [ ] Style enums mapped to Tailwind classes (never raw CSS values)
- [ ] Fallback/default case in block renderer for unknown types

### Visual Editing

- [ ] Server Component fetches `{ data, query, variables }`, passes to Client Component
- [ ] Client Component uses `useTina()` with all three props
- [ ] `data-tina-field={tinaField(data.page, 'fieldName')}` on DOM elements
- [ ] Draft Mode API route (`/api/preview`)
- [ ] `ui.router` on every content collection
- [ ] Test click-to-edit on string, rich-text, image, list fields

### Basic SEO

- [ ] `generateMetadata()` in every page with title and description
- [ ] `app/robots.ts` -- disallow `/admin`, `/api`
- [ ] `app/sitemap.ts` -- dynamic from all collections

### Build & Deploy

- [ ] `"build": "tinacms build && next build"` in package.json
- [ ] `"dev": "tinacms dev -c \"next dev\""` in package.json
- [ ] `"start": "next start"` in package.json
- [ ] Install `@vercel/analytics` and `@vercel/speed-insights`, render in root layout
- [ ] Test production build locally: `pnpm build && pnpm start`
- [ ] Deploy to Vercel with Tina Cloud env vars (`NEXT_PUBLIC_TINA_CLIENT_ID`, `TINA_TOKEN`, `NEXT_PUBLIC_TINA_BRANCH`)
- [ ] Set up Vercel Deploy Hook for content change rebuilds
- [ ] Verify visual editing works in deployed environment with Tina Cloud connected

---

## Phase 2: Polish (~50 tasks)

Production-quality SEO, additional collections, accessibility, performance.

### Additional Collections (as needed)

- [ ] `posts` collection with title, date, author reference, excerpt, body, tags, SEO
- [ ] `authors` collection with name, avatar, bio, social links
- [ ] `footer` singleton (if complex enough to separate from navigation)
- [ ] Content hooks: `beforeSubmit` for slug generation and `modifiedDate` auto-population
- [ ] `draft` boolean on posts, conditional rendering (drafts hidden in production)

### Additional Blocks

- [ ] Features grid (heading, items list with icon/title/description, columns enum)
- [ ] FAQ accordion (heading, items list with question/answer)
- [ ] Testimonials (quotes list with text/author/role/avatar)
- [ ] Gallery (images list)
- [ ] Add `ui.previewSrc` thumbnails for visual selector (images in `public/admin/blocks/`)

### Complete SEO

- [ ] Description waterfall utility (metaDescription -> excerpt -> auto-truncate -> siteDescription)
- [ ] OG image waterfall (page ogImage -> collection default -> global defaultOgImage)
- [ ] Full Open Graph tags (title, description, image with dimensions, url, site_name, type, locale)
- [ ] Twitter/X Card tags (card, title, description, image, site, creator)
- [ ] JSON-LD: Organization, WebSite (homepage), WebPage (all), BreadcrumbList
- [ ] JSON-LD: Article/BlogPosting (blog posts), FAQPage (FAQ blocks)
- [ ] Dynamic OG images (`opengraph-image.tsx` or `/api/og` route)
- [ ] RSS feed (`app/feed.xml/route.ts`)
- [ ] `noIndex` and `noFollow` as separate booleans in SEO schema
- [ ] Sitemap respects `noIndex` and `draft` booleans, uses content `lastModified`

### Accessibility

- [ ] ARIA landmarks (main, nav, footer, aside)
- [ ] Semantic HTML in all block templates (heading hierarchy, lists)
- [ ] Alt text field alongside every image field, validated as required
- [ ] Skip-to-content link
- [ ] Color contrast check on all style enum options

### Performance

- [ ] `next/font` optimization
- [ ] `next/image` with `sizes` attribute on every image
- [ ] Lazy loading below-fold blocks
- [ ] `loading.tsx` skeletons for Tina-powered pages
- [ ] `cacheComponents: true` in `next.config.ts` with appropriate `cacheLife` presets

### Rich Text

- [ ] Toolbar customization per collection (full for posts, minimal for CTAs)
- [ ] Rich text rendering component with proper styling
- [ ] MDX component registration if using embedded components

### 404 Page

- [ ] `notFound` singleton collection (heading, body, CTA, image)
- [ ] Custom `app/not-found.tsx` wired to Tina collection
- [ ] Returns proper HTTP 404 status, hardcoded `noIndex: true`

---

## Phase 3: Comprehensive (~30 tasks)

Enterprise polish, editor experience, dependency management, QA.

### Navigation & Footer

- [ ] Dropdown support in navigation (nested children)
- [ ] Active nav state logic
- [ ] Mobile nav pattern (hamburger, slide-out)
- [ ] Breadcrumb component from page hierarchy

### Reusable Field Groups (DRY Schema)

- [ ] CTA group: text, url, style (primary/secondary/ghost), openInNewTab
- [ ] Link group: label, url, openInNewTab
- [ ] Responsive image group: src, alt (required), caption, width, height
- [ ] SEO group: extracted as shared variable, applied to all content collections
- [ ] Section style group: shared across all block templates

### Custom Field Components

- [ ] Character count textarea for meta descriptions
- [ ] Conditional field visibility based on sibling values
- [ ] URL/link field with internal/external toggle

### Dependency Management

- [ ] RenovateBot or Dependabot config with TinaCMS/React/Next.js grouping
- [ ] Pin exact TinaCMS versions (no caret ranges)

### QA

- [ ] All collections CRUD tested in `/admin`
- [ ] Visual editing tested on every page template and block type
- [ ] Lighthouse audit: target 90+ across all categories
- [ ] Mobile responsive check on all templates
- [ ] Validate OG tags (Facebook Debugger, Twitter Validator, opengraph.xyz)
- [ ] Validate JSON-LD (Google Rich Results Test)
- [ ] Validate sitemap.xml and robots.txt
- [ ] Cross-browser check (Chrome, Firefox, Safari, Edge)

### Editor Documentation

- [ ] Guide covering: accessing `/admin`, visual vs form editing, blocks, media, SEO fields, drafts
- [ ] Screenshots of block selector and editing modes

### Analytics & Forms

- [ ] Analytics installed (GA4, Plausible, Fathom, or Vercel Analytics)
- [ ] Contact form if needed (Formspree, Resend -- separate from Tina)

## Common Gotchas

| Problem | Cause | Fix |
|---------|-------|-----|
| `Cannot find module '../tina/__generated__/client'` | Wrong build order | `tinacms build && next build` |
| `require is not defined` / `ERR_REQUIRE_ESM` | TinaCMS 3.x is ESM-only | Use `import` syntax, `"type": "module"` |
| `Schema Not Successfully Built` | Frontend imports in `tina/config.ts` | Keep imports minimal |
| `Field name contains invalid characters` | Hyphens/spaces | Alphanumeric + underscores only |
| `GetCollection failed: template name not provided` | Missing `_template` in frontmatter | Add when using `templates` array |
| Visual editing not working | Multiple causes | See debugging checklist in `visual-editing.md` |
| List items show "Item 0" | Missing `ui.itemProps` | Add meaningful label function |
| Mismatched package versions | Tina packages out of sync | Pin exact, use package grouping |
| Content stale after Git push | Database index not updated | Re-index from Tina Cloud dashboard |
