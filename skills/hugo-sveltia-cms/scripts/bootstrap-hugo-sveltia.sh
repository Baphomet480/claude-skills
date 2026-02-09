#!/usr/bin/env bash
set -euo pipefail

# Bootstrap a Hugo + Sveltia CMS + Basecoat site
# Usage: ./bootstrap-hugo-sveltia.sh --name my-site --repo user/repo --auth-url https://worker.workers.dev [--cdn]

SITE_NAME=""
REPO=""
AUTH_URL=""
USE_CDN=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --name) SITE_NAME="$2"; shift 2 ;;
    --repo) REPO="$2"; shift 2 ;;
    --auth-url) AUTH_URL="$2"; shift 2 ;;
    --cdn) USE_CDN=true; shift ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

if [[ -z "$SITE_NAME" ]]; then
  echo "Error: --name is required"
  echo "Usage: $0 --name my-site --repo user/repo --auth-url https://worker.workers.dev [--cdn]"
  exit 1
fi

REPO="${REPO:-owner/repo}"
AUTH_URL="${AUTH_URL:-https://your-auth-worker.workers.dev}"

echo "🚀 Creating Hugo site: $SITE_NAME"
hugo new site "$SITE_NAME" --format yaml
cd "$SITE_NAME"

# --- Basecoat + Tailwind setup ---
if [[ "$USE_CDN" == false ]]; then
  echo "📦 Setting up npm + Tailwind + Basecoat..."
  npm init -y --silent
  npm install -D tailwindcss @tailwindcss/cli basecoat-css --silent

  mkdir -p assets/css
  cat > assets/css/main.css << 'CSS'
@import "tailwindcss";
@import "basecoat-css";
CSS
fi

# --- Directory structure ---
echo "📁 Creating directory structure..."
mkdir -p archetypes content/posts static/admin static/images/uploads data layouts/_default layouts/partials/components

# --- Hugo config ---
cat > hugo.yaml << YAML
baseURL: "https://example.com"
languageCode: "en-us"
title: "${SITE_NAME}"

build:
  buildStats:
    enable: true
  cachebusters:
    - source: 'assets/notwatching/hugo_stats\\.json'
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

params:
  description: "A new Hugo site with Sveltia CMS and Basecoat UI"

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
YAML

# --- Admin interface ---
cat > static/admin/index.html << 'HTML'
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="color-scheme" content="light dark" />
  <title>Content Manager</title>
</head>
<body>
  <script src="https://unpkg.com/@sveltia/cms/dist/sveltia-cms.js"></script>
</body>
</html>
HTML

cat > static/admin/config.yml << YAML
# yaml-language-server: \$schema=https://unpkg.com/@sveltia/cms/schema/sveltia-cms.json

backend:
  name: github
  repo: "${REPO}"
  branch: main
  base_url: "${AUTH_URL}"

media_folder: "static/images/uploads"
public_folder: "/images/uploads"

collections:
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
    fields:
      - { label: Title, name: title, widget: string }
      - { label: Date, name: date, widget: datetime }
      - { label: Draft, name: draft, widget: boolean, default: true }
      - { label: Description, name: description, widget: text, required: false }
      - { label: Featured Image, name: image, widget: image, required: false }
      - { label: Tags, name: tags, widget: list, required: false }
      - { label: Categories, name: categories, widget: list, required: false }
      - { label: Body, name: body, widget: markdown }

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
YAML

# --- Layouts ---

# Determine CSS include based on approach
if [[ "$USE_CDN" == true ]]; then
  CSS_INCLUDE='    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/basecoat-css@latest/dist/basecoat.cdn.min.css">
    <script src="https://cdn.jsdelivr.net/npm/basecoat-css@latest/dist/js/basecoat.min.js" defer></script>'
else
  CSS_INCLUDE='    {{ with (templates.Defer (dict "key" "global")) }}
      {{ partial "css.html" . }}
    {{ end }}'

  # Create CSS partial
  cat > layouts/partials/css.html << 'GOHTML'
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
GOHTML
fi

cat > layouts/_default/baseof.html << GOHTML
<!doctype html>
<html lang="{{ .Site.LanguageCode }}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{ if not .IsHome }}{{ .Title }} | {{ end }}{{ .Site.Title }}</title>
  <meta name="description" content="{{ with .Params.description }}{{ . }}{{ else }}{{ .Site.Params.description }}{{ end }}">
${CSS_INCLUDE}
</head>
<body class="min-h-screen bg-background text-foreground">
  <header class="border-b">
    <nav class="container mx-auto px-4 py-4 flex items-center justify-between">
      <a href="/" class="text-lg font-semibold">{{ .Site.Title }}</a>
      <div class="flex gap-4">
        {{ range .Site.Menus.main }}
          <a href="{{ .URL }}" class="text-sm text-muted-foreground hover:text-foreground">{{ .Name }}</a>
        {{ end }}
      </div>
    </nav>
  </header>
  <main class="container mx-auto px-4 py-8">
    {{ block "main" . }}{{ end }}
  </main>
  <footer class="border-t mt-16">
    <div class="container mx-auto px-4 py-8 text-sm text-muted-foreground">
      &copy; {{ now.Year }} {{ .Site.Title }}
    </div>
  </footer>
</body>
</html>
GOHTML

cat > layouts/index.html << 'GOHTML'
{{ define "main" }}
  <h1 class="text-3xl font-bold mb-8">{{ .Site.Title }}</h1>
  <p class="text-muted-foreground mb-8">{{ .Site.Params.description }}</p>
  <div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
    {{ range first 9 (where .Site.RegularPages.ByDate.Reverse "Section" "posts") }}
      <div class="card">
        {{ with .Params.image }}
          <img src="{{ . }}" alt="{{ $.Title }}" class="card-image">
        {{ end }}
        <div class="card-body">
          <h2 class="card-title">
            <a href="{{ .Permalink }}">{{ .Title }}</a>
          </h2>
          <p class="text-sm text-muted-foreground">{{ .Date.Format "January 2, 2006" }}</p>
          <p>{{ .Summary }}</p>
        </div>
      </div>
    {{ end }}
  </div>
{{ end }}
GOHTML

cat > layouts/_default/list.html << 'GOHTML'
{{ define "main" }}
  <h1 class="text-3xl font-bold mb-8">{{ .Title }}</h1>
  <div class="space-y-6">
    {{ range .Pages }}
      <article class="card">
        <div class="card-body">
          <h2 class="card-title">
            <a href="{{ .Permalink }}">{{ .Title }}</a>
          </h2>
          <p class="text-sm text-muted-foreground">{{ .Date.Format "January 2, 2006" }}</p>
          {{ with .Params.description }}<p>{{ . }}</p>{{ end }}
        </div>
      </article>
    {{ end }}
  </div>
  {{ template "_internal/pagination.html" . }}
{{ end }}
GOHTML

cat > layouts/_default/single.html << 'GOHTML'
{{ define "main" }}
  <article class="max-w-prose mx-auto">
    <header class="mb-8">
      <h1 class="text-3xl font-bold mb-2">{{ .Title }}</h1>
      <p class="text-sm text-muted-foreground">{{ .Date.Format "January 2, 2006" }}</p>
      {{ with .Params.tags }}
        <div class="flex gap-2 mt-4">
          {{ range . }}
            <span class="badge">{{ . }}</span>
          {{ end }}
        </div>
      {{ end }}
    </header>
    {{ with .Params.image }}
      <img src="{{ . }}" alt="{{ $.Title }}" class="rounded-lg mb-8 w-full">
    {{ end }}
    <div class="prose prose-neutral dark:prose-invert max-w-none">
      {{ .Content }}
    </div>
  </article>
{{ end }}
GOHTML

# --- Component partials ---
cat > layouts/partials/components/card.html << 'GOHTML'
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
GOHTML

cat > layouts/partials/components/badge.html << 'GOHTML'
{{- $text := .text -}}
{{- $variant := .variant | default "default" -}}
<span class="badge badge-{{ $variant }}">{{ $text }}</span>
GOHTML

# --- Archetypes ---
cat > archetypes/posts.md << 'YAML'
---
title: "{{ replace .Name "-" " " | title }}"
date: {{ .Date }}
draft: true
description: ""
image: ""
tags: []
categories: []
---
YAML

cat > archetypes/default.md << 'YAML'
---
title: "{{ replace .Name "-" " " | title }}"
date: {{ .Date }}
draft: true
type: page
description: ""
---
YAML

# --- Sample content ---
cat > content/posts/hello-world.md << 'YAML'
---
title: "Hello World"
date: 2025-01-15T10:00:00Z
draft: false
description: "Welcome to our new site built with Hugo, Sveltia CMS, and Basecoat UI."
tags:
  - welcome
  - hugo
categories:
  - General
---

This is the first post on the site. Edit it via the CMS at `/admin/` or directly in this file.
YAML

cat > data/settings.yaml << 'YAML'
title: "${SITE_NAME}"
description: "A new Hugo site with Sveltia CMS and Basecoat UI"
YAML

# --- .gitignore ---
cat > .gitignore << 'EOF'
/public
/resources
.hugo_build.lock
node_modules/
hugo_stats.json
EOF

# --- GitHub Actions workflow ---
echo "⚙️  Creating GitHub Actions workflow..."
mkdir -p .github/workflows

if [[ "$USE_CDN" == true ]]; then
  cat > .github/workflows/deploy.yml << 'YAML'
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

      - run: hugo --minify

      - name: Deploy to Cloudflare Pages
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        uses: cloudflare/wrangler-action@v3
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          command: pages deploy public --project-name ${{ vars.PAGES_PROJECT_NAME }}

      # -- Uncomment for PR preview deployments --
      # - name: Deploy PR Preview
      #   if: github.event_name == 'pull_request'
      #   uses: cloudflare/wrangler-action@v3
      #   with:
      #     apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
      #     accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
      #     command: >-
      #       pages deploy public
      #       --project-name ${{ vars.PAGES_PROJECT_NAME }}
      #       --branch ${{ github.head_ref }}
YAML
else
  cat > .github/workflows/deploy.yml << 'YAML'
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

      # -- Uncomment for PR preview deployments --
      # - name: Deploy PR Preview
      #   if: github.event_name == 'pull_request'
      #   uses: cloudflare/wrangler-action@v3
      #   with:
      #     apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
      #     accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
      #     command: >-
      #       pages deploy public
      #       --project-name ${{ vars.PAGES_PROJECT_NAME }}
      #       --branch ${{ github.head_ref }}
YAML
fi

echo ""
echo "✅ Site created: $SITE_NAME"
echo ""
echo "Next steps:"
echo "  cd $SITE_NAME"
echo "  hugo server"
echo "  # Visit http://localhost:1313 for the site"
echo "  # Visit http://localhost:1313/admin/ for the CMS (Chromium browser)"
echo ""
echo "Before deploying:"
echo "  1. Update 'repo' in static/admin/config.yml"
echo "  2. Set up GitHub OAuth App"
echo "  3. Deploy sveltia-cms-auth Cloudflare Worker"
echo "  4. Update 'base_url' in static/admin/config.yml"
echo "  5. Connect repo to Cloudflare Pages"
echo "  6. Set GitHub Secrets: CLOUDFLARE_API_TOKEN, CLOUDFLARE_ACCOUNT_ID"
echo "  7. Set GitHub Variable: PAGES_PROJECT_NAME"
echo ""
echo "CI/CD workflow created at .github/workflows/deploy.yml"
echo "  Push to main → build + deploy to Cloudflare Pages"
echo "  Pull requests → build validation only"
