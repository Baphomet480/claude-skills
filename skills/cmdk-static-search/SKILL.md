---
name: cmdk-static-fulltext-search
description: A high-performance, database-free, edge-cached full-text search implementation using `cmdk` and Next.js static API routes.
---

# CMDK Static Full-Text Search Pattern

This pattern implements a global `Cmd+K` command menu that can search across massive amounts of Markdown/MDX content instantly without paying for a database or serverless execution costs.

## When to Use

- When a project requires a global search feature.
- When the content is file-system based (MDX, Markdown) or fetched from a headless CMS at build time.
- When you want to avoid third-party search tools like Algolia.
- When you need full-text search (searching the raw body text) rather than just title/URL matching.

## Implementation Details

### 1. Static API Route (`src/app/api/search/route.ts`)

Instead of fetching data on every keypress or paying for serverless execution, we force Next.js to bake our entire content payload into a static JSON edge-cached file at build time.

```ts
import { NextResponse } from "next/server";
// Import your data fetchers/local FS queries here

// CRITICAL: Force static generation to avoid $Vercel serverless execution fees.
export const dynamic = "force-static";

export async function GET() {
  // 1. Fetch all posts/MDX files
  // 2. Map them into `{ title, href, type, content: rawMdxString }`
  // 3. Return as a single `NextResponse.json()`
}
```

### 2. High-Performance CmdK Component (`src/components/ui/SearchPalette.tsx`)

Because we pass raw Markdown chunks (often thousands of characters long) into `cmdk` to be searched, `cmdk`'s default `command-score` algorithm will block the main thread and freeze the browser on every keypress. We bypass this with a basic native `.includes()` search.

```tsx
import { useState, useEffect, useCallback } from "react";
import { Command } from "cmdk";

export function SearchPalette() {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [results, setResults] = useState([]);

  // Fetch data only when they open the palette
  useEffect(() => {
    if (open && results.length === 0) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      fetch("/api/search")
        .then((res) => res.json())
        .then(setResults);
    }
  }, [open, results.length]);

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh] px-4">
      {/* ... Add backdrop & Cmd K event listener ... */}
      <Command
        shouldFilter={true}
        // CRITICAL: Fast native filter prevents main-thread blocking on giant text payloads
        filter={(value, searchString) => {
          if (value.toLowerCase().includes(searchString.toLowerCase()))
            return 1;
          return 0;
        }}
      >
        <Command.Input value={search} onValueChange={setSearch} />
        <Command.List>
          {results.map((result) => (
            <Command.Item
              key={result.href}
              // CRITICAL: Combine type, title, and raw content for the full-text matching string
              value={`${result.type} ${result.title} ${result.content || ""}`}
              onSelect={() => router.push(result.href)}
            >
              {/* Title Rendering */}
              {result.title}

              {/* Dynamic Snippet Generator: Call a method to extract +/- 40 characters from where `search` matched `result.content` */}
            </Command.Item>
          ))}
        </Command.List>
      </Command>
    </div>
  );
}
```

### 3. Dynamic Snippet Generation

Extract the surrounding 80 characters of text where the match occurs, sanitize Markdown symbols, and highlight the query string within the snippet:

```tsx
const getSnippet = (content?: string, query?: string) => {
  if (!content || !query || query.length < 3) return null;
  const cleanContent = content
    .replace(/[#*\`_\[\]()]/g, " ")
    .replace(/\s+/g, " ");
  const index = cleanContent.toLowerCase().indexOf(query.toLowerCase());
  if (index === -1) return null;

  const start = Math.max(0, index - 40);
  const end = Math.min(cleanContent.length, index + query.length + 40);

  let snippet = cleanContent.slice(start, end);
  if (start > 0) snippet = "..." + snippet;
  if (end < cleanContent.length) snippet = snippet + "...";

  const regex = new RegExp(`(${query})`, "gi");
  const parts = snippet.split(regex);

  return (
    <span>
      {parts.map((part, i) =>
        part.toLowerCase() === query.toLowerCase() ? (
          <span key={i} className="font-bold text-accent">
            {part}
          </span>
        ) : (
          part
        ),
      )}
    </span>
  );
};
```
