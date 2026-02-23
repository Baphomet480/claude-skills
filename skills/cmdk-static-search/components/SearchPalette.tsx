'use client';

import { useState, useEffect, useCallback } from 'react';
import { Command } from 'cmdk';
import { Search, FileText, ChevronRight, X } from 'lucide-react';
import { useRouter } from 'next/navigation';

type SearchResult = {
  title: string;
  href: string;
  type: string;
  content?: string;
};

export function SearchPalette() {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  // Toggle the menu when ⌘K is pressed
  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen((open) => !open);
      }
    };

    document.addEventListener('keydown', down);
    return () => document.removeEventListener('keydown', down);
  }, []);

  // Fetch data when opened
  useEffect(() => {
    if (open && results.length === 0) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setLoading(true);
      fetch('/api/search')
        .then(res => res.json())
        .then(data => {
          setResults(data);
          setLoading(false);
        })
        .catch(err => {
          console.error('Failed to load search index:', err);
          setLoading(false);
        });
    }
  }, [open, results.length]);

  const runCommand = useCallback((command: () => void) => {
    setOpen(false);
    command();
  }, []);

  const getIcon = (type: string) => {
    // Return appropriate Lucide icons based on result type
    switch(type) {
      case 'Article': return <FileText className="w-4 h-4 text-blue-500 shrink-0" />;
      default: return <FileText className="w-4 h-4 text-gray-400 shrink-0" />;
    }
  };

  const getSnippet = (content?: string, query?: string) => {
    if (!content || !query || query.length < 3) return null;
    
    // Quick sanitization to remove common markdown structural elements
    const cleanContent = content.replace(/[#*`_[\]()]/g, ' ').replace(/\s+/g, ' ');
    const index = cleanContent.toLowerCase().indexOf(query.toLowerCase());
    if (index === -1) return null;
    
    // Extract a 40 character buffer around the match
    const start = Math.max(0, index - 40);
    const end = Math.min(cleanContent.length, index + query.length + 40);
    
    let snippet = cleanContent.slice(start, end);
    if (start > 0) snippet = '...' + snippet;
    if (end < cleanContent.length) snippet = snippet + '...';
    
    // Split to highlight the exact matched substring
    const regex = new RegExp(`(${query})`, 'gi');
    const parts = snippet.split(regex);
    
    return (
      <span className="text-[0.7rem] text-gray-500 mt-0.5 line-clamp-1 leading-snug font-body group-aria-selected:text-gray-300 transition-colors text-left">
        {parts.map((part, i) => 
          part.toLowerCase() === query.toLowerCase() ? <span key={i} className="text-white font-semibold">{part}</span> : part
        )}
      </span>
    );
  };

  // Grouping results
  const groupedResults = results.reduce((acc, curr) => {
    if (!acc[curr.type]) {
      acc[curr.type] = [];
    }
    acc[curr.type].push(curr);
    return acc;
  }, {} as Record<string, SearchResult[]>);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh] px-4">
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black/80 backdrop-blur-sm transition-opacity"
        onClick={() => setOpen(false)}
      />

      <div className="relative z-50 w-full max-w-xl shadow-2xl overflow-hidden rounded-xl border border-gray-800 bg-gray-900">
        <Command
          className="flex flex-col w-full bg-transparent overflow-hidden h-full rounded-xl"
          label="Global Command Menu"
          shouldFilter={true}
          filter={(value, search) => {
            if (value.toLowerCase().includes(search.toLowerCase())) return 1;
            return 0;
          }}
        >
          <div className="flex items-center border-b border-gray-800 px-4 py-3">
            <Search className="w-5 h-5 text-gray-400 mr-3 shrink-0" />
            <Command.Input 
              autoFocus
              value={search}
              onValueChange={setSearch}
              className="flex-1 bg-transparent border-0 outline-hidden font-body text-lg text-white placeholder:text-gray-500" 
              placeholder="Search across the platform..." 
            />
            <button 
              onClick={() => setOpen(false)}
              className="sm:hidden text-xs uppercase tracking-widest text-gray-400 hover:text-white p-2 bg-transparent border-0"
            >
              Cancel
            </button>
            <kbd className="hidden sm:inline-block font-mono text-[10px] text-gray-400 bg-black px-1.5 py-0.5 rounded border border-gray-800 uppercase tracking-widest">
              ESC
            </kbd>
          </div>

          <Command.List className="max-h-[60vh] overflow-y-auto p-2 scrollbar-thin scrollbar-thumb-gray-800 scrollbar-track-transparent">
            {loading && <Command.Loading className="px-4 py-6 text-center text-gray-500 text-sm">Searching...</Command.Loading>}
            {!loading && <Command.Empty className="px-4 py-6 text-center text-gray-500 text-sm">No records found.</Command.Empty>}

            {Object.keys(groupedResults).map(type => (
              <Command.Group 
                key={type} 
                heading={<span className="px-3 py-2 text-xs uppercase tracking-widest text-gray-500 block">{type}s</span>}
              >
                {groupedResults[type].map((result, i) => (
                  <Command.Item
                    key={`${type}-${i}`}
                    value={`${result.type} ${result.title} ${result.content || ''}`}
                    onSelect={() => runCommand(() => router.push(result.href))}
                    className="flex flex-col items-start px-3 py-3 rounded-lg cursor-pointer aria-selected:bg-gray-800 aria-selected:text-white text-gray-400 transition-colors group outline-none"
                  >
                    <div className="flex items-center w-full">
                      {getIcon(result.type)}
                      <div className="ml-3 flex flex-col items-start overflow-hidden flex-1 max-w-[calc(100%-2.5rem)]">
                        <span className="text-[0.95rem] truncate w-full text-left text-white transition-colors">{result.title}</span>
                        {getSnippet(result.content, search)}
                      </div>
                      <ChevronRight className="w-4 h-4 ml-auto opacity-0 group-aria-selected:opacity-100 text-gray-400 transition-opacity shrink-0" />
                    </div>
                  </Command.Item>
                ))}
              </Command.Group>
            ))}
          </Command.List>
        </Command>
      </div>
    </div>
  );
}
