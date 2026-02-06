"use client";

/**
 * Minimal Kitchen Sink — starter template
 *
 * Drop this file into your project's sink route and replace the placeholder
 * components with real imports from your `/components` directory.
 *
 * Route mapping:
 *   Next.js App Router → /app/sink/page.tsx
 *   Vite + React       → /src/pages/sink.tsx  (needs router entry)
 *   Astro              → /src/pages/sink.astro (wrap in a client island)
 */

import { useState } from "react";

// ── Replace these placeholder components with real imports ──────────────────
// import { Button }     from "@/components/ui/button";
// import { Card }       from "@/components/ui/card";
// import { Input }      from "@/components/ui/input";
// import { Badge }      from "@/components/ui/badge";
// import { Alert }      from "@/components/ui/alert";
// import { Modal }      from "@/components/ui/modal";
// import { SiteHeader } from "@/components/layout/site-header";
// import { SiteFooter } from "@/components/layout/site-footer";

// ── Section registry (drives sidebar navigation) ───────────────────────────

const SECTIONS = [
    { id: "site-header", label: "Site Header" },
    { id: "site-footer", label: "Site Footer" },
    { id: "typography", label: "Typography" },
    { id: "buttons", label: "Buttons" },
    { id: "badges", label: "Badges" },
    { id: "cards", label: "Cards" },
    { id: "forms", label: "Form Controls" },
    { id: "modals", label: "Modals & Dialogs" },
    { id: "alerts", label: "Alerts" },
    { id: "colors", label: "Color Palette" },
    { id: "theme-test", label: "Theme Test" },
] as const;

// ── Sink page ──────────────────────────────────────────────────────────────

export default function SinkPage() {
    // Production guard — returns nothing on the live site
    if (process.env.NEXT_PUBLIC_VERCEL_ENV === "production") return null;

    const [modalOpen, setModalOpen] = useState(false);

    return (
        <div className="flex min-h-screen">
            {/* ── Sidebar ── */}
            <nav className="sticky top-0 hidden h-screen w-56 shrink-0 overflow-y-auto border-r p-4 lg:block">
                <h2 className="mb-4 text-sm font-semibold uppercase tracking-wider text-muted-foreground">
                    Components
                </h2>
                <ul className="space-y-1">
                    {SECTIONS.map((s) => (
                        <li key={s.id}>
                            <a
                                href={`#${s.id}`}
                                className="block rounded px-2 py-1 text-sm hover:bg-accent"
                            >
                                {s.label}
                            </a>
                        </li>
                    ))}
                </ul>
            </nav>

            {/* ── Main content ── */}
            <main className="flex-1 space-y-16 p-8 lg:p-12">
                <header>
                    <h1 className="text-4xl font-bold">Kitchen Sink</h1>
                    <p className="mt-2 text-muted-foreground">
                        Component inventory and design system reference.
                    </p>
                </header>

                {/* ── Site Header ── */}
                <section id="site-header" className="space-y-6">
                    <h2 className="border-b pb-2 text-2xl font-semibold">Site Header</h2>
                    <p className="text-sm text-muted-foreground">
                        Rendered inline (not as the page wrapper) to test responsive
                        breakpoints, sticky behavior, and nav states in isolation.
                    </p>
                    {/* Replace with: <SiteHeader /> */}
                    <div className="overflow-hidden rounded-lg border">
                        <header className="flex items-center justify-between bg-background px-6 py-4">
                            <div className="flex items-center gap-3">
                                <div className="h-8 w-8 rounded-full bg-primary" />
                                <span className="text-lg font-bold">Brand</span>
                            </div>
                            <nav className="hidden items-center gap-6 md:flex">
                                <a href="#" className="text-sm font-medium hover:text-primary">Home</a>
                                <a href="#" className="text-sm font-medium hover:text-primary">About</a>
                                <a href="#" className="text-sm font-medium hover:text-primary">Services</a>
                                <a href="#" className="text-sm font-medium hover:text-primary">Contact</a>
                            </nav>
                            <button className="rounded bg-primary px-4 py-2 text-sm text-primary-foreground">
                                CTA
                            </button>
                        </header>
                    </div>
                    <div>
                        <h3 className="mb-3 text-sm font-medium text-muted-foreground">
                            Mobile variant (hamburger)
                        </h3>
                        <div className="max-w-sm overflow-hidden rounded-lg border">
                            <header className="flex items-center justify-between bg-background px-4 py-3">
                                <div className="flex items-center gap-2">
                                    <div className="h-6 w-6 rounded-full bg-primary" />
                                    <span className="text-sm font-bold">Brand</span>
                                </div>
                                <button className="flex h-8 w-8 items-center justify-center rounded hover:bg-accent">
                                    <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                                        <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
                                    </svg>
                                </button>
                            </header>
                        </div>
                    </div>
                </section>

                {/* ── Site Footer ── */}
                <section id="site-footer" className="space-y-6">
                    <h2 className="border-b pb-2 text-2xl font-semibold">Site Footer</h2>
                    <p className="text-sm text-muted-foreground">
                        Rendered inline to test link columns, responsive stacking, and
                        brand consistency at the page boundary.
                    </p>
                    {/* Replace with: <SiteFooter /> */}
                    <div className="overflow-hidden rounded-lg border">
                        <footer className="bg-muted px-6 py-8">
                            <div className="grid gap-8 md:grid-cols-4">
                                <div>
                                    <h4 className="mb-3 text-sm font-semibold">Brand</h4>
                                    <p className="text-xs text-muted-foreground">
                                        A brief tagline or description of the brand.
                                    </p>
                                </div>
                                <div>
                                    <h4 className="mb-3 text-sm font-semibold">Navigation</h4>
                                    <ul className="space-y-1 text-xs text-muted-foreground">
                                        <li><a href="#" className="hover:text-foreground">Home</a></li>
                                        <li><a href="#" className="hover:text-foreground">About</a></li>
                                        <li><a href="#" className="hover:text-foreground">Services</a></li>
                                        <li><a href="#" className="hover:text-foreground">Contact</a></li>
                                    </ul>
                                </div>
                                <div>
                                    <h4 className="mb-3 text-sm font-semibold">Legal</h4>
                                    <ul className="space-y-1 text-xs text-muted-foreground">
                                        <li><a href="#" className="hover:text-foreground">Privacy</a></li>
                                        <li><a href="#" className="hover:text-foreground">Terms</a></li>
                                    </ul>
                                </div>
                                <div>
                                    <h4 className="mb-3 text-sm font-semibold">Social</h4>
                                    <div className="flex gap-3">
                                        <div className="h-8 w-8 rounded bg-foreground/10" />
                                        <div className="h-8 w-8 rounded bg-foreground/10" />
                                        <div className="h-8 w-8 rounded bg-foreground/10" />
                                    </div>
                                </div>
                            </div>
                            <div className="mt-8 border-t pt-4 text-center text-xs text-muted-foreground">
                                © {new Date().getFullYear()} Brand. All rights reserved.
                            </div>
                        </footer>
                    </div>
                </section>

                {/* ── Typography ── */}
                <section id="typography" className="space-y-6">
                    <h2 className="border-b pb-2 text-2xl font-semibold">Typography</h2>
                    <div className="space-y-4">
                        <h1 className="text-5xl font-bold">Heading 1</h1>
                        <h2 className="text-4xl font-semibold">Heading 2</h2>
                        <h3 className="text-3xl font-semibold">Heading 3</h3>
                        <h4 className="text-2xl font-medium">Heading 4</h4>
                        <h5 className="text-xl font-medium">Heading 5</h5>
                        <h6 className="text-lg font-medium">Heading 6</h6>
                        <p>
                            Body text at default size. Replace this with a sentence that
                            exercises your brand voice.
                        </p>
                        <p className="text-sm text-muted-foreground">
                            Small / muted caption text for secondary information.
                        </p>
                        <blockquote className="border-l-4 pl-4 italic text-muted-foreground">
                            A blockquote for callouts or testimonials.
                        </blockquote>
                        <pre className="rounded bg-muted p-4 text-sm">
                            <code>{"const x = 42; // inline code block"}</code>
                        </pre>
                    </div>
                </section>

                {/* ── Buttons ── */}
                <section id="buttons" className="space-y-6">
                    <h2 className="border-b pb-2 text-2xl font-semibold">Buttons</h2>

                    <div>
                        <h3 className="mb-3 text-sm font-medium text-muted-foreground">
                            Variants — replace with real Button imports
                        </h3>
                        <div className="flex flex-wrap items-center gap-3">
                            {/* <Button variant="primary">Primary</Button> */}
                            {/* <Button variant="secondary">Secondary</Button> */}
                            {/* <Button variant="outline">Outline</Button> */}
                            {/* <Button variant="ghost">Ghost</Button> */}
                            {/* <Button variant="destructive">Destructive</Button> */}
                            <button className="rounded bg-primary px-4 py-2 text-primary-foreground">
                                Placeholder Primary
                            </button>
                        </div>
                    </div>

                    <div>
                        <h3 className="mb-3 text-sm font-medium text-muted-foreground">
                            States
                        </h3>
                        <div className="flex flex-wrap items-center gap-3">
                            <button className="rounded bg-primary px-4 py-2 text-primary-foreground">
                                Default
                            </button>
                            <button
                                className="rounded bg-primary px-4 py-2 text-primary-foreground opacity-50"
                                disabled
                            >
                                Disabled
                            </button>
                        </div>
                    </div>
                </section>

                {/* ── Badges ── */}
                <section id="badges" className="space-y-6">
                    <h2 className="border-b pb-2 text-2xl font-semibold">Badges</h2>
                    <div className="flex flex-wrap gap-2">
                        {/* Replace with real Badge imports */}
                        <span className="rounded-full bg-primary/10 px-3 py-1 text-xs font-medium text-primary">
                            Default
                        </span>
                        <span className="rounded-full bg-green-500/10 px-3 py-1 text-xs font-medium text-green-700">
                            Success
                        </span>
                        <span className="rounded-full bg-yellow-500/10 px-3 py-1 text-xs font-medium text-yellow-700">
                            Warning
                        </span>
                        <span className="rounded-full bg-red-500/10 px-3 py-1 text-xs font-medium text-red-700">
                            Error
                        </span>
                    </div>
                </section>

                {/* ── Cards ── */}
                <section id="cards" className="space-y-6">
                    <h2 className="border-b pb-2 text-2xl font-semibold">Cards</h2>
                    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                        {/* Replace with real Card imports */}
                        <div className="rounded-lg border p-6 shadow-sm transition hover:shadow-md">
                            <h3 className="font-semibold">Basic Card</h3>
                            <p className="mt-2 text-sm text-muted-foreground">
                                A simple card with text content.
                            </p>
                        </div>
                        <div className="cursor-pointer rounded-lg border p-6 shadow-sm transition hover:shadow-lg">
                            <h3 className="font-semibold">Interactive Card</h3>
                            <p className="mt-2 text-sm text-muted-foreground">
                                Hover to see the lift effect.
                            </p>
                        </div>
                    </div>
                </section>

                {/* ── Form Controls ── */}
                <section id="forms" className="space-y-6">
                    <h2 className="border-b pb-2 text-2xl font-semibold">
                        Form Controls
                    </h2>
                    <div className="max-w-md space-y-4">
                        {/* Replace with real Input, Select, Checkbox, etc. */}
                        <div>
                            <label className="mb-1 block text-sm font-medium">
                                Text Input
                            </label>
                            <input
                                type="text"
                                placeholder="Enter value…"
                                className="w-full rounded border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                            />
                        </div>
                        <div>
                            <label className="mb-1 block text-sm font-medium">
                                Text Input (error)
                            </label>
                            <input
                                type="text"
                                defaultValue="Bad value"
                                className="w-full rounded border border-red-500 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-500"
                            />
                            <p className="mt-1 text-xs text-red-500">
                                This field is required.
                            </p>
                        </div>
                        <div className="flex items-center gap-2">
                            <input type="checkbox" id="demo-check" className="rounded" />
                            <label htmlFor="demo-check" className="text-sm">
                                Checkbox label
                            </label>
                        </div>
                    </div>
                </section>

                {/* ── Modals ── */}
                <section id="modals" className="space-y-6">
                    <h2 className="border-b pb-2 text-2xl font-semibold">
                        Modals & Dialogs
                    </h2>
                    <button
                        onClick={() => setModalOpen(true)}
                        className="rounded bg-primary px-4 py-2 text-primary-foreground"
                    >
                        Open Modal
                    </button>
                    {modalOpen && (
                        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
                            <div className="w-full max-w-md rounded-lg bg-background p-6 shadow-xl">
                                <h3 className="text-lg font-semibold">Example Modal</h3>
                                <p className="mt-2 text-sm text-muted-foreground">
                                    This modal opens and closes. Replace with your real Modal
                                    component.
                                </p>
                                <button
                                    onClick={() => setModalOpen(false)}
                                    className="mt-4 rounded bg-primary px-4 py-2 text-primary-foreground"
                                >
                                    Close
                                </button>
                            </div>
                        </div>
                    )}
                </section>

                {/* ── Alerts ── */}
                <section id="alerts" className="space-y-6">
                    <h2 className="border-b pb-2 text-2xl font-semibold">Alerts</h2>
                    <div className="space-y-3">
                        {/* Replace with real Alert imports */}
                        <div className="rounded border-l-4 border-blue-500 bg-blue-50 p-4 text-sm text-blue-800 dark:bg-blue-950 dark:text-blue-200">
                            <strong>Info:</strong> This is an informational message.
                        </div>
                        <div className="rounded border-l-4 border-green-500 bg-green-50 p-4 text-sm text-green-800 dark:bg-green-950 dark:text-green-200">
                            <strong>Success:</strong> Operation completed.
                        </div>
                        <div className="rounded border-l-4 border-red-500 bg-red-50 p-4 text-sm text-red-800 dark:bg-red-950 dark:text-red-200">
                            <strong>Error:</strong> Something went wrong.
                        </div>
                    </div>
                </section>

                {/* ── Color Palette (Chaos Lab) ── */}
                <section id="colors" className="space-y-6">
                    <h2 className="border-b pb-2 text-2xl font-semibold">
                        Color Palette
                    </h2>
                    <p className="text-sm text-muted-foreground">
                        Enumerate your theme tokens here. For Tailwind v4, read CSS custom
                        properties from your theme. For v3, read from tailwind.config.
                    </p>
                    {/* Placeholder — replace with programmatic token grid */}
                    <div className="grid grid-cols-3 gap-4 sm:grid-cols-4 md:grid-cols-6">
                        {[
                            { name: "background", cls: "bg-background" },
                            { name: "foreground", cls: "bg-foreground" },
                            { name: "primary", cls: "bg-primary" },
                            { name: "secondary", cls: "bg-secondary" },
                            { name: "accent", cls: "bg-accent" },
                            { name: "destructive", cls: "bg-destructive" },
                            { name: "muted", cls: "bg-muted" },
                        ].map((c) => (
                            <div key={c.name} className="space-y-1.5">
                                <div
                                    className={`h-16 rounded-lg border shadow-sm ${c.cls}`}
                                />
                                <p className="text-xs font-medium">{c.name}</p>
                            </div>
                        ))}
                    </div>
                </section>

                {/* ── Theme Test (Chaos Lab) ── */}
                <section id="theme-test" className="space-y-6">
                    <h2 className="border-b pb-2 text-2xl font-semibold">Theme Test</h2>
                    <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
                        <div
                            className="rounded-xl border bg-background p-6"
                            data-theme="light"
                        >
                            <h3 className="mb-4 text-sm font-semibold uppercase tracking-wider">
                                Light Mode
                            </h3>
                            <p className="text-sm">
                                Render a representative sample of components here.
                            </p>
                        </div>
                        <div className="dark rounded-xl border bg-background p-6">
                            <h3 className="mb-4 text-sm font-semibold uppercase tracking-wider">
                                Dark Mode
                            </h3>
                            <p className="text-sm">
                                Same components, forced dark class wrapper.
                            </p>
                        </div>
                    </div>
                </section>
            </main>
        </div>
    );
}
