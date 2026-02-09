"use client";

// ── Kitchen Sink — Starter Template (React / Next.js) ────────────────────────
//
// This is a structural skeleton for the sink page. Replace placeholder sections
// with real component imports. Every rendered element must be an importable
// module — no inline-only markup.
//
// Production guard: returns null in production.
// Franchise placeholder: [FRANCHISE_NAME]

import { useState } from "react";

// ── Replace these with real imports from your component library ───────────────
// import { Button }    from "@/components/ui/button";
// import { Badge }     from "@/components/ui/badge";
// import { Card }      from "@/components/ui/card";
// import { Alert }     from "@/components/ui/alert";
// import { Dialog }    from "@/components/ui/dialog";
// import { Tabs }      from "@/components/ui/tabs";
// import { Input }     from "@/components/ui/input";
// import { Skeleton }  from "@/components/ui/skeleton";

// ── Section Config ───────────────────────────────────────────────────────────
const SECTIONS = [
  { id: "tokens", label: "Design Tokens" },
  { id: "voice", label: "Voice & Tone" },
  { id: "illustrations", label: "Illustrations" },
  { id: "header", label: "Site Header" },
  { id: "footer", label: "Site Footer" },
  { id: "typo", label: "Typography" },
  { id: "buttons", label: "Buttons" },
  { id: "badges", label: "Badges" },
  { id: "cards", label: "Cards" },
  { id: "forms", label: "Form Controls" },
  { id: "modals", label: "Modals & Dialogs" },
  { id: "alerts", label: "Alerts" },
  { id: "motion", label: "Motion Sampler" },
  { id: "tier2", label: "Tier 2 Components" },
  { id: "tier3", label: "Tier 3 Components" },
  { id: "chaos", label: "Chaos Laboratory" },
] as const;

// ── Main Page ────────────────────────────────────────────────────────────────
export default function KitchenSinkPage() {
  // Production guard — never render in production
  if (process.env.NEXT_PUBLIC_VERCEL_ENV === "production") return null;

  return (
    <div className="flex min-h-screen bg-background text-foreground">
      {/* ── Sidebar Navigation ── */}
      <nav className="sticky top-0 hidden h-screen w-56 shrink-0 overflow-y-auto border-r bg-muted/30 p-4 lg:block">
        <h2 className="mb-4 text-sm font-semibold uppercase tracking-wider text-muted-foreground">
          Kitchen Sink
        </h2>
        <ul className="space-y-1">
          {SECTIONS.map((s) => (
            <li key={s.id}>
              <a
                href={`#${s.id}`}
                className="block rounded-md px-3 py-1.5 text-sm text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground"
              >
                {s.label}
              </a>
            </li>
          ))}
        </ul>
      </nav>

      {/* ── Main Content ── */}
      <main className="flex-1 space-y-16 p-6 lg:p-10">
        <header>
          <h1 className="text-4xl font-bold tracking-tight">Kitchen Sink</h1>
          <p className="mt-2 text-lg text-muted-foreground">
            Living source of truth for the design system.
          </p>
          <p className="mt-1 text-sm text-muted-foreground">
            Franchise: <strong>[FRANCHISE_NAME]</strong>
          </p>
        </header>

        {/* ── Design Tokens ── */}
        <section id="tokens" className="space-y-6">
          <h2 className="border-b pb-2 text-2xl font-semibold">Design Tokens</h2>
          {/* Color palette — render from CSS custom properties or Tailwind config */}
          <div className="grid grid-cols-3 gap-4 sm:grid-cols-4 md:grid-cols-6">
            {[
              { name: "background", css: "var(--background)" },
              { name: "foreground", css: "var(--foreground)" },
              { name: "primary", css: "var(--primary)" },
              { name: "secondary", css: "var(--secondary)" },
              { name: "muted", css: "var(--muted)" },
              { name: "accent", css: "var(--accent)" },
              { name: "destructive", css: "var(--destructive)" },
            ].map((token) => (
              <div key={token.name} className="space-y-1.5">
                <div
                  className="h-16 rounded-lg border shadow-sm"
                  style={{ backgroundColor: token.css }}
                />
                <p className="text-xs font-medium">{token.name}</p>
                <p className="font-mono text-xs text-muted-foreground">{token.css}</p>
              </div>
            ))}
          </div>
          {/* Typography scale, spacing ramp */}
        </section>

        {/* ── Buttons (representative section showing variant × size grid) ── */}
        <section id="buttons" className="space-y-6">
          <h2 className="border-b pb-2 text-2xl font-semibold">Buttons</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left">
                  <th className="px-4 py-2 font-medium">Variant</th>
                  <th className="px-4 py-2 font-medium">Small</th>
                  <th className="px-4 py-2 font-medium">Medium</th>
                  <th className="px-4 py-2 font-medium">Large</th>
                </tr>
              </thead>
              <tbody>
                {/* Map over variants × sizes using your real <Button> component:
                {(["primary","secondary","outline","ghost","destructive"] as const).map(
                  (variant) => (
                    <tr key={variant} className="border-b">
                      <td className="px-4 py-3 font-mono text-xs">{variant}</td>
                      {(["sm","md","lg"] as const).map((size) => (
                        <td key={size} className="px-4 py-3">
                          <Button variant={variant} size={size}>{variant}</Button>
                        </td>
                      ))}
                    </tr>
                  )
                )} */}
              </tbody>
            </table>
          </div>
          {/* States: default, disabled, focus-visible */}
        </section>

        {/* ── Modals (representative interactive section) ── */}
        <ModalSection />

        {/* ── Remaining sections follow the same pattern ──
          See SKILL.md Phase 6 "Sink Page Layout" for the full section order:
          - Voice & Tone, Illustrations, Site Header, Site Footer, Typography
          - Badges, Cards, Form Controls, Alerts, Motion Sampler
          - Tier 2 (Tabs, Breadcrumbs, Accordion, Tooltip, Dropdown)
          - Tier 3 (Content-Author Components)
          - Chaos Laboratory (token vis, state matrix, dark/light, responsive stubs)
        */}
      </main>
    </div>
  );
}

// ── Modal Section (example of interactive sub-component) ─────────────────────
function ModalSection() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <section id="modals" className="space-y-6">
      <h2 className="border-b pb-2 text-2xl font-semibold">Modals & Dialogs</h2>
      {/* Replace with real <Button> and <Dialog> components */}
      <button
        onClick={() => setIsOpen(true)}
        className="rounded-md border px-4 py-2 text-sm hover:bg-accent"
      >
        Open Modal
      </button>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div
            className="absolute inset-0 bg-black/50 motion-safe:animate-[fade-in_200ms_ease-out]"
            onClick={() => setIsOpen(false)}
          />
          <div className="relative z-10 w-full max-w-md rounded-lg border bg-background p-6 shadow-xl motion-safe:animate-[modal-in_300ms_ease-out]">
            <h3 className="text-lg font-semibold">Confirm Action</h3>
            <p className="mt-2 text-sm text-muted-foreground">
              Destructive confirmation with specific details per voice guidelines.
            </p>
            <div className="mt-6 flex justify-end gap-3">
              <button
                onClick={() => setIsOpen(false)}
                className="rounded-md border px-3 py-1.5 text-sm hover:bg-accent"
              >
                Cancel
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="rounded-md bg-destructive px-3 py-1.5 text-sm text-destructive-foreground hover:bg-destructive/90"
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
