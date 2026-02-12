// tina/config.ts — Full-featured TinaCMS configuration for Next.js 16
// Customize collections, fields, and media for your project.

import { defineConfig } from 'tinacms'

// Reusable SEO field group — add to every page/post collection
const seoFields = [
  {
    name: 'metaTitle',
    label: 'Meta Title',
    type: 'string' as const,
    description: 'Overrides page title in search results. Keep under 60 chars.',
    ui: {
      validate: (val: string) =>
        val && val.length > 60 ? `${val.length}/60 — too long` : undefined,
    },
  },
  {
    name: 'metaDescription',
    label: 'Meta Description',
    type: 'string' as const,
    description: '120-160 characters. Shown below title in search results.',
    ui: {
      component: 'textarea',
      validate: (val: string) =>
        val && val.length > 160 ? `${val.length}/160 — too long` : undefined,
    },
  },
  {
    name: 'ogImage',
    label: 'Social Share Image',
    type: 'image' as const,
    description: '1200×630px recommended.',
  },
  { name: 'noIndex', label: 'Hide from Search Engines', type: 'boolean' as const },
  { name: 'canonicalUrl', label: 'Canonical URL', type: 'string' as const },
]

// --- Block Templates ---
// Add your block templates here. Each becomes a drag-and-drop section.

const heroBlock = {
  name: 'hero',
  label: 'Hero',
  ui: {
    previewSrc: '/admin/blocks/hero.png',
    defaultItem: {
      heading: 'Your Heading Here',
      subheading: 'A compelling subheading that supports your main message.',
      ctaText: 'Get Started',
      ctaUrl: '#',
    },
  },
  fields: [
    { name: 'heading', label: 'Heading', type: 'string' as const, required: true },
    { name: 'subheading', label: 'Subheading', type: 'string' as const },
    { name: 'backgroundImage', label: 'Background Image', type: 'image' as const },
    {
      name: 'style',
      label: 'Layout',
      type: 'string' as const,
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

const featuresBlock = {
  name: 'features',
  label: 'Features Grid',
  ui: {
    previewSrc: '/admin/blocks/features.png',
    defaultItem: {
      heading: 'Features',
      items: [
        { title: 'Feature 1', description: 'Description of feature 1.' },
        { title: 'Feature 2', description: 'Description of feature 2.' },
        { title: 'Feature 3', description: 'Description of feature 3.' },
      ],
    },
  },
  fields: [
    { name: 'heading', label: 'Section Heading', type: 'string' as const },
    { name: 'subheading', label: 'Section Subheading', type: 'string' as const },
    {
      name: 'columns',
      label: 'Columns',
      type: 'string' as const,
      options: ['2', '3', '4'],
    },
    {
      name: 'items',
      label: 'Features',
      type: 'object' as const,
      list: true,
      ui: {
        itemProps: (item: any) => ({ label: item?.title || 'Feature' }),
      },
      fields: [
        { name: 'icon', label: 'Icon', type: 'string' as const },
        { name: 'title', label: 'Title', type: 'string' as const, required: true },
        { name: 'description', label: 'Description', type: 'string' as const, ui: { component: 'textarea' } },
      ],
    },
  ],
}

const contentBlock = {
  name: 'content',
  label: 'Content Section',
  fields: [
    { name: 'heading', label: 'Heading', type: 'string' as const },
    { name: 'body', label: 'Body', type: 'rich-text' as const },
    { name: 'image', label: 'Image', type: 'image' as const },
    {
      name: 'imagePosition',
      label: 'Image Position',
      type: 'string' as const,
      options: ['left', 'right', 'above', 'below', 'none'],
    },
  ],
}

const ctaBlock = {
  name: 'ctaBanner',
  label: 'CTA Banner',
  ui: {
    defaultItem: {
      heading: 'Ready to get started?',
      buttonText: 'Contact Us',
      buttonUrl: '/contact',
    },
  },
  fields: [
    { name: 'heading', label: 'Heading', type: 'string' as const, required: true },
    { name: 'subheading', label: 'Subheading', type: 'string' as const },
    { name: 'buttonText', label: 'Button Text', type: 'string' as const },
    { name: 'buttonUrl', label: 'Button URL', type: 'string' as const },
    {
      name: 'style',
      label: 'Style',
      type: 'string' as const,
      options: ['primary', 'dark', 'gradient'],
    },
  ],
}

const faqBlock = {
  name: 'faq',
  label: 'FAQ',
  fields: [
    { name: 'heading', label: 'Section Heading', type: 'string' as const },
    {
      name: 'items',
      label: 'Questions',
      type: 'object' as const,
      list: true,
      ui: {
        itemProps: (item: any) => ({ label: item?.question || 'Question' }),
      },
      fields: [
        { name: 'question', label: 'Question', type: 'string' as const, required: true },
        { name: 'answer', label: 'Answer', type: 'rich-text' as const },
      ],
    },
  ],
}

// --- Main Config ---

export default defineConfig({
  branch:
    process.env.NEXT_PUBLIC_TINA_BRANCH ||
    process.env.VERCEL_GIT_COMMIT_REF ||
    'main',
  clientId: process.env.TINA_PUBLIC_CLIENT_ID || '',
  token: process.env.TINA_TOKEN || '',

  build: {
    outputFolder: 'admin',
    publicFolder: 'public',
  },

  media: {
    // Option A: Repo-based (simplest, images in Git)
    tina: {
      mediaRoot: 'uploads',
      publicFolder: 'public',
    },
    // Option B: Cloudinary (uncomment and remove tina block above)
    // loadCustomStore: async () => {
    //   const pack = await import('next-tinacms-cloudinary')
    //   return pack.TinaCloudCloudinaryMediaStore
    // },
  },

  schema: {
    collections: [
      // --- Pages ---
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
          {
            name: 'title',
            label: 'Page Title',
            type: 'string',
            isTitle: true,
            required: true,
          },
          { name: 'draft', label: 'Draft', type: 'boolean' },
          {
            name: 'blocks',
            label: 'Page Sections',
            type: 'object',
            list: true,
            ui: { visualSelector: true },
            templates: [heroBlock, featuresBlock, contentBlock, ctaBlock, faqBlock],
          },
          {
            name: 'seo',
            label: 'SEO & Social',
            type: 'object',
            ui: { component: 'group' },
            fields: seoFields,
          },
        ],
      },

      // --- Blog Posts ---
      {
        name: 'post',
        label: 'Blog Posts',
        path: 'content/posts',
        format: 'mdx',
        ui: {
          router: ({ document }) => `/blog/${document._sys.filename}`,
        },
        fields: [
          {
            name: 'title',
            label: 'Title',
            type: 'string',
            isTitle: true,
            required: true,
          },
          { name: 'date', label: 'Publish Date', type: 'datetime', required: true },
          { name: 'author', label: 'Author', type: 'reference', collections: ['author'] },
          {
            name: 'excerpt',
            label: 'Excerpt',
            type: 'string',
            ui: { component: 'textarea' },
          },
          { name: 'featuredImage', label: 'Featured Image', type: 'image' },
          {
            name: 'tags',
            label: 'Tags',
            type: 'string',
            list: true,
            options: ['featured', 'news', 'tutorial', 'case-study'],
          },
          { name: 'draft', label: 'Draft', type: 'boolean' },
          { name: 'body', label: 'Body', type: 'rich-text', isBody: true },
          {
            name: 'seo',
            label: 'SEO & Social',
            type: 'object',
            ui: { component: 'group' },
            fields: seoFields,
          },
        ],
      },

      // --- Authors ---
      {
        name: 'author',
        label: 'Authors',
        path: 'content/authors',
        format: 'json',
        fields: [
          { name: 'name', label: 'Name', type: 'string', isTitle: true, required: true },
          { name: 'avatar', label: 'Avatar', type: 'image' },
          { name: 'bio', label: 'Bio', type: 'string', ui: { component: 'textarea' } },
          { name: 'email', label: 'Email', type: 'string' },
          {
            name: 'social',
            label: 'Social Links',
            type: 'object',
            fields: [
              { name: 'twitter', label: 'Twitter/X', type: 'string' },
              { name: 'linkedin', label: 'LinkedIn', type: 'string' },
              { name: 'website', label: 'Website', type: 'string' },
            ],
          },
        ],
      },

      // --- Site Settings (Singleton) ---
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
            name: 'defaultSeo',
            label: 'Default SEO',
            type: 'object',
            ui: { component: 'group' },
            fields: seoFields,
          },
          {
            name: 'social',
            label: 'Social Links',
            type: 'object',
            fields: [
              { name: 'twitter', label: 'Twitter/X Handle', type: 'string' },
              { name: 'linkedin', label: 'LinkedIn URL', type: 'string' },
              { name: 'github', label: 'GitHub URL', type: 'string' },
              { name: 'instagram', label: 'Instagram URL', type: 'string' },
            ],
          },
        ],
      },

      // --- Navigation (Singleton) ---
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
              itemProps: (item: any) => ({ label: item?.label || 'Nav Item' }),
            },
            fields: [
              { name: 'label', label: 'Label', type: 'string', required: true },
              { name: 'url', label: 'URL', type: 'string', required: true },
            ],
          },
        ],
      },
    ],
  },
})
