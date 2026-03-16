# Schema Design

## Config File

`tina/config.ts` (ESM-only in TinaCMS 3.x):

```typescript
import { defineConfig } from 'tinacms'

export default defineConfig({
  branch: process.env.NEXT_PUBLIC_TINA_BRANCH || process.env.VERCEL_GIT_COMMIT_REF || 'main',
  clientId: process.env.TINA_PUBLIC_CLIENT_ID || '',
  token: process.env.TINA_TOKEN || '',
  build: { outputFolder: 'admin', publicFolder: 'public' },
  media: { tina: { mediaRoot: 'uploads', publicFolder: 'public' } },
  schema: { collections: [ /* ... */ ] },
})
```

Use `templates/tina-config-starter.ts` as a starting point.

## Field Types

| TinaCMS Type | Widget | Notes |
|-------------|--------|-------|
| `string` | Text input | `isTitle: true` for list display |
| `string` + `list: true` | Tag input | With `options` array = select dropdown |
| `string` + `ui.component: 'textarea'` | Textarea | Multi-line text |
| `number` | Number input | |
| `boolean` | Toggle | Defaults to false |
| `datetime` | Date picker | ISO format stored |
| `image` | Image picker | Uses configured media store |
| `rich-text` | Markdown editor | `isBody: true` for document body. Toolbar: `heading`, `link`, `image`, `quote`, `ul`, `ol`, `bold`, `italic`, `code`, `codeBlock`, `mermaid`, `table`, `raw`, `embed`. Set `showFloatingToolbar: false` to disable. |
| `rich-text` + `templates` | MDX editor | Custom embedded components rendered as `<ComponentName prop="value" />` |
| `object` | Field group | Nested fields |
| `object` + `list: true` | Repeatable group | Always add `ui.itemProps` |
| `object` + `list: true` + `templates` | Block selector | The "blocks pattern" |
| `reference` | Document picker | `collections: ['collectionName']` |

**Field names must be alphanumeric + underscores only.** Hyphens or spaces cause build errors. Also avoid `children` as a field name (conflicts with TinaCMS internals).

**New in TinaCMS 3.x:**
- `ui.halfWidth` (3.2.0) -- render text fields at half width (two fields side by side)
- `openFormOnCreate` (3.6.0) -- auto-navigate into object form after creation
- `addItemBehavior: 'prepend'` -- add new list items at top instead of bottom
- Fuzzy search is now the default (3.3.0)
- `reference` fields cannot be `list: true` -- wrap in an object field as workaround

## Collection Patterns

### Folder Collection (pages, posts)

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
  fields: [ /* ... */ ],
}
```

### Singleton Collection (global settings, navigation)

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
  fields: [ /* ... */ ],
}
```

## Blocks Pattern

The primary architecture for page-builder-style editing. Used on landing pages and marketing pages. (Single rich-text body is fine for blog posts.)

```typescript
{
  name: 'blocks',
  label: 'Page Sections',
  type: 'object',
  list: true,
  ui: { visualSelector: true },
  templates: [heroBlock, featuresBlock, contentBlock, ctaBlock, faqBlock],
}
```

### Block Template Structure

```typescript
const heroBlock = {
  name: 'hero',
  label: 'Hero Section',
  ui: {
    previewSrc: '/admin/blocks/hero.png',  // Optional: visual selector thumbnail
    defaultItem: {
      heading: 'Your Heading Here',
      subheading: 'A compelling subheading.',
      ctaText: 'Get Started',
      ctaUrl: '#',
      style: 'centered',
    },
  },
  fields: [
    { name: 'heading', label: 'Heading', type: 'string' as const, required: true },
    { name: 'subheading', label: 'Subheading', type: 'string' as const },
    { name: 'backgroundImage', label: 'Background Image', type: 'image' as const },
    {
      name: 'style', label: 'Layout', type: 'string' as const,
      options: [
        { value: 'centered', label: 'Centered' },
        { value: 'left', label: 'Left Aligned' },
        { value: 'split', label: 'Split (Text + Image)' },
      ],
    },
    { name: 'ctaText', label: 'Button Text', type: 'string' as const },
    { name: 'ctaUrl', label: 'Button URL', type: 'string' as const },
  ],
}
```

### Common Blocks

A production site typically needs 5-13 blocks:

| Block | Fields |
|-------|--------|
| **Hero** | Heading, subheading, CTA, background image, layout style |
| **Features** | Heading, items list (icon, title, description), columns enum |
| **Content** | Heading, rich-text body, optional image, image position |
| **CTA Banner** | Heading, subheading, button text/URL, style |
| **FAQ** | Heading, items list (question, answer) |
| **Testimonials** | Items list (quote, author, role, avatar) |
| **Gallery** | Images list |
| **Stats** | Number highlights (value, label) |
| **Team** | People list (name, role, photo, bio) |
| **Pricing** | Plans list (name, price, features, CTA) |
| **Logos** | Images list (partner/client logos) |
| **Video** | Embed URL, poster image |
| **Contact** | Form embed or contact info |

## Field Quality Checklist

Apply to every field:

| Attribute | When |
|-----------|------|
| `isTitle: true` | On the title field of every collection |
| `required: true` | On mandatory fields |
| `ui.validate` | Character limits (60 for titles, 160 for descriptions), format checks |
| `ui.description` | Editorial guidance for non-obvious fields |
| `ui.component: 'textarea'` | Multi-line string fields |
| `ui.component: 'group'` | Collapsible secondary groups (SEO, advanced) |
| `ui.itemProps` | **Every** list field -- meaningful labels, never "Item 0" |

**List item labels:**
```typescript
ui: {
  itemProps: (item) => ({
    label: item?.title || item?.name || item?.heading || 'Untitled',
  }),
}
```

## Reusable Field Groups

Extract as shared variables for DRY schemas:

```typescript
const ctaFields = [
  { name: 'text', label: 'Button Text', type: 'string' as const },
  { name: 'url', label: 'Button URL', type: 'string' as const },
  { name: 'style', label: 'Style', type: 'string' as const, options: ['primary', 'secondary', 'ghost'] },
  { name: 'openInNewTab', label: 'Open in New Tab', type: 'boolean' as const },
]

const sectionStyleFields = [
  { name: 'layout', label: 'Layout', type: 'string' as const, options: ['default', 'wide', 'narrow'] },
  { name: 'background', label: 'Background', type: 'string' as const, options: [
    { value: 'bg-white', label: 'White' },
    { value: 'bg-gray-50', label: 'Light Gray' },
    { value: 'bg-gray-900', label: 'Dark' },
  ]},
]
```

**Style enums must map to Tailwind classes** -- never expose raw CSS values to editors.

**Tailwind v4 dynamic classes:** Enums producing class names like `bg-blue-500` are not found by Tailwind's source scanner. Fix with `@source inline()` directive (Tailwind v4.1+):

```css
/* In your global CSS */
@source inline("{hover:,}bg-{red,green,blue,gray}-{50,100,500,900}");
```

Or use a mapping object so Tailwind sees complete class strings at build time.

## Content Hooks

Auto-compute fields on save:

```typescript
ui: {
  beforeSubmit: async ({ values }) => ({
    ...values,
    slug: values.title.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, ''),
    modifiedDate: new Date().toISOString(),
  }),
}
```

## Reference Fields

Cross-collection relationships:

```typescript
{ name: 'author', label: 'Author', type: 'reference', collections: ['author'] }
{ name: 'relatedPosts', label: 'Related Posts', type: 'reference', list: true, collections: ['post'] }
```

**Performance note:** Reference dropdowns can be slow/503 with large collections (>500 docs). Use a custom field component with pagination for large sets.

## Custom Field Components

Use `wrapFieldsWithMeta()` to preserve label/description/validation rendering:

```typescript
import { wrapFieldsWithMeta } from 'tinacms'

{
  name: 'rating',
  type: 'number',
  ui: {
    component: wrapFieldsWithMeta(({ input }) => (
      <input type="range" min="0" max="10" step="1" {...input} />
    ))
  }
}
```

Props received: `field` (definition), `input` (value + callbacks), `meta` (dirty, valid), `form` (CMS form for cross-field access via `form.change()`).

Set `ui.component: 'hidden'` to hide a field while keeping it programmatically accessible. Use `ui.component: () => null` to render nothing.

## Static Params

Generate static paths at build time:

```typescript
export async function generateStaticParams() {
  const pages = await client.queries.pageConnection()
  return pages.data.pageConnection.edges?.map((edge) => ({
    slug: edge?.node?._sys.filename,
  })) || []
}
```

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Single rich-text for landing pages | Blocks list with templates (rich-text fine for blog posts) |
| Raw CSS values in schema | Enums mapped to Tailwind classes |
| Hyphens/spaces in field names | Alphanumeric + underscores only |
| Missing `ui.itemProps` on lists | Label functions showing meaningful content |
| Ungrouped Tina dependency updates | Package grouping in RenovateBot/Dependabot |
| Inline media (base64) | External media provider for production |
| No block fallback | Default case in renderer for unknown types |
