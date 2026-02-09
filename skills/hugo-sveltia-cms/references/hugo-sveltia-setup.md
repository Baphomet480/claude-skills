# Hugo + Sveltia CMS + Basecoat — Complete Reference

## 1. Hugo Configuration

Minimal `hugo.yaml`:

```yaml
baseURL: "https://example.com"  # CHANGEME
languageCode: "en-us"
title: "Site Title"  # CHANGEME

# Build settings
build:
  buildStats:
    enable: true
  cachebusters:
    - source: 'assets/notwatching/hugo_stats\.json'
      target: css

module:
  mounts:
    - source: assets
      target: assets
    - disableWatch: true
      source: hugo_stats.json
      target: assets/notwatching/hugo_stats.json

pagination:
  pagerSize: 10

taxonomies:
  tag: tags
  category: categories

markup:
  goldmark:
    renderer:
      unsafe: true
  highlight:
    style: monokai

params:
  description: "Site description"  # CHANGEME

menus:
  main:
    - name: Home
      pageRef: /
      weight: 10
    - name: Blog
      pageRef: /posts
      weight: 20
    - name: About
      pageRef: /about
      weight: 30
```

Note: The `build.buildStats` and `module.mounts` blocks are required for Tailwind CSS v4 + Hugo's `css.TailwindCSS` pipe. Tailwind reads `hugo_stats.json` to detect used classes. Without this, Tailwind purges everything.

### Directory Structure

```
site-root/
├── archetypes/           # Content templates
├── assets/
│   └── css/
│       └── main.css      # Tailwind + Basecoat imports
├── content/              # Markdown content
├── data/                 # Data files (JSON/YAML)
├── layouts/
│   ├── _default/
│   │   ├── baseof.html   # Base template
│   │   ├── list.html     # List pages
│   │   └── single.html   # Single pages
│   ├── partials/
│   │   ├── head.html
│   │   ├── header.html
│   │   ├── footer.html
│   │   └── components/   # Basecoat component partials
│   └── index.html        # Home page
├── static/
│   ├── admin/
│   │   ├── index.html    # Sveltia CMS entry
│   │   └── config.yml    # CMS configuration
│   └── images/
│       └── uploads/      # CMS media uploads
├── hugo.yaml
├── package.json
└── .gitignore
```

---

## 2. Basecoat Integration

### Option A: npm + Tailwind Pipeline (Recommended)

**Install:**
```bash
npm init -y
npm install -D tailwindcss @tailwindcss/cli basecoat-css
```

**`assets/css/main.css`:**
```css
@import "tailwindcss";
@import "basecoat-css";
```

**`layouts/partials/css.html`:**
```html
{{ with resources.Get "css/main.css" }}
  {{ $opts := dict "minify" (not hugo.IsDevelopment) }}
  {{ with . | css.TailwindCSS $opts }}
    {{ if hugo.IsDevelopment }}
      <link rel="stylesheet" href="{{ .RelPermalink }}">
    {{ else }}
      {{ with . | fingerprint }}
        <link rel="stylesheet" href="{{ .RelPermalink }}" integrity="{{ .Data.Integrity }}" crossorigin="anonymous">
      {{ end }}
    {{ end }}
  {{ end }}
{{ end }}
```

**In `baseof.html` `<head>`:**
```html
{{ with (templates.Defer (dict "key" "global")) }}
  {{ partial "css.html" . }}
{{ end }}
```

The `templates.Defer` ensures Tailwind processes all templates before generating CSS. The `hugo_stats.json` mount (from hugo.yaml) makes class usage visible to Tailwind for tree-shaking.

**Build command for CF Pages:** `npm install && hugo --minify`

**Basecoat JS (for interactive components like dropdowns, dialogs):**
```html
<script src="https://cdn.jsdelivr.net/npm/basecoat-css@latest/dist/js/basecoat.min.js" defer></script>
```

Or install locally: copy specific component JS from the npm package.

### Option B: CDN Only (Quick Prototypes)

Add to `baseof.html` `<head>`:
```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/basecoat-css@latest/dist/basecoat.cdn.min.css">
<script src="https://cdn.jsdelivr.net/npm/basecoat-css@latest/dist/js/basecoat.min.js" defer></script>
```

No `package.json` needed. No tree-shaking. Build command: `hugo --minify`.

### Hugo Component Partials

Create reusable partials for Basecoat components:

**`layouts/partials/components/card.html`:**
```html
{{- $title := .title | default "" -}}
{{- $body := .body | default "" -}}
{{- $image := .image | default "" -}}
{{- $link := .link | default "" -}}
<div class="card">
  {{- with $image }}
  <img src="{{ . }}" alt="{{ $title }}" class="card-image">
  {{- end }}
  <div class="card-body">
    {{- with $title }}<h3 class="card-title">{{ . }}</h3>{{ end }}
    {{- with $body }}<p>{{ . }}</p>{{ end }}
    {{- with $link }}<a href="{{ . }}" class="btn btn-primary">Read more</a>{{ end }}
  </div>
</div>
```

**Usage in templates:**
```html
{{ partial "components/card" (dict "title" .Title "body" .Summary "image" .Params.image "link" .Permalink) }}
```

**`layouts/partials/components/badge.html`:**
```html
{{- $text := .text -}}
{{- $variant := .variant | default "default" -}}
<span class="badge badge-{{ $variant }}">{{ $text }}</span>
```

---

## 3. CMS Config Structure

### `static/admin/config.yml`

```yaml
# yaml-language-server: $schema=https://unpkg.com/@sveltia/cms/schema/sveltia-cms.json

backend:
  name: github
  repo: "owner/repo"  # CHANGEME
  branch: main
  base_url: "https://your-auth-worker.workers.dev"  # CHANGEME — Cloudflare Worker URL

media_folder: "static/images/uploads"
public_folder: "/images/uploads"

collections:
  # Collections go here — see patterns below
```

### Backend (GitHub Only)

```yaml
backend:
  name: github
  repo: "owner/repo"
  branch: main
  base_url: "https://your-auth-worker.workers.dev"
  # Optional: commit message templates
  commit_messages:
    create: "feat(content): create {{collection}} '{{slug}}'"
    update: "fix(content): update {{collection}} '{{slug}}'"
    delete: "chore(content): delete {{collection}} '{{slug}}'"
    uploadMedia: "feat(media): upload '{{path}}'"
    deleteMedia: "chore(media): delete '{{path}}'"
```

---

## 4. Collection Patterns

### Standard: Blog Posts

```yaml
- name: posts
  label: Posts
  label_singular: Post
  folder: "content/posts"
  create: true
  slug: "{{year}}-{{month}}-{{day}}-{{slug}}"
  extension: "md"
  format: "yaml"
  sortable_fields:
    fields: [title, date]
  view_groups:
    - label: Year
      field: date
      pattern: '\d{4}'
  fields:
    - { label: Title, name: title, widget: string }
    - { label: Date, name: date, widget: datetime }
    - { label: Draft, name: draft, widget: boolean, default: true }
    - { label: Description, name: description, widget: text, required: false }
    - { label: Featured Image, name: image, widget: image, required: false }
    - { label: Tags, name: tags, widget: list, required: false }
    - { label: Categories, name: categories, widget: list, required: false }
    - { label: Body, name: body, widget: markdown }
```

### Standard: Pages

```yaml
- name: pages
  label: Pages
  label_singular: Page
  folder: "content"
  create: true
  extension: "md"
  format: "yaml"
  filter: { field: type, value: page }
  fields:
    - { label: Title, name: title, widget: string }
    - { label: Type, name: type, widget: hidden, default: page }
    - { label: Draft, name: draft, widget: boolean, default: true }
    - { label: Weight, name: weight, widget: number, required: false }
    - { label: Description, name: description, widget: text, required: false }
    - { label: Body, name: body, widget: markdown }
```

### Standard: Single File (Site Settings)

```yaml
- name: settings
  label: Site Settings
  files:
    - label: General
      name: general
      file: "data/settings.yaml"
      format: "yaml"
      fields:
        - { label: Site Title, name: title, widget: string }
        - { label: Description, name: description, widget: text }
        - { label: Logo, name: logo, widget: image, required: false }
        - label: Social Links
          name: social
          widget: object
          fields:
            - { label: GitHub, name: github, widget: string, required: false }
            - { label: LinkedIn, name: linkedin, widget: string, required: false }
            - { label: Twitter/X, name: twitter, widget: string, required: false }
```

---

## 5. Domain Collection Patterns

### Consulting / Services Site

```yaml
- name: services
  label: Services
  label_singular: Service
  folder: "content/services"
  create: true
  extension: "md"
  format: "yaml"
  fields:
    - { label: Title, name: title, widget: string }
    - { label: Date, name: date, widget: datetime }
    - { label: Draft, name: draft, widget: boolean, default: true }
    - { label: Weight, name: weight, widget: number, default: 10 }
    - { label: Icon, name: icon, widget: string, required: false, hint: "Lucide icon name" }
    - { label: Summary, name: description, widget: text }
    - { label: Featured Image, name: image, widget: image, required: false }
    - label: Pricing
      name: pricing
      widget: object
      required: false
      fields:
        - { label: Starting Price, name: starting_price, widget: string, required: false }
        - { label: Pricing Model, name: model, widget: select, options: ["fixed", "hourly", "retainer", "custom"], required: false }
    - { label: Body, name: body, widget: markdown }

- name: case_studies
  label: Case Studies
  label_singular: Case Study
  folder: "content/case-studies"
  create: true
  extension: "md"
  format: "yaml"
  fields:
    - { label: Title, name: title, widget: string }
    - { label: Date, name: date, widget: datetime }
    - { label: Draft, name: draft, widget: boolean, default: true }
    - { label: Client, name: client, widget: string }
    - { label: Industry, name: industry, widget: string, required: false }
    - { label: Summary, name: description, widget: text }
    - { label: Featured Image, name: image, widget: image, required: false }
    - label: Outcomes
      name: outcomes
      widget: list
      required: false
      fields:
        - { label: Metric, name: metric, widget: string }
        - { label: Result, name: result, widget: string }
    - { label: Testimonial, name: testimonial, widget: text, required: false }
    - { label: Tags, name: tags, widget: list, required: false }
    - { label: Body, name: body, widget: markdown }

- name: testimonials
  label: Testimonials
  label_singular: Testimonial
  folder: "content/testimonials"
  create: true
  extension: "md"
  format: "yaml"
  fields:
    - { label: Name, name: title, widget: string }
    - { label: Date, name: date, widget: datetime }
    - { label: Draft, name: draft, widget: boolean, default: false }
    - { label: Role, name: role, widget: string }
    - { label: Company, name: company, widget: string }
    - { label: Photo, name: image, widget: image, required: false }
    - { label: Quote, name: body, widget: markdown }
    - { label: Rating, name: rating, widget: number, min: 1, max: 5, required: false }

- name: team
  label: Team
  label_singular: Team Member
  folder: "content/team"
  create: true
  extension: "md"
  format: "yaml"
  fields:
    - { label: Name, name: title, widget: string }
    - { label: Date, name: date, widget: datetime }
    - { label: Draft, name: draft, widget: boolean, default: true }
    - { label: Role, name: role, widget: string }
    - { label: Weight, name: weight, widget: number, default: 10 }
    - { label: Photo, name: image, widget: image, required: false }
    - { label: Email, name: email, widget: string, required: false }
    - { label: LinkedIn, name: linkedin, widget: string, required: false }
    - label: Certifications
      name: certifications
      widget: list
      required: false
    - { label: Bio, name: body, widget: markdown }
```

### Medical Practice

```yaml
- name: providers
  label: Providers
  label_singular: Provider
  folder: "content/providers"
  create: true
  extension: "md"
  format: "yaml"
  fields:
    - { label: Name, name: title, widget: string }
    - { label: Date, name: date, widget: datetime }
    - { label: Draft, name: draft, widget: boolean, default: true }
    - { label: Credentials, name: credentials, widget: string, hint: "e.g., MD, DO, NP, PA-C" }
    - { label: Specialty, name: specialty, widget: string }
    - { label: Weight, name: weight, widget: number, default: 10 }
    - { label: Photo, name: image, widget: image, required: false }
    - { label: Accepting New Patients, name: accepting_patients, widget: boolean, default: true }
    - label: Languages
      name: languages
      widget: list
      default: ["English"]
    - label: Education
      name: education
      widget: list
      required: false
      fields:
        - { label: Degree, name: degree, widget: string }
        - { label: Institution, name: institution, widget: string }
        - { label: Year, name: year, widget: string, required: false }
    - label: Board Certifications
      name: board_certifications
      widget: list
      required: false
    - label: Locations
      name: locations
      widget: list
      required: false
      hint: "Location names matching entries in the Locations collection"
    - { label: Bio, name: body, widget: markdown }

- name: locations
  label: Locations
  label_singular: Location
  folder: "content/locations"
  create: true
  extension: "md"
  format: "yaml"
  fields:
    - { label: Name, name: title, widget: string }
    - { label: Date, name: date, widget: datetime }
    - { label: Draft, name: draft, widget: boolean, default: true }
    - { label: Weight, name: weight, widget: number, default: 10 }
    - { label: Address, name: address, widget: string }
    - { label: City, name: city, widget: string }
    - { label: State, name: state, widget: string }
    - { label: ZIP, name: zip, widget: string }
    - { label: Phone, name: phone, widget: string }
    - { label: Fax, name: fax, widget: string, required: false }
    - { label: Photo, name: image, widget: image, required: false }
    - label: Hours
      name: hours
      widget: list
      fields:
        - { label: Day, name: day, widget: select, options: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"] }
        - { label: Open, name: open, widget: string, hint: "e.g., 8:00 AM" }
        - { label: Close, name: close, widget: string, hint: "e.g., 5:00 PM" }
    - { label: Map Embed URL, name: map_url, widget: string, required: false }
    - { label: Details, name: body, widget: markdown }

- name: medical_services
  label: Services & Specialties
  label_singular: Service
  folder: "content/services"
  create: true
  extension: "md"
  format: "yaml"
  fields:
    - { label: Title, name: title, widget: string }
    - { label: Date, name: date, widget: datetime }
    - { label: Draft, name: draft, widget: boolean, default: true }
    - { label: Weight, name: weight, widget: number, default: 10 }
    - { label: Icon, name: icon, widget: string, required: false }
    - { label: Summary, name: description, widget: text }
    - { label: Featured Image, name: image, widget: image, required: false }
    - label: Insurance Accepted
      name: insurance
      widget: list
      required: false
    - { label: Body, name: body, widget: markdown }

- name: patient_resources
  label: Patient Resources
  label_singular: Resource
  folder: "content/patient-resources"
  create: true
  extension: "md"
  format: "yaml"
  fields:
    - { label: Title, name: title, widget: string }
    - { label: Date, name: date, widget: datetime }
    - { label: Draft, name: draft, widget: boolean, default: true }
    - { label: Weight, name: weight, widget: number, default: 10 }
    - { label: Category, name: category, widget: select, options: ["Forms", "Insurance", "Preparation", "FAQ", "Education"] }
    - { label: File, name: file, widget: file, required: false }
    - { label: Body, name: body, widget: markdown }
```

### Content / Blog Site

```yaml
- name: posts
  label: Posts
  label_singular: Post
  folder: "content/posts"
  create: true
  slug: "{{year}}-{{month}}-{{day}}-{{slug}}"
  extension: "md"
  format: "yaml"
  fields:
    - { label: Title, name: title, widget: string }
    - { label: Date, name: date, widget: datetime }
    - { label: Draft, name: draft, widget: boolean, default: true }
    - { label: Author, name: author, widget: relation, collection: authors, search_fields: [title], value_field: title, required: false }
    - { label: Description, name: description, widget: text, required: false }
    - { label: Featured Image, name: image, widget: image, required: false }
    - { label: Tags, name: tags, widget: list, required: false }
    - { label: Categories, name: categories, widget: list, required: false }
    - { label: Body, name: body, widget: markdown }

- name: authors
  label: Authors
  label_singular: Author
  folder: "content/authors"
  create: true
  extension: "md"
  format: "yaml"
  fields:
    - { label: Name, name: title, widget: string }
    - { label: Date, name: date, widget: datetime }
    - { label: Draft, name: draft, widget: boolean, default: false }
    - { label: Photo, name: image, widget: image, required: false }
    - { label: Role, name: role, widget: string, required: false }
    - { label: Email, name: email, widget: string, required: false }
    - { label: Website, name: website, widget: string, required: false }
    - { label: Bio, name: body, widget: markdown }
```

---

## 6. Widget Reference

| Widget | Hugo Front Matter | Notes |
|--------|-------------------|-------|
| `string` | `field: "value"` | Single line text |
| `text` | `field: "multi\nline"` | Multi-line text |
| `number` | `field: 42` | Add `value_type: int` or `float` |
| `boolean` | `field: true` | |
| `datetime` | `field: 2025-01-15T10:00:00Z` | |
| `select` | `field: "option1"` | Single value from `options` list |
| `relation` | `field: "referenced-slug"` | Links to another collection |
| `list` | `field: [a, b, c]` | Simple list or complex with subfields |
| `object` | `field:\n  sub: val` | Nested fields |
| `markdown` | Body content | Always use for `body` field |
| `image` | `field: "/images/uploads/pic.jpg"` | |
| `file` | `field: "/files/doc.pdf"` | Any file type |
| `hidden` | `field: "value"` | Not shown in editor |
| `color` | `field: "#ff0000"` | |
| `map` | `field:\n  lat: 0\n  lng: 0` | Geographic coordinates |
| `code` | `field: "code string"` | With syntax highlighting |

### Relation Widget Example

```yaml
- label: Author
  name: author
  widget: relation
  collection: "authors"
  search_fields: ["title"]
  value_field: "title"
  display_fields: ["title"]
```

### List Widget with Subfields

```yaml
- label: Gallery
  name: gallery
  widget: list
  fields:
    - { label: Image, name: image, widget: image }
    - { label: Caption, name: caption, widget: string }
    - { label: Alt Text, name: alt, widget: string }
```

---

## 7. Authentication

Sveltia CMS requires OAuth. The recommended approach is `sveltia-cms-auth` deployed as a Cloudflare Worker.

### Setup Steps

**1. Register GitHub OAuth App:**
- Go to GitHub → Settings → Developer Settings → OAuth Apps → New
- Application name: "Sveltia CMS - [Your Site]"
- Homepage URL: `https://your-site.com`
- Authorization callback URL: `https://your-auth-worker.workers.dev/callback`
- Save Client ID and Client Secret

**2. Deploy Cloudflare Worker:**

```bash
npm create cloudflare@latest sveltia-cms-auth
cd sveltia-cms-auth
npm install @sveltia/cms-auth
```

**`src/index.js`:**
```javascript
import { createAuth } from '@sveltia/cms-auth';
export default { fetch: createAuth() };
```

**Set secrets:**
```bash
npx wrangler secret put GITHUB_CLIENT_ID
npx wrangler secret put GITHUB_CLIENT_SECRET
# Optional: restrict to specific domains
npx wrangler secret put ALLOWED_DOMAINS  # e.g., "your-site.com"
```

**Deploy:**
```bash
npx wrangler deploy
```

**3. Update CMS `config.yml`:**
```yaml
backend:
  name: github
  repo: "owner/repo"
  branch: main
  base_url: "https://sveltia-cms-auth.your-account.workers.dev"
```

### Alternative Auth Options

**Option 2: Self-hosted on any platform**
Deploy `sveltia-cms-auth` as a Node.js app anywhere that supports it. Same env vars: `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, `ALLOWED_DOMAINS`.

**Option 3: Existing Netlify site**
If you have a Netlify site, you can use Netlify's built-in OAuth provider (under Site Settings → Access Control → OAuth) even while hosting on CF Pages. Set `base_url` to your Netlify site URL.

---

## 8. Deployment: Cloudflare Pages

### Connect Repository (Dashboard)

1. Cloudflare Dashboard → Pages → Create a project → Connect to Git
2. Select GitHub repo
3. Build settings:
   - **Framework preset**: None (or Hugo if available)
   - **Build command**: `hugo --minify` (or `npm install && hugo --minify` if using Basecoat npm path)
   - **Build output directory**: `public`
4. Environment variables:
   - `HUGO_VERSION`: `0.145.0` (or latest)
   - `NODE_VERSION`: `20` (if using npm)

### GitHub Actions CI/CD (Recommended)

The bootstrap script creates `.github/workflows/deploy.yml` automatically. It handles:
- **Push to main** → build Hugo → deploy to Cloudflare Pages (production)
- **Pull requests** → build Hugo → validate build succeeds (no deploy)

**Required GitHub Secrets:**

| Secret | Description | Where to find |
|---|---|---|
| `CLOUDFLARE_API_TOKEN` | API token with Pages write permission | CF Dashboard → API Tokens → "Edit Cloudflare Workers" template |
| `CLOUDFLARE_ACCOUNT_ID` | Your Cloudflare account ID | CF Dashboard → any zone → Overview sidebar |

**Required GitHub Variable:**

| Variable | Description | Where to set |
|---|---|---|
| `PAGES_PROJECT_NAME` | Your CF Pages project name | Repository → Settings → Variables → Actions |

**Workflow (npm + Tailwind path):**

```yaml
name: Deploy

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: true
          fetch-depth: 0

      - uses: peaceiris/actions-hugo@v3
        with:
          hugo-version: 'latest'
          extended: true

      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: 'pnpm'

      - run: pnpm install --frozen-lockfile
      - run: hugo --minify

      - name: Deploy to Cloudflare Pages
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        uses: cloudflare/wrangler-action@v3
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          command: pages deploy public --project-name ${{ vars.PAGES_PROJECT_NAME }}
```

**CDN-only sites:** Remove the pnpm/Node steps — only Hugo setup + `hugo --minify` are needed.

**PR preview deployments:** Uncomment the preview section in the generated workflow, or see the `cloudflare-pages` skill's `references/ci-cd-templates.md` for the full pattern.

### Custom Domain

1. CF Pages → your project → Custom domains → Add
2. Add CNAME record in CF DNS pointing to `your-project.pages.dev`

### Alternative: Vercel / Netlify / GitHub Pages

**Vercel** — `vercel.json`:
```json
{
  "build": {
    "env": { "HUGO_VERSION": "0.145.0" }
  }
}
```
Build command: `hugo --minify`, output: `public`.

**Netlify** — `netlify.toml`:
```toml
[build]
  command = "hugo --minify"
  publish = "public"

[build.environment]
  HUGO_VERSION = "0.145.0"
```

**GitHub Pages** — `.github/workflows/hugo.yml`:
```yaml
name: Deploy Hugo to GitHub Pages

on:
  push:
    branches: [main]

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: true
          fetch-depth: 0

      - uses: peaceiris/actions-hugo@v3
        with:
          hugo-version: 'latest'
          extended: true

      - run: hugo --minify

      - uses: actions/upload-pages-artifact@v3
        with:
          path: ./public

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
```

---

## 9. TinaCMS Field Mapping Reference

When converting from TinaCMS, map `tina/config.ts` schema to `config.yml`:

### Field Types

| TinaCMS `type` | Sveltia `widget` | Config Notes |
|----------------|------------------|--------------|
| `string` | `string` | Direct mapping |
| `string` + `list: true` | `list` | Simple string list |
| `string` + `options` | `select` | Map `options` array |
| `number` | `number` | Add `value_type: int` or `float` |
| `boolean` | `boolean` | Direct mapping |
| `datetime` | `datetime` | Direct mapping |
| `image` | `image` | Adjust media paths |
| `rich-text` | `markdown` | Loses Tina visual editing features |
| `object` | `object` | Map each subfield recursively |
| `object` + `list: true` | `list` with `fields` | List of objects |
| `reference` | `relation` | Set `collection`, `search_fields`, `value_field` |

### Structure Mapping

```
# TinaCMS (tina/config.ts)
collections: [{
  name: "post",
  label: "Blog Posts",
  path: "content/posts",
  format: "md",
  fields: [...]
}]

# Sveltia CMS (static/admin/config.yml)
collections:
  - name: post
    label: Blog Posts
    folder: "content/posts"
    create: true
    extension: "md"
    format: "yaml"
    fields: [...]
```

### Media Path Mapping

```
# TinaCMS
media: {
  tina: {
    mediaRoot: "images",
    publicFolder: "static"
  }
}

# Sveltia CMS
media_folder: "static/images"
public_folder: "/images"
```

### What Doesn't Transfer

- **Visual block editing** — Tina's rich-text editor with custom React components has no Sveltia equivalent. Content still renders in Hugo; editors just use Markdown.
- **GraphQL queries** — No more `tina/__generated__/`. Content is plain Markdown + YAML.
- **Template components** — Tina rich-text `templates` (for shortcodes in the visual editor) don't carry over. Shortcodes in content still work in Hugo; editors type them manually.
- **Real-time preview** — Tina's live preview requires its GraphQL server. Sveltia doesn't have real-time preview; editors save → Hugo rebuilds → page refreshes.
- **TinaCloud auth** — Replaced by GitHub OAuth + CF Worker.

---

## 10. Common Gotchas

### 1. TOML Front Matter Bug
**Problem:** Sveltia generates malformed TOML (`+++`) front matter.
**Fix:** Always set `extension: "md"` and `format: "yaml"` on every collection. Convert existing TOML content with `scripts/convert-toml-to-yaml.py`.

### 2. Missing `extension` / `format`
**Problem:** CMS creates files with `.yml` extension or TOML format.
**Fix:** Explicitly set both on every folder collection.

### 3. Media Upload Path Mismatch
**Problem:** Images uploaded via CMS return 404.
**Fix:** Ensure `media_folder` starts with `static/` and `public_folder` is the URL path (without `static/`).

### 4. OAuth Redirect Loop
**Problem:** Login redirects back to login page.
**Fix:** Check `base_url` in config matches the deployed Worker URL exactly. Verify `Authorization callback URL` in GitHub OAuth app settings matches `<worker-url>/callback`.

### 5. Collections Not Loading
**Problem:** CMS shows empty or errors loading content.
**Fix:** Verify `folder` paths match actual directory structure. Paths are relative to repo root. Check `branch` matches your default branch name.

### 6. Date Format Issues
**Problem:** Hugo can't parse CMS-generated dates.
**Fix:** Use `datetime` widget (generates ISO 8601). In Hugo templates: `{{ .Date.Format "January 2, 2006" }}`.

### 7. Slug Conflicts
**Problem:** CMS generates slugs that conflict with Hugo's URL structure.
**Fix:** Set explicit `slug` pattern: `"{{year}}-{{month}}-{{day}}-{{slug}}"` or `"{{slug}}"`.

### 8. Tailwind Purges Basecoat Classes
**Problem:** Basecoat component classes missing in production build.
**Fix:** Ensure `hugo.yaml` has the `build.buildStats` and `module.mounts` config. The `hugo_stats.json` file must be mounted into assets for Tailwind to read.

---

## 11. Converting Front Matter Formats

### TOML → YAML Example

**Before (TOML):**
```
+++
title = "My Post"
date = 2025-01-15T10:00:00Z
draft = false
tags = ["hugo", "cms"]
[params]
  image = "/images/post.jpg"
+++
```

**After (YAML):**
```yaml
---
title: "My Post"
date: 2025-01-15T10:00:00Z
draft: false
tags:
  - hugo
  - cms
params:
  image: "/images/post.jpg"
---
```

Use `scripts/convert-toml-to-yaml.py` for batch conversion.

---

## 12. i18n / Multilingual

### Hugo Languages Config

```yaml
defaultContentLanguage: en
languages:
  en:
    languageName: English
    weight: 1
  es:
    languageName: Español
    weight: 2
```

### CMS i18n Config

```yaml
i18n:
  structure: multiple_folders
  locales: [en, es]
  default_locale: en
```

Structure options:
- `multiple_folders` — `content/en/posts/`, `content/es/posts/` (Hugo's folder-based approach)
- `multiple_files` — `content/posts/hello.en.md`, `content/posts/hello.es.md` (Hugo's filename-based approach)
- `single_file` — Both languages in one file (not recommended for Hugo)
