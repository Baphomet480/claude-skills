import { NextResponse } from 'next/server';
// IMPORT_YOUR_DATA_FETCHERS_HERE

export const dynamic = 'force-static';

export async function GET() {
  try {
    // 1. Fetch your data from CMS, local files, database, etc.
    const rawData = [];

    // 2. Map data into the standardized SearchResult format
    // Mandatory fields: title (string), href (string), type (string)
    // Optional (but recommended for full-text search): content (string)
    const results = rawData.map(item => ({
      title: item.title,
      href: `/content/${item.slug}`,
      type: 'Article', // Used for grouping
      content: item.body // Raw markdown/text for full-text fuzzy matching
    }));

    return NextResponse.json(results);
  } catch (error) {
    console.error('Search API Error:', error);
    return NextResponse.json({ error: 'Failed to fetch search data' }, { status: 500 });
  }
}
