# TinaCMS + Next.js 16 — Day 0–2 Full Setup Checklist

**Stack Versions — Do Not Hardcode**

At project init, the agent or developer MUST look up current stable versions:

```bash
# Check latest stable versions before pinning
npm view next version
npm view tinacms version
npm view @tinacms/cli version
npm view react version
npm view react-dom version
npm view tailwindcss version
```

**Minimum version floors (below these, features in this checklist break):**
- `next` ≥ 16.0.10 (security patches for CVE-2025-66478, CVE-2025-55184, CVE-2025-55183)
- `tinacms` ≥ 3.3.x (visual selector, current schema API)
- `@tinacms/cli` ≥ 2.1.x (current build toolchain)
- `react` / `react-dom` ≥ 19.2.x (View Transitions, useEffectEvent, Activity)
- `tailwindcss` ≥ 4.x (if using v4; v3.4.x also acceptable — check project requirements)
- `shadcn/ui` — not versioned as a package; uses `npx shadcn@latest init` and `npx shadcn@latest add`
- Node.js ≥ 20.9.0 (Node 18 dropped in Next.js 16)
- TypeScript ≥ 5.1.0

**Dependency management:** Configure RenovateBot (preferred over Dependabot) with package grouping to keep `tinacms` and `@tinacms/cli` version-synced. Mismatched Tina package versions break builds.

```json
// renovate.json — minimum viable config
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": ["config:recommended"],
  "packageRules": [
    {
      "matchPackagePatterns": ["tinacms", "@tinacms/*"],
      "groupName": "TinaCMS",
      "automerge": false
    },
    {
      "matchPackageNames": ["next"],
      "groupName": "Next.js",
      "automerge": false
    },
    {
      "matchPackageNames": ["react", "react-dom", "@types/react", "@types/react-dom"],
      "groupName": "React",
      "automerge": false
    },
    {
      "matchPackagePatterns": ["tailwindcss", "@tailwindcss/*"],
      "groupName": "Tailwind CSS",
      "automerge": true
    }
  ]
}
```

---

## Day 0 — Foundation, Schema Architecture & Content Modeling

### Project Scaffolding

- [ ] **0.01** Next.js 16 App Router project init (`npx create-next-app@latest`)
- [ ] **0.02** Verify Turbopack default bundler works (now default in Next.js 16)
- [ ] **0.03** Install TinaCMS: `npx @tinacms/cli@latest init`
- [ ] **0.04** Verify local dev: `tinacms dev` → confirm `/admin` loads
- [ ] **0.05** Clean up starter boilerplate code
- [ ] **0.06** Set up Git repo, `.gitignore` (include `tina/__generated__/`)
- [ ] **0.07** Configure env vars: `TINA_PUBLIC_CLIENT_ID`, `TINA_TOKEN`, `TINA_BRANCH`
- [ ] **0.08** Look up and install current stable versions: `npm view next version && npm view tinacms version && npm view @tinacms/cli version`
- [ ] **0.09** Verify `tinacms` and `@tinacms/cli` versions are synced (mismatched versions break builds)
- [ ] **0.10** Add `renovate.json` to repo root with TinaCMS/Next.js/React/Tailwind package grouping (see config above)

### Tailwind CSS & shadcn/ui Setup

- [ ] **0.11** Install Tailwind CSS (check v3 vs v4 — v4 has different config pattern):
  - v4: `npm install tailwindcss @tailwindcss/postcss` + CSS `@import "tailwindcss"`
  - v3: `npm install -D tailwindcss postcss autoprefixer && npx tailwindcss init -p`
- [ ] **0.12** Configure Tailwind content paths to include Tina block components, page templates, and shadcn components
- [ ] **0.13** Initialize shadcn/ui: `npx shadcn@latest init`
  - Select style, base color, CSS variables preference
  - Confirm `components.json` generated with correct aliases
- [ ] **0.14** Install baseline shadcn components likely needed for any CMS site:
  ```bash
  npx shadcn@latest add button card separator badge
  npx shadcn@latest add accordion    # for FAQ blocks
  npx shadcn@latest add navigation-menu  # for site nav
  npx shadcn@latest add sheet        # for mobile nav
  npx shadcn@latest add form input textarea  # for contact forms
  ```
- [ ] **0.15** Add additional shadcn components as blocks require them (install per-component, not all at once)
- [ ] **0.16** Verify shadcn components work inside Tina block components with `tinaField` data attributes
- [ ] **0.17** Set up Tailwind theme extension in config — map brand colors, fonts, spacing to design tokens
- [ ] **0.18** Ensure Tina schema enum values map cleanly to Tailwind utility classes:
  ```ts
  // Schema enum
  options: [
    { label: 'White', value: 'bg-white' },
    { label: 'Light Gray', value: 'bg-gray-50' },
    { label: 'Brand', value: 'bg-brand-500' },
  ]
  ```
  - If using Tailwind v4 with dynamic classes, verify classes aren't purged (safelist or explicit references)

### Next.js 16 Specific Setup

- [ ] **0.19** Confirm all `params` and `searchParams` access is async (`await props.params`) — fully sync access removed in Next.js 16
- [ ] **0.20** Update page type patterns to use `PageProps<'/path/[slug]'>` with `npx next typegen`
- [ ] **0.21** Verify React Compiler config (`reactCompiler` promoted from experimental to stable — not enabled by default)
- [ ] **0.22** Test TinaCMS build with Turbopack (`tinacms build && next build`)
- [ ] **0.23** Configure `proxy.ts` if needed (replaces middleware in Next.js 16 for network boundary concerns)
- [ ] **0.24** Check for and apply all current security patches: `npm audit`, review https://nextjs.org/blog for security advisories, run `npx fix-react2shell-next` if applicable

### Schema Design (tina/config.ts) — Collections

- [ ] **0.25** Define `pages` collection — dynamic pages with blocks pattern
- [ ] **0.26** Define `posts` collection — blog/articles with structured fields
- [ ] **0.27** Define `authors` collection — referenced by posts
- [ ] **0.28** Define `global` singleton — site-wide settings (see SEO section for required fields)
- [ ] **0.29** Define `navigation` singleton — editable nav structure
- [ ] **0.30** Define `footer` singleton — footer content and link groups
- [ ] **0.31** Define `notFound` singleton — customizable 404 page content
- [ ] **0.32** Define `tags` collection — centralized tag management (referenced by posts)
- [ ] **0.33** Define `categories` collection — centralized category management

### Schema Design — Singletons Pattern

- [ ] **0.34** All singletons use `ui: { global: true }` where appropriate
- [ ] **0.35** All singletons use `allowedActions: { create: false, delete: false }`
- [ ] **0.36** Single Document Collections for homepage, site settings, footer, nav, 404

### Schema Design — Blocks Pattern

- [ ] **0.37** Page sections as `type: 'object', list: true` with `templates` array
- [ ] **0.38** `ui: { visualSelector: true }` on blocks field
- [ ] **0.39** Preview images for each block template via `ui.previewSrc`
- [ ] **0.40** Default item values via `ui.defaultItem` on each template
- [ ] **0.41** Style fields as enum groups mapped to Tailwind classes — never raw CSS
- [ ] **0.42** Section style group on every block: layout, background, height, textColor (all enums)
- [ ] **0.43** Fallback/default case in block renderer for unknown block types

### Schema Design — Field Quality

- [ ] **0.44** `isTitle: true` on title fields (every collection needs one)
- [ ] **0.45** `required: true` on all mandatory fields
- [ ] **0.46** `ui.validate` functions for field-level validation
  - Character limits on meta descriptions (155 chars recommended)
  - Required alt text when image is present
  - URL format validation on link fields
- [ ] **0.47** `ui.description` on fields needing editorial guidance
- [ ] **0.48** `ui.component: 'textarea'` on multi-line string fields
- [ ] **0.49** `ui.component: 'group'` for collapsible secondary field groups (SEO, advanced settings)
- [ ] **0.50** `ui.format` on slug/filename fields
- [ ] **0.51** `ui.dateFormat` on date fields for consistent display
- [ ] **0.52** `ui.max` / `ui.min` on list fields where appropriate (e.g., max 6 testimonials)

### Schema Design — List Item UX

- [ ] **0.53** `ui.itemProps` on EVERY list/object-list field showing meaningful labels:
  ```ts
  ui: {
    itemProps: (item) => ({
      label: item?.title || item?.name || item?.heading || 'Untitled',
    }),
  }
  ```
- [ ] **0.54** Apply `itemProps` to: page blocks, nav items, FAQ items, team members, testimonials, link groups, social links — every single list

### Schema Design — Tags & Categories

- [ ] **0.55** Tags field as `type: 'string', list: true` with `ui.component: 'tags'`
- [ ] **0.56** OR: reference field pointing to centralized tags collection
- [ ] **0.57** Category selector: reference to categories collection or `type: 'string'` with `options` array
- [ ] **0.58** Tags/categories displayed in post schema, queryable for filtering

### Schema Design — Reference Fields

- [ ] **0.59** Author reference on posts (`type: 'reference', collections: ['authors']`)
- [ ] **0.60** Related posts reference list on posts
- [ ] **0.61** Any cross-collection relationships needed for the project

### Schema Design — Content Hooks

- [ ] **0.62** `beforeSubmit` hook for slug generation from title
- [ ] **0.63** `beforeSubmit` hook for auto-populating `modifiedDate` timestamp
- [ ] **0.64** `beforeSubmit` hook for any other computed/derived fields

---

## Day 1 — Visual Editing, Complete SEO/OG, & Custom Components

### Visual Editing / Click-to-Edit

- [ ] **1.01** Create Client Components (`'use client'`) for every editable page template
- [ ] **1.02** Wire `useTina()` hook with correct query/variables/data props in each Client Component
- [ ] **1.03** Add `data-tina-field={tinaField(data, 'fieldName')}` on every editable DOM element
- [ ] **1.04** Set up Draft Mode API route (`/api/preview`) for visual editing toggle
- [ ] **1.05** Purpose-built components accepting Tina types — no generic wrappers (breaks `tinaField`)
- [ ] **1.06** Block renderer with `switch`/map and default fallback for unknown blocks
- [ ] **1.07** Test click-to-edit on every field type: string, rich text, image, objects, lists
- [ ] **1.08** Verify visual editing works with async params (Next.js 16 requirement)
- [ ] **1.09** Test React 19.2 View Transitions with visual editing (new opportunity)

### Visual Editing Debugging Checklist

- [ ] **1.10** Draft mode enabled? (`/api/preview`)
- [ ] **1.11** Component is a Client Component? (`'use client'`)
- [ ] **1.12** `useTina` called with correct props?
- [ ] **1.13** `tinaField` attributes on DOM elements (not wrapper components)?
- [ ] **1.14** Tina dev server running? (`tinacms dev`)
- [ ] **1.15** Types generated and up to date? (`tina/__generated__/`)

### Global Settings Singleton — Complete Field Set

- [ ] **1.16** `siteName` — feeds `og:site_name`, JSON-LD, title template
- [ ] **1.17** `siteDescription` — global fallback description for all meta
- [ ] **1.18** `siteUrl` — base URL for constructing `og:url`, canonical URLs, sitemap
- [ ] **1.19** `defaultOgImage` — fallback social share image (with `alt`, `width`, `height` subfields)
- [ ] **1.20** `logo` — feeds `og:logo`, JSON-LD Organization logo
- [ ] **1.21** `logoDark` — dark mode variant
- [ ] **1.22** `favicon` — primary favicon
- [ ] **1.23** `appleTouchIcon` — Apple touch icon
- [ ] **1.24** `themeColor` — feeds `<meta name="theme-color">`
- [ ] **1.25** `twitterHandle` — feeds `twitter:site` (the brand's @handle)
- [ ] **1.26** `socialLinks` — list of profile URLs for JSON-LD `sameAs`
- [ ] **1.27** `googleSiteVerification` — verification meta tag (if needed)
- [ ] **1.28** `defaultRobots` — site-wide default robots directive
- [ ] **1.29** `titleTemplate` — e.g., `%s | Site Name` — used in `generateMetadata()`
- [ ] **1.30** `locale` — e.g., `en_US` — feeds `og:locale`

### Per-Page/Post SEO Object — Complete Field Set

- [ ] **1.31** `metaTitle` — overrides page title for `<title>`, `og:title`, `twitter:title`
- [ ] **1.32** `metaDescription` — explicit page description
- [ ] **1.33** `ogImage` — page-specific social image
- [ ] **1.34** `ogImageAlt` — required when ogImage is set (validate this)
- [ ] **1.35** `ogImageWidth` / `ogImageHeight` — dimensions for proper rendering
- [ ] **1.36** `canonical` — optional canonical URL override (syndicated content, preferred URL)
- [ ] **1.37** `noIndex` — boolean toggle, feeds robots meta
- [ ] **1.38** `noFollow` — separate boolean (not always paired with noIndex)
- [ ] **1.39** `ogType` — default "website" for pages, "article" for posts
- [ ] **1.40** `twitterCreator` — per-post author handle (falls back to site handle)
- [ ] **1.41** `excerpt` / `summary` — short description for cards, RSS, fallback before metaDescription

### For Blog/Article Collections — Additional SEO Fields

- [ ] **1.42** `publishedDate` — feeds `article:published_time`
- [ ] **1.43** `modifiedDate` — auto-populated via `beforeSubmit`, feeds `article:modified_time`
- [ ] **1.44** `author` — reference, feeds `article:author` and JSON-LD
- [ ] **1.45** Tags/categories — feed `article:tag`, `article:section`

### SEO Description Waterfall Logic

- [ ] **1.46** Build utility function implementing fallback chain:
  1. `metaDescription` (explicitly set per-page)
  2. `excerpt` / `summary` (if present)
  3. Auto-truncated first paragraph of content (programmatic)
  4. `siteDescription` (global fallback)
- [ ] **1.47** Same waterfall for title: `metaTitle` → `pageTitle` → `siteName`
- [ ] **1.48** Same waterfall for OG image: page `ogImage` → collection default → global `defaultOgImage`

### Complete Meta Tag Output — Implementation

- [ ] **1.49** `generateMetadata()` in every page layout pulling from Tina data + waterfall utility

**Basic meta tags:**
- [ ] **1.50** `<title>` — via title waterfall + titleTemplate
- [ ] **1.51** `<meta name="description">` — via description waterfall
- [ ] **1.52** `<link rel="canonical">` — canonical field OR constructed from siteUrl + path
- [ ] **1.53** `<meta name="robots">` — constructed from noIndex + noFollow booleans + defaultRobots
- [ ] **1.54** `<meta name="theme-color">` — from global themeColor
- [ ] **1.55** `<meta name="author">` — from author reference (posts)

**Open Graph tags — complete set:**
- [ ] **1.56** `og:title`
- [ ] **1.57** `og:description`
- [ ] **1.58** `og:image` (absolute URL — must include siteUrl prefix)
- [ ] **1.59** `og:image:width`
- [ ] **1.60** `og:image:height`
- [ ] **1.61** `og:image:alt`
- [ ] **1.62** `og:image:type` (image/jpeg, image/png, image/webp)
- [ ] **1.63** `og:url` (absolute canonical URL)
- [ ] **1.64** `og:site_name`
- [ ] **1.65** `og:type` (website | article | profile)
- [ ] **1.66** `og:locale` (e.g., en_US)
- [ ] **1.67** `og:logo` (from global settings)

**Article-specific OG (blog/posts only):**
- [ ] **1.68** `article:published_time`
- [ ] **1.69** `article:modified_time`
- [ ] **1.70** `article:author`
- [ ] **1.71** `article:section` (category)
- [ ] **1.72** `article:tag` (one per tag)

**Twitter/X Card tags — complete set:**
- [ ] **1.73** `twitter:card` (summary_large_image)
- [ ] **1.74** `twitter:title`
- [ ] **1.75** `twitter:description`
- [ ] **1.76** `twitter:image`
- [ ] **1.77** `twitter:image:alt`
- [ ] **1.78** `twitter:site` (@brandhandle from global)
- [ ] **1.79** `twitter:creator` (@authorhandle, falls back to twitter:site)

**Favicon & App icons:**
- [ ] **1.80** `<link rel="icon">` — favicon
- [ ] **1.81** `<link rel="apple-touch-icon">` — iOS icon
- [ ] **1.82** `<link rel="manifest">` — web app manifest
  - ⚠️ **Do NOT use `"display": "standalone"`** unless building a true PWA — breaks iOS Safari share sheet (iMessage, Notes, AirDrop, etc.)
  - Use `"display": "browser"` (default Safari behavior) or `"display": "minimal-ui"` (tinted bar, minor iOS quirks)
  - For address bar tinting without a manifest, `<meta name="theme-color">` (task 1.24/1.54) is sufficient
- [ ] **1.83** Verification tags (google-site-verification, etc.)

### JSON-LD Structured Data

- [ ] **1.84** `Organization` — on every page: logo, name, url, sameAs (social links)
- [ ] **1.85** `WebSite` — on homepage: name, url, potentialAction (sitelinks search)
- [ ] **1.86** `WebPage` — on all pages: name, description, dateModified, url
- [ ] **1.87** `Article` / `BlogPosting` — on blog posts: headline, author, datePublished, dateModified, image, description
- [ ] **1.88** `BreadcrumbList` — on all pages with depth > 1
- [ ] **1.89** `FAQPage` — on pages using FAQ blocks (feeds Google rich results)
- [ ] **1.90** `LocalBusiness` — if applicable to client type
- [ ] **1.91** `Person` — on author pages if they exist

### Dynamic OG Image Generation

- [ ] **1.92** `next/og` (or `@vercel/og`) setup for dynamic OG image generation
- [ ] **1.93** Route handler at `app/api/og/route.tsx` or per-route `opengraph-image.tsx`
- [ ] **1.94** Template includes: page title, site name/logo, brand colors
- [ ] **1.95** Fallback to uploaded static OG image when dynamic generation not appropriate

### Discovery & Crawling Files

- [ ] **1.96** `app/sitemap.ts` — dynamic sitemap from all Tina collections
  - Respects `noIndex` boolean (exclude noIndex pages)
  - Respects `draft` boolean (exclude drafts)
  - Includes `lastmod` from modifiedDate
  - Includes `changefreq` and `priority` where appropriate
- [ ] **1.97** `app/robots.ts` — dynamic robots.txt
  - References sitemap URL
  - Disallows `/admin`, `/api/preview`
  - Respects global defaultRobots setting
- [ ] **1.98** RSS/Atom feed generation (`app/feed.xml/route.ts`) for blog collections
  - Includes title, description, link, pubDate, author per item
  - Uses description waterfall for item descriptions

### 404 Page — Editable via CMS

- [ ] **1.99** Custom `app/not-found.tsx` page
- [ ] **2.01** `notFound` single document collection in Tina with fields:
  - `heading` — main 404 headline
  - `body` — rich text or markdown body
  - `image` — optional illustration/image
  - `ctaText` — button label
  - `ctaLink` — button destination
- [ ] **2.02** Wire `not-found.tsx` to pull from Tina `notFound` collection
- [ ] **2.03** Styled consistent with site design
- [ ] **2.04** Returns proper HTTP 404 status code
- [ ] **2.05** Include SEO: `noIndex: true` hardcoded, still has title/description for display

### Custom Field Components

- [ ] **2.06** Character count textarea for meta descriptions (shows count vs 155 limit)
- [ ] **2.07** Conditional field visibility based on sibling values
- [ ] **2.08** Color picker component (if needed beyond enum selectors)
- [ ] **2.09** URL/link field with internal/external toggle and validation

---

## Day 2 — Polish, Build, Deployment & Editor Experience

### Beginner Series Completion Verification

- [ ] **2.10** ✅ Part 1 — Your New TinaCMS Site: Next.js setup, install CMS, hello world, render content
- [ ] **2.11** ✅ Part 2 — Live Editing: routing to editor, wiring content to editor, loading content
- [ ] **2.12** ✅ Part 3 — The Content Model: new fields, string to markdown, rendering markdown, image fields ("A Thousand Words")
- [ ] **2.13** ✅ Part 4 — Website Builder Experience: what are blocks, create new template, link to model, render templates

### Technical Guides Completion

- [ ] **2.14** Markdown / MDX rendering setup (with custom component registration if using MDX)
- [ ] **2.15** Using Tina as a Website Builder — blocks pattern fully implemented and tested
- [ ] **2.16** Querying Tina content at runtime — verified for all collections
- [ ] **2.17** Storing media with content — media provider configured
- [ ] **2.18** Configuring collections — all patterns applied and validated
- [ ] **2.19** Single Document Collections — all singletons verified
- [ ] **2.20** Marking draft documents — conditional rendering in page templates (draft posts don't render in production)
- [ ] **2.21** Modifying data on save — `beforeSubmit` hooks working (slugs, timestamps, computed fields)

### Rich Text Configuration

- [ ] **2.22** Rich text toolbar customization per collection:
  - Blog posts: full toolbar (headings, bold, italic, links, images, code blocks, lists)
  - CTA/hero text: minimal (bold, italic, links only)
  - Bio/description: moderate (bold, italic, links, lists)
- [ ] **2.23** MDX component registration if using embedded components in rich text
- [ ] **2.24** Rich text rendering component with proper styling

### Reusable Field Groups (DRY Schema)

- [ ] **2.25** CTA group: `text`, `url`, `style` (primary/secondary/ghost), `openInNewTab`
- [ ] **2.26** Link group: `label`, `url`, `openInNewTab`, `isExternal`
- [ ] **2.27** Responsive image group: `src`, `alt` (required), `caption`, `width`, `height`
- [ ] **2.28** SEO group: extracted as reusable field definition applied to all content collections
- [ ] **2.29** Section style group: extracted and shared across all block templates

### Navigation & Information Architecture

- [ ] **2.30** Navigation singleton: nested link objects (label, url, children for dropdowns)
- [ ] **2.31** Footer singleton: column groups with link lists, social links, legal text
- [ ] **2.32** Breadcrumb component wired to page hierarchy
- [ ] **2.33** Active nav state logic
- [ ] **2.34** Mobile nav pattern (hamburger, slide-out, etc.)
- [ ] **2.35** Skip-to-content link for accessibility

### Media Management

- [ ] **2.36** Configure external media provider for production (Cloudinary or S3)
- [ ] **2.37** OR: local media with Git-tracked images in `/public` (simpler, fine for small sites)
- [ ] **2.38** Image optimization via Next.js `<Image>` component in ALL templates
- [ ] **2.39** Proper `sizes` attribute on every `<Image>`
- [ ] **2.40** Alt text field alongside EVERY image field — validated as required when image present
- [ ] **2.41** Image fallbacks — what renders when image fields are empty/missing

### Accessibility

- [ ] **2.42** ARIA landmarks on all templates (main, nav, footer, aside)
- [ ] **2.43** Focus management on block interactions and navigation
- [ ] **2.44** Color contrast verification on all style enum options
- [ ] **2.45** Semantic HTML in all block templates (proper heading hierarchy, lists, etc.)
- [ ] **2.46** Alt text enforcement (see 2.39)

### Performance

- [ ] **2.47** `next/font` optimization (load fonts properly, no FOUT/FOIT)
- [ ] **2.48** Lazy loading below-fold blocks/images
- [ ] **2.49** `loading.tsx` skeletons for Tina-powered pages
- [ ] **2.50** Verify Turbopack file system caching is working (stable in 16.1)

### Redirects

- [ ] **2.51** Redirects config in `next.config.ts` for any URL migrations
- [ ] **2.52** OR: redirects collection in Tina for editor-managed redirects
- [ ] **2.53** Verify all old URLs from previous site (if migration) are covered

### Error Handling & Edge Cases

- [ ] **2.54** Error boundaries on block renderer
- [ ] **2.55** Fallback for missing/null fields in all templates (no crashes on empty content)
- [ ] **2.56** Empty state handling — what renders when a page has zero blocks
- [ ] **2.57** Preview/draft indicator visible to editors but not public visitors

### Build & Deployment

- [ ] **2.58** Build command verified: `tinacms build && next build`
- [ ] **2.59** `tina/__generated__/` types are current and building clean
- [ ] **2.60** Vercel deployment config:
  ```json
  {
    "buildCommand": "tinacms build && next build",
    "framework": "nextjs"
  }
  ```
- [ ] **2.61** Environment variables set in hosting platform (Vercel/Netlify/etc.)
- [ ] **2.62** Test production build locally before first deploy
- [ ] **2.63** Verify visual editing works in deployed environment (TinaCMS Cloud connected)
- [ ] **2.64** Verify draft mode / preview works in production

### QA Checklist

- [ ] **2.65** Test all collections CRUD in `/admin` — create, read, update, delete
- [ ] **2.66** Test visual editing on every page template
- [ ] **2.67** Test all blocks — add, edit, reorder, delete
- [ ] **2.68** Lighthouse audit: target 90+ across all categories
- [ ] **2.69** Mobile responsive check on all templates
- [ ] **2.70** Cross-browser check on visual editing (Chrome, Firefox, Safari, Edge)
- [ ] **2.71** Validate OG tags with:
  - Facebook Sharing Debugger (https://developers.facebook.com/tools/debug/)
  - Twitter/X Card Validator
  - LinkedIn Post Inspector
  - opengraph.xyz or similar
- [ ] **2.72** Validate JSON-LD with Google Rich Results Test
- [ ] **2.73** Validate sitemap.xml loads and is well-formed
- [ ] **2.74** Validate robots.txt is correct
- [ ] **2.75** Validate RSS feed (if applicable)
- [ ] **2.76** Test 404 page — both display and HTTP status code

### Form Integration (if needed)

- [ ] **2.77** Contact/inquiry form connected to backend (Formspree, Resend, etc.)
- [ ] **2.78** Form separate from Tina — Tina manages content, not submissions
- [ ] **2.79** Form validation, success/error states

### Analytics

- [ ] **2.80** Analytics installed (GA4, Plausible, Fathom, etc.)
- [ ] **2.81** Consent handling if required (GDPR, CCPA)

### Editor Documentation

- [ ] **2.82** Write client-facing editor guide covering:
  - How to access `/admin`
  - How to edit pages (visual mode vs form mode)
  - How to add, reorder, and remove blocks
  - How to manage media/images
  - How to fill in SEO fields (with guidance on what makes a good meta description, title, etc.)
  - How to create/manage blog posts
  - How to edit navigation and footer
  - How to manage tags/categories
  - How to customize the 404 page
  - How to mark content as draft
- [ ] **2.83** Include screenshots of block selector, visual editing, form editing modes
- [ ] **2.84** Include "what each SEO field does and why it matters" reference for editors

---

## Summary

| Day | Focus | Task Count |
|-----|-------|------------|
| Day 0 | Foundation, Tailwind/shadcn, schema architecture, content modeling, field UX | 0.01–0.64 (64 tasks) |
| Day 1 | Visual editing, complete SEO/OG/meta, 404, custom components | 1.01–1.99 (99 tasks) |
| Day 2 | Polish, build, deployment, QA, editor docs | 2.01–2.84 (84 tasks) |
| **Total** | | **~247 tasks** |

### Anti-Patterns to Avoid

| Pattern | Why It's Bad | Correct Approach |
|---------|-------------|------------------|
| Single rich text field for page body | Loses block-level editing, no visual structure | Use blocks list field with templates |
| Exposing CSS values in schema | Non-technical editors break design | Enums mapped to Tailwind classes |
| Generic wrapper components | Breaks `tinaField` attachment | Purpose-built components accepting Tina types |
| `useTina` in Server Components | Runtime error — hooks require client | Wrap in Client Component (`'use client'`) |
| Dependabot for Tina packages | Async updates break version sync | RenovateBot with grouping |
| Inline media (base64 in content) | Bloats Git history, slow builds | External media provider (Cloudinary/S3) |
| No fallback for missing blocks | Page crashes on schema changes | Default case in block renderer |
| Hardcoded SEO in pages | Editors can't update metadata | SEO object in schema with waterfall |
| List items showing "Item 0" | Editors can't identify content | `ui.itemProps` with meaningful labels |
| Missing og:url | Social shares don't link correctly | Construct from siteUrl + canonical path |
| Missing image dimensions in OG | Social platforms render poorly | Include og:image:width and og:image:height |
| No description waterfall | Pages with empty meta descriptions | metaDescription → excerpt → auto-truncate → siteDescription |
| Sync params access (Next.js 16+) | Build fails — removed in v16 | `await props.params` everywhere |
| `manifest.json` with `display: "standalone"` | Breaks iOS Safari share sheet (iMessage, AirDrop, Notes) | `"display": "browser"` or omit manifest; use `<meta name="theme-color">` for tinting |
