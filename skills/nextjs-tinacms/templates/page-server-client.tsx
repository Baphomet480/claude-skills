// =============================================================================
// Next.js 16 + TinaCMS Page Pattern
// Server Component fetches data → Client Component enables visual editing
// =============================================================================

// --- FILE 1: app/[slug]/page.tsx (Server Component) ---

import type { Metadata } from 'next'
import { client } from '@/tina/__generated__/client'
import { PageClient } from './PageClient'
import { generatePageMetadata } from '@/lib/metadata'

// Generate metadata for SEO/OG/Twitter
export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>
}): Promise<Metadata> {
  const { slug } = await params
  const result = await client.queries.page({ relativePath: `${slug}.md` })
  return generatePageMetadata(result.data.page, 'https://yourdomain.com')
}

// Generate static paths at build time
export async function generateStaticParams() {
  const pages = await client.queries.pageConnection()
  return (
    pages.data.pageConnection.edges?.map((edge) => ({
      slug: edge?.node?._sys.filename,
    })) || []
  )
}

// Server Component — fetches data, passes to client
export default async function Page({
  params,
}: {
  params: Promise<{ slug: string }> // ← Next.js 16: params is a Promise
}) {
  const { slug } = await params // ← Must await
  const result = await client.queries.page({ relativePath: `${slug}.md` })

  return (
    <PageClient
      query={result.query}
      variables={result.variables}
      data={result.data}
    />
  )
}


// --- FILE 2: app/[slug]/PageClient.tsx (Client Component) ---

// 'use client'
//
// import { useTina, tinaField } from 'tinacms/dist/react'
// import { TinaMarkdown } from 'tinacms/dist/rich-text'
// import { BlockRenderer } from '@/components/blocks/BlockRenderer'
//
// interface PageClientProps {
//   query: string
//   variables: Record<string, any>
//   data: any
// }
//
// export function PageClient(props: PageClientProps) {
//   // useTina enables live editing — data updates in real-time when editing in /admin
//   const { data } = useTina({
//     query: props.query,
//     variables: props.variables,
//     data: props.data,
//   })
//
//   const page = data.page
//
//   return (
//     <main>
//       {/* data-tina-field enables click-to-edit in the visual editor */}
//       <h1 data-tina-field={tinaField(page, 'title')}>{page.title}</h1>
//
//       {/* Render page blocks */}
//       {page.blocks && <BlockRenderer blocks={page.blocks} />}
//     </main>
//   )
// }


// --- FILE 3: lib/metadata.ts (Reusable metadata helper) ---

// import type { Metadata } from 'next'
//
// interface TinaPage {
//   title: string
//   seo?: {
//     metaTitle?: string
//     metaDescription?: string
//     ogImage?: string
//     ogTitle?: string
//     ogDescription?: string
//     twitterCard?: 'summary_large_image' | 'summary'
//     noIndex?: boolean
//     canonicalUrl?: string
//   }
// }
//
// export function generatePageMetadata(page: TinaPage, siteUrl: string): Metadata {
//   const seo = page.seo
//   const title = seo?.metaTitle || page.title
//   const description = seo?.metaDescription || ''
//
//   return {
//     title,
//     description,
//     robots: seo?.noIndex ? { index: false, follow: false } : { index: true, follow: true },
//     alternates: seo?.canonicalUrl ? { canonical: seo.canonicalUrl } : undefined,
//     openGraph: {
//       title: seo?.ogTitle || title,
//       description: seo?.ogDescription || description,
//       images: seo?.ogImage ? [{ url: seo.ogImage, width: 1200, height: 630 }] : undefined,
//       type: 'website',
//     },
//     twitter: {
//       card: seo?.twitterCard || 'summary_large_image',
//       title: seo?.ogTitle || title,
//       description: seo?.ogDescription || description,
//       images: seo?.ogImage ? [seo.ogImage] : undefined,
//     },
//   }
// }


// --- FILE 4: app/[slug]/opengraph-image.tsx (Dynamic OG Image) ---

// import { ImageResponse } from 'next/og'
// import { client } from '@/tina/__generated__/client'
//
// export const size = { width: 1200, height: 630 }
// export const contentType = 'image/png'
// export const alt = 'Page preview image'
//
// export default async function OGImage({
//   params,
// }: {
//   params: Promise<{ slug: string }> // ← Next.js 16: Promise
// }) {
//   const { slug } = await params
//
//   // Check for CMS-managed OG image first
//   const result = await client.queries.page({ relativePath: `${slug}.md` })
//   const page = result.data.page
//
//   // If CMS has a custom OG image, don't generate — Next.js uses the uploaded one
//   // This route only fires if no static OG image exists
//
//   return new ImageResponse(
//     (
//       <div
//         style={{
//           display: 'flex',
//           flexDirection: 'column',
//           justifyContent: 'center',
//           alignItems: 'center',
//           width: '100%',
//           height: '100%',
//           backgroundColor: '#0a0a0a',
//           color: '#ffffff',
//           fontFamily: 'system-ui',
//           padding: '60px',
//         }}
//       >
//         <div style={{ fontSize: 64, fontWeight: 700, textAlign: 'center' }}>
//           {page.title}
//         </div>
//         {page.seo?.metaDescription && (
//           <div
//             style={{
//               fontSize: 28,
//               color: '#a1a1aa',
//               marginTop: 24,
//               textAlign: 'center',
//               maxWidth: '80%',
//             }}
//           >
//             {page.seo.metaDescription}
//           </div>
//         )}
//       </div>
//     ),
//     { ...size }
//   )
// }
