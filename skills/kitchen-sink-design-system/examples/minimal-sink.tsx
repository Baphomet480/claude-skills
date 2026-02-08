"use client";

// ── Kitchen Sink — Design System Reference Page ─────────────────────────────
//
// This page is the living source of truth for the project's design system.
// It renders every component, token, and content pattern in one place.
//
// Production guard: this page should never render in production.
// Franchise placeholder: [FRANCHISE_NAME] (set in GEMINI.md)
//
// Replace placeholder components with real imports from /components.
// Every rendered element must be an importable module — no inline-only markup.

// ── Imports ─────────────────────────────────────────────────────────────────
// Replace these with real imports from your component library:
//
// import { Button }     from "@/components/ui/button";
// import { Card }       from "@/components/ui/card";
// import { Input }      from "@/components/ui/input";
// import { Badge }      from "@/components/ui/badge";
// import { Alert }      from "@/components/ui/alert";
// import { Dialog }     from "@/components/ui/dialog";
// import { Tabs }       from "@/components/ui/tabs";
// import { Accordion }  from "@/components/ui/accordion";
// import { Tooltip }    from "@/components/ui/tooltip";
// import { Toggle }     from "@/components/ui/toggle";
// import { Skeleton }   from "@/components/ui/skeleton";

import { useState } from "react";

// ── CVA Example: Button (base + variant pattern) ───────────────────────────
// In a real project, this lives in /components/ui/button.tsx.
// Shown inline here as the canonical reference pattern.

import { cva, type VariantProps } from "class-variance-authority";

function cn(...inputs: (string | undefined | null | false)[]) {
    return inputs.filter(Boolean).join(" ");
}

const buttonVariants = cva(
    // Base: shared structure (always applied)
    [
        "inline-flex items-center justify-center gap-2 rounded-md font-medium",
        "transition-colors duration-100 ease-out",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
        "disabled:pointer-events-none disabled:opacity-50",
    ],
    {
        variants: {
            variant: {
                primary: "bg-primary text-primary-foreground hover:bg-primary/90",
                secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
                outline: "border border-input bg-transparent hover:bg-accent hover:text-accent-foreground",
                ghost: "hover:bg-accent hover:text-accent-foreground",
                destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
                link: "text-primary underline-offset-4 hover:underline",
            },
            size: {
                sm: "h-8 px-3 text-sm",
                md: "h-10 px-4 text-sm",
                lg: "h-12 px-6 text-base",
            },
        },
        compoundVariants: [
            { variant: "destructive", size: "lg", class: "font-semibold" },
        ],
        defaultVariants: {
            variant: "primary",
            size: "md",
        },
    }
);

interface ButtonProps
    extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> { }

function Button({ className, variant, size, ...props }: ButtonProps) {
    return (
        <button
            className={cn(buttonVariants({ variant, size }), className ?? "")}
            {...props}
        />
    );
}

// ── CVA Example: Badge ─────────────────────────────────────────────────────
const badgeVariants = cva(
    "inline-flex items-center rounded-full px-3 py-1 text-xs font-medium transition-colors",
    {
        variants: {
            variant: {
                default: "bg-primary/10 text-primary",
                secondary: "bg-secondary text-secondary-foreground",
                success: "bg-green-500/10 text-green-700 dark:text-green-400",
                warning: "bg-amber-500/10 text-amber-700 dark:text-amber-400",
                destructive: "bg-destructive/10 text-destructive",
                outline: "border border-input text-foreground",
            },
        },
        defaultVariants: { variant: "default" },
    }
);

interface BadgeProps
    extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> { }

function Badge({ className, variant, ...props }: BadgeProps) {
    return <span className={cn(badgeVariants({ variant }), className ?? "")} {...props} />;
}

// ── CVA Example: Alert ─────────────────────────────────────────────────────
const alertVariants = cva(
    "relative w-full rounded-lg border p-4 text-sm transition-colors [&>svg]:absolute [&>svg]:left-4 [&>svg]:top-4",
    {
        variants: {
            variant: {
                info: "border-blue-200 bg-blue-50 text-blue-900 dark:border-blue-800 dark:bg-blue-950 dark:text-blue-100",
                success: "border-green-200 bg-green-50 text-green-900 dark:border-green-800 dark:bg-green-950 dark:text-green-100",
                warning: "border-amber-200 bg-amber-50 text-amber-900 dark:border-amber-800 dark:bg-amber-950 dark:text-amber-100",
                destructive: "border-destructive/50 bg-destructive/5 text-destructive dark:border-destructive dark:bg-destructive/10",
            },
        },
        defaultVariants: { variant: "info" },
    }
);

interface AlertProps
    extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof alertVariants> { }

function Alert({ className, variant, ...props }: AlertProps) {
    return <div role="alert" className={cn(alertVariants({ variant }), className ?? "")} {...props} />;
}

// ── Section Config ──────────────────────────────────────────────────────────
const SECTIONS = [
    { id: "tokens", label: "Design Tokens" },
    { id: "voice", label: "Voice & Tone" },
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

// ── Main Page ───────────────────────────────────────────────────────────────
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
                        Franchise: <strong>[FRANCHISE_NAME]</strong> — all placeholder content uses this universe.
                    </p>
                </header>

                {/* ════════════════════════════════════════════════════════════════ */}
                {/* SECTION: Design Tokens                                         */}
                {/* ════════════════════════════════════════════════════════════════ */}
                <section id="tokens" className="space-y-6">
                    <h2 className="border-b pb-2 text-2xl font-semibold">Design Tokens</h2>
                    <p className="text-muted-foreground">
                        Primitive → Semantic token mapping. These tokens are the API for the entire design system.
                    </p>

                    {/* Color palette — read from CSS custom properties or Tailwind config */}
                    <div className="space-y-4">
                        <h3 className="text-lg font-medium">Color Palette</h3>
                        <div className="grid grid-cols-3 gap-4 sm:grid-cols-4 md:grid-cols-6">
                            {/* Replace with programmatic token rendering:
                  Object.entries(semanticColors).map(([name, value]) => (...))
              */}
                            {[
                                { name: "background", css: "var(--background)" },
                                { name: "foreground", css: "var(--foreground)" },
                                { name: "primary", css: "var(--primary)" },
                                { name: "secondary", css: "var(--secondary)" },
                                { name: "muted", css: "var(--muted)" },
                                { name: "accent", css: "var(--accent)" },
                                { name: "destructive", css: "var(--destructive)" },
                                { name: "border", css: "var(--border)" },
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
                    </div>

                    {/* Typography scale */}
                    <div className="space-y-4">
                        <h3 className="text-lg font-medium">Typography Scale</h3>
                        <div className="space-y-3 rounded-lg border p-6">
                            <p className="text-5xl font-extrabold">Heading 1 — 3rem / 48px</p>
                            <p className="text-4xl font-bold">Heading 2 — 2.25rem / 36px</p>
                            <p className="text-3xl font-semibold">Heading 3 — 1.875rem / 30px</p>
                            <p className="text-2xl font-semibold">Heading 4 — 1.5rem / 24px</p>
                            <p className="text-xl font-medium">Heading 5 — 1.25rem / 20px</p>
                            <p className="text-lg font-medium">Heading 6 — 1.125rem / 18px</p>
                            <p className="text-base">Body — 1rem / 16px</p>
                            <p className="text-sm text-muted-foreground">Caption — 0.875rem / 14px</p>
                        </div>
                    </div>
                </section>

                {/* ════════════════════════════════════════════════════════════════ */}
                {/* SECTION: Voice & Tone                                          */}
                {/* ════════════════════════════════════════════════════════════════ */}
                <section id="voice" className="space-y-6">
                    <h2 className="border-b pb-2 text-2xl font-semibold">Voice & Tone</h2>

                    {/* Voice definition */}
                    <div className="space-y-3">
                        <h3 className="text-lg font-medium">Brand Voice</h3>
                        <p className="text-muted-foreground">
                            Our voice is <strong>[adjective]</strong>, <strong>[adjective]</strong>,
                            and <strong>[adjective]</strong>.
                        </p>
                        {/* Replace with the project's actual voice adjectives */}
                    </div>

                    {/* Tone map */}
                    <div className="space-y-3">
                        <h3 className="text-lg font-medium">Tone Map</h3>
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm">
                                <thead>
                                    <tr className="border-b text-left">
                                        <th className="px-4 py-2 font-medium">User State</th>
                                        <th className="px-4 py-2 font-medium">Tone</th>
                                        <th className="px-4 py-2 font-medium">Example</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr className="border-b">
                                        <td className="px-4 py-2">Pleased</td>
                                        <td className="px-4 py-2">Enthusiastic</td>
                                        <td className="px-4 py-2 text-muted-foreground">
                                            "You're all set! Your changes are live."
                                        </td>
                                    </tr>
                                    <tr className="border-b">
                                        <td className="px-4 py-2">Neutral</td>
                                        <td className="px-4 py-2">Informative</td>
                                        <td className="px-4 py-2 text-muted-foreground">
                                            "3 items in your cart."
                                        </td>
                                    </tr>
                                    <tr className="border-b">
                                        <td className="px-4 py-2">Confused</td>
                                        <td className="px-4 py-2">Supportive</td>
                                        <td className="px-4 py-2 text-muted-foreground">
                                            "Let's get you back on track. Try refreshing the page."
                                        </td>
                                    </tr>
                                    <tr className="border-b">
                                        <td className="px-4 py-2">Frustrated</td>
                                        <td className="px-4 py-2">Empathetic</td>
                                        <td className="px-4 py-2 text-muted-foreground">
                                            "Something went wrong. Your draft is safe — try again."
                                        </td>
                                    </tr>
                                    <tr>
                                        <td className="px-4 py-2">First-time</td>
                                        <td className="px-4 py-2">Encouraging</td>
                                        <td className="px-4 py-2 text-muted-foreground">
                                            "Welcome! Let's set up your workspace — it only takes a minute."
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>

                    {/* Content patterns */}
                    <div className="space-y-4">
                        <h3 className="text-lg font-medium">Content Patterns</h3>
                        <div className="grid gap-4 md:grid-cols-2">
                            {/* Empty state */}
                            <div className="rounded-lg border p-6 text-center">
                                <div className="mx-auto mb-3 h-12 w-12 rounded-full bg-muted" />
                                <p className="font-medium">No projects yet</p>
                                <p className="mt-1 text-sm text-muted-foreground">
                                    The Fellowship hasn't assembled yet. Create your first quest to begin.
                                </p>
                                <Button variant="primary" size="sm" className="mt-4">
                                    Create Project
                                </Button>
                            </div>

                            {/* Error state */}
                            <Alert variant="destructive">
                                <p className="font-medium">Couldn't save your changes</p>
                                <p className="mt-1 text-sm">
                                    The file may have been modified by another fellowship member.
                                    Try refreshing and saving again.
                                </p>
                            </Alert>

                            {/* Success state */}
                            <Alert variant="success">
                                <p className="font-medium">Quest updated</p>
                                <p className="mt-1 text-sm">
                                    Your changes will appear across Middle-earth within a few minutes.
                                </p>
                            </Alert>

                            {/* Loading state */}
                            <div className="space-y-3 rounded-lg border p-6">
                                <p className="text-sm text-muted-foreground">
                                    Loading your fellowship roster...
                                </p>
                                <div className="space-y-2">
                                    <div className="h-4 w-3/4 animate-pulse rounded bg-muted" />
                                    <div className="h-4 w-1/2 animate-pulse rounded bg-muted" />
                                    <div className="h-4 w-2/3 animate-pulse rounded bg-muted" />
                                </div>
                            </div>
                        </div>
                    </div>
                </section>

                {/* ════════════════════════════════════════════════════════════════ */}
                {/* SECTION: Site Header                                           */}
                {/* ════════════════════════════════════════════════════════════════ */}
                <section id="header" className="space-y-6">
                    <h2 className="border-b pb-2 text-2xl font-semibold">Site Header</h2>
                    <p className="text-sm text-muted-foreground">
                        Rendered inline to test responsive breakpoints and navigation states.
                    </p>
                    {/* Replace with: <SiteHeader /> */}
                    <div className="rounded-lg border">
                        <header className="flex h-16 items-center justify-between border-b px-6">
                            <div className="flex items-center gap-6">
                                <span className="text-lg font-bold">Logo</span>
                                <nav className="hidden gap-4 text-sm md:flex">
                                    <a href="#" className="text-foreground hover:text-primary">Home</a>
                                    <a href="#" className="text-muted-foreground hover:text-primary">About</a>
                                    <a href="#" className="text-muted-foreground hover:text-primary">Services</a>
                                    <a href="#" className="text-muted-foreground hover:text-primary">Contact</a>
                                </nav>
                            </div>
                            <Button variant="primary" size="sm">Get Started</Button>
                        </header>
                    </div>
                </section>

                {/* ════════════════════════════════════════════════════════════════ */}
                {/* SECTION: Site Footer                                           */}
                {/* ════════════════════════════════════════════════════════════════ */}
                <section id="footer" className="space-y-6">
                    <h2 className="border-b pb-2 text-2xl font-semibold">Site Footer</h2>
                    {/* Replace with: <SiteFooter /> */}
                    <div className="rounded-lg border">
                        <footer className="grid grid-cols-2 gap-8 border-t px-6 py-10 text-sm md:grid-cols-4">
                            <div>
                                <h4 className="mb-3 font-semibold">Product</h4>
                                <ul className="space-y-2 text-muted-foreground">
                                    <li><a href="#" className="hover:text-foreground">Features</a></li>
                                    <li><a href="#" className="hover:text-foreground">Pricing</a></li>
                                    <li><a href="#" className="hover:text-foreground">Changelog</a></li>
                                </ul>
                            </div>
                            <div>
                                <h4 className="mb-3 font-semibold">Company</h4>
                                <ul className="space-y-2 text-muted-foreground">
                                    <li><a href="#" className="hover:text-foreground">About</a></li>
                                    <li><a href="#" className="hover:text-foreground">Blog</a></li>
                                    <li><a href="#" className="hover:text-foreground">Careers</a></li>
                                </ul>
                            </div>
                            <div>
                                <h4 className="mb-3 font-semibold">Legal</h4>
                                <ul className="space-y-2 text-muted-foreground">
                                    <li><a href="#" className="hover:text-foreground">Privacy</a></li>
                                    <li><a href="#" className="hover:text-foreground">Terms</a></li>
                                </ul>
                            </div>
                            <div>
                                <h4 className="mb-3 font-semibold">Connect</h4>
                                <ul className="space-y-2 text-muted-foreground">
                                    <li><a href="#" className="hover:text-foreground">Twitter</a></li>
                                    <li><a href="#" className="hover:text-foreground">GitHub</a></li>
                                </ul>
                            </div>
                        </footer>
                    </div>
                </section>

                {/* ════════════════════════════════════════════════════════════════ */}
                {/* SECTION: Typography                                            */}
                {/* ════════════════════════════════════════════════════════════════ */}
                <section id="typo" className="space-y-6">
                    <h2 className="border-b pb-2 text-2xl font-semibold">Typography</h2>
                    <div className="max-w-2xl space-y-4">
                        <h1 className="text-5xl font-extrabold tracking-tight">Heading One</h1>
                        <h2 className="text-4xl font-bold">Heading Two</h2>
                        <h3 className="text-3xl font-semibold">Heading Three</h3>
                        <h4 className="text-2xl font-semibold">Heading Four</h4>
                        <h5 className="text-xl font-medium">Heading Five</h5>
                        <h6 className="text-lg font-medium">Heading Six</h6>
                        <p>
                            Body text. The quick brown fox jumps over the lazy dog. This paragraph
                            demonstrates the default body text styling, including line height and
                            font weight at the base size.
                        </p>
                        <ul className="list-inside list-disc space-y-1 text-muted-foreground">
                            <li>Unordered list item one</li>
                            <li>Unordered list item two</li>
                            <li>Unordered list item three</li>
                        </ul>
                        <ol className="list-inside list-decimal space-y-1 text-muted-foreground">
                            <li>Ordered list item one</li>
                            <li>Ordered list item two</li>
                            <li>Ordered list item three</li>
                        </ol>
                        <blockquote className="border-l-4 border-primary/30 pl-4 italic text-muted-foreground">
                            "Not all those who wander are lost." — Bilbo Baggins
                        </blockquote>
                        <p>
                            Inline code: <code className="rounded bg-muted px-1.5 py-0.5 font-mono text-sm">npm run dev</code>
                        </p>
                    </div>
                </section>

                {/* ════════════════════════════════════════════════════════════════ */}
                {/* SECTION: Buttons                                               */}
                {/* ════════════════════════════════════════════════════════════════ */}
                <section id="buttons" className="space-y-6">
                    <h2 className="border-b pb-2 text-2xl font-semibold">Buttons</h2>
                    <p className="text-sm text-muted-foreground">
                        All variants × sizes rendered as a grid. Uses CVA base + variant pattern.
                    </p>

                    {/* Variant × Size grid */}
                    <div className="space-y-4">
                        <h3 className="text-lg font-medium">Variant × Size Matrix</h3>
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
                                    {(["primary", "secondary", "outline", "ghost", "destructive", "link"] as const).map(
                                        (variant) => (
                                            <tr key={variant} className="border-b">
                                                <td className="px-4 py-3 font-mono text-xs">{variant}</td>
                                                {(["sm", "md", "lg"] as const).map((size) => (
                                                    <td key={size} className="px-4 py-3">
                                                        <Button variant={variant} size={size}>
                                                            {variant}
                                                        </Button>
                                                    </td>
                                                ))}
                                            </tr>
                                        )
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    {/* States */}
                    <div className="space-y-3">
                        <h3 className="text-lg font-medium">States</h3>
                        <div className="flex flex-wrap gap-3">
                            <Button variant="primary">Default</Button>
                            <Button variant="primary" disabled>Disabled</Button>
                            <Button variant="primary" className="ring-2 ring-ring ring-offset-2">
                                Focus Visible
                            </Button>
                        </div>
                    </div>
                </section>

                {/* ════════════════════════════════════════════════════════════════ */}
                {/* SECTION: Badges                                                */}
                {/* ════════════════════════════════════════════════════════════════ */}
                <section id="badges" className="space-y-6">
                    <h2 className="border-b pb-2 text-2xl font-semibold">Badges</h2>
                    <div className="flex flex-wrap gap-3">
                        <Badge variant="default">Default</Badge>
                        <Badge variant="secondary">Secondary</Badge>
                        <Badge variant="success">Success</Badge>
                        <Badge variant="warning">Warning</Badge>
                        <Badge variant="destructive">Destructive</Badge>
                        <Badge variant="outline">Outline</Badge>
                    </div>
                </section>

                {/* ════════════════════════════════════════════════════════════════ */}
                {/* SECTION: Cards                                                 */}
                {/* ════════════════════════════════════════════════════════════════ */}
                <section id="cards" className="space-y-6">
                    <h2 className="border-b pb-2 text-2xl font-semibold">Cards</h2>
                    <div className="grid gap-6 md:grid-cols-3">
                        {/* Basic card */}
                        <div className="rounded-lg border bg-card p-6 text-card-foreground shadow-sm">
                            <h3 className="font-semibold">Basic Card</h3>
                            <p className="mt-2 text-sm text-muted-foreground">
                                A simple card with padding, border, and shadow.
                            </p>
                        </div>

                        {/* Card with header/footer */}
                        <div className="overflow-hidden rounded-lg border bg-card text-card-foreground shadow-sm">
                            <div className="border-b bg-muted/30 px-6 py-3">
                                <h3 className="font-semibold">With Header</h3>
                            </div>
                            <div className="p-6">
                                <p className="text-sm text-muted-foreground">
                                    Card body content with a distinct header region.
                                </p>
                            </div>
                            <div className="border-t bg-muted/30 px-6 py-3">
                                <Button variant="ghost" size="sm">Action</Button>
                            </div>
                        </div>

                        {/* Interactive card (hover lift) */}
                        <div className="cursor-pointer rounded-lg border bg-card p-6 text-card-foreground shadow-sm transition-all duration-100 ease-out hover:-translate-y-0.5 hover:shadow-lg">
                            <h3 className="font-semibold">Interactive Card</h3>
                            <p className="mt-2 text-sm text-muted-foreground">
                                Hover to see the lift effect. Uses motion token: duration-instant, ease-out.
                            </p>
                        </div>
                    </div>
                </section>

                {/* ════════════════════════════════════════════════════════════════ */}
                {/* SECTION: Form Controls                                         */}
                {/* ════════════════════════════════════════════════════════════════ */}
                <section id="forms" className="space-y-6">
                    <h2 className="border-b pb-2 text-2xl font-semibold">Form Controls</h2>
                    <div className="grid max-w-lg gap-6">
                        {/* Text input */}
                        <div className="space-y-2">
                            <label htmlFor="name" className="text-sm font-medium">Fellowship Name</label>
                            <input
                                id="name"
                                type="text"
                                placeholder="Gandalf the Grey"
                                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                            />
                        </div>

                        {/* Input with error */}
                        <div className="space-y-2">
                            <label htmlFor="email" className="text-sm font-medium">Email</label>
                            <input
                                id="email"
                                type="email"
                                placeholder="gandalf@shire.com"
                                aria-invalid="true"
                                aria-describedby="email-error"
                                className="flex h-10 w-full rounded-md border border-destructive bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-destructive focus-visible:ring-offset-2"
                            />
                            <p id="email-error" className="text-sm text-destructive">
                                This email is already registered. Try signing in instead.
                            </p>
                        </div>

                        {/* Textarea */}
                        <div className="space-y-2">
                            <label htmlFor="bio" className="text-sm font-medium">Quest Description</label>
                            <textarea
                                id="bio"
                                rows={3}
                                placeholder="Describe the perilous journey ahead..."
                                className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                            />
                        </div>

                        {/* Select */}
                        <div className="space-y-2">
                            <label htmlFor="race" className="text-sm font-medium">Race</label>
                            <select
                                id="race"
                                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                            >
                                <option value="">Select a race</option>
                                <option>Hobbit</option>
                                <option>Elf</option>
                                <option>Dwarf</option>
                                <option>Human</option>
                                <option>Wizard</option>
                            </select>
                        </div>

                        {/* Checkbox */}
                        <div className="flex items-center gap-2">
                            <input
                                id="terms"
                                type="checkbox"
                                className="h-4 w-4 rounded border-input accent-primary"
                            />
                            <label htmlFor="terms" className="text-sm">
                                I accept the Council of Elrond's terms and conditions
                            </label>
                        </div>

                        {/* Radio group */}
                        <fieldset className="space-y-2">
                            <legend className="text-sm font-medium">Preferred Weapon</legend>
                            {["Sword", "Bow", "Axe", "Staff"].map((weapon) => (
                                <div key={weapon} className="flex items-center gap-2">
                                    <input
                                        id={weapon.toLowerCase()}
                                        name="weapon"
                                        type="radio"
                                        className="h-4 w-4 border-input accent-primary"
                                    />
                                    <label htmlFor={weapon.toLowerCase()} className="text-sm">
                                        {weapon}
                                    </label>
                                </div>
                            ))}
                        </fieldset>
                    </div>
                </section>

                {/* ════════════════════════════════════════════════════════════════ */}
                {/* SECTION: Modals & Dialogs                                      */}
                {/* ════════════════════════════════════════════════════════════════ */}
                <ModalSection />

                {/* ════════════════════════════════════════════════════════════════ */}
                {/* SECTION: Alerts                                                */}
                {/* ════════════════════════════════════════════════════════════════ */}
                <section id="alerts" className="space-y-6">
                    <h2 className="border-b pb-2 text-2xl font-semibold">Alerts</h2>
                    <div className="space-y-4 max-w-2xl">
                        <Alert variant="info">
                            <p className="font-medium">The Council will convene at dawn</p>
                            <p className="mt-1 text-sm">All fellowship members should prepare their arguments.</p>
                        </Alert>
                        <Alert variant="success">
                            <p className="font-medium">Ring destroyed successfully</p>
                            <p className="mt-1 text-sm">The quest is complete. Middle-earth is saved.</p>
                        </Alert>
                        <Alert variant="warning">
                            <p className="font-medium">Approaching Mordor</p>
                            <p className="mt-1 text-sm">One does not simply walk in. Consider alternative routes.</p>
                        </Alert>
                        <Alert variant="destructive">
                            <p className="font-medium">The Balrog has been awakened</p>
                            <p className="mt-1 text-sm">Evacuate the mines immediately. Fly, you fools!</p>
                        </Alert>
                    </div>
                </section>

                {/* ════════════════════════════════════════════════════════════════ */}
                {/* SECTION: Motion Sampler                                        */}
                {/* ════════════════════════════════════════════════════════════════ */}
                <MotionSamplerSection />

                {/* ════════════════════════════════════════════════════════════════ */}
                {/* SECTION: Tier 2 Components                                     */}
                {/* ════════════════════════════════════════════════════════════════ */}
                <section id="tier2" className="space-y-6">
                    <h2 className="border-b pb-2 text-2xl font-semibold">Tier 2 Components</h2>
                    <p className="text-muted-foreground">
                        Tabs, Breadcrumbs, Accordion, Tooltip, Dropdown — replace with real imports.
                    </p>
                    {/* Import and render real components here:
              <Tabs />, <Breadcrumbs />, <Accordion />, <Tooltip />, <DropdownMenu />
          */}
                </section>

                {/* ════════════════════════════════════════════════════════════════ */}
                {/* SECTION: Tier 3 Components                                     */}
                {/* ════════════════════════════════════════════════════════════════ */}
                <section id="tier3" className="space-y-6">
                    <h2 className="border-b pb-2 text-2xl font-semibold">Tier 3 Components</h2>
                    <p className="text-muted-foreground">
                        Table, Stats Cards, Charts, Progress, Skeleton — replace with real imports.
                    </p>
                    {/* Import and render real components here:
              <DataTable />, <StatsCard />, <ProgressBar />, <Skeleton />
          */}
                </section>

                {/* ════════════════════════════════════════════════════════════════ */}
                {/* SECTION: Chaos Laboratory                                      */}
                {/* ════════════════════════════════════════════════════════════════ */}
                <section id="chaos" className="space-y-6">
                    <h2 className="border-b pb-2 text-2xl font-semibold">Chaos Laboratory</h2>
                    <p className="text-sm text-muted-foreground">
                        Stress-test the design system. Side-by-side dark/light, overflow, edge cases.
                    </p>

                    {/* Dark / Light side-by-side */}
                    <div className="grid grid-cols-2 overflow-hidden rounded-lg border">
                        <div className="bg-white p-6 text-gray-900">
                            <h4 className="font-semibold">Light Mode</h4>
                            <p className="mt-1 text-sm text-gray-500">Preview components in light theme.</p>
                            <div className="mt-3 flex gap-2">
                                <Button variant="primary" size="sm">Primary</Button>
                                <Badge variant="success">Online</Badge>
                            </div>
                        </div>
                        <div className="bg-gray-950 p-6 text-gray-50">
                            <h4 className="font-semibold">Dark Mode</h4>
                            <p className="mt-1 text-sm text-gray-400">Preview components in dark theme.</p>
                            <div className="mt-3 flex gap-2">
                                <Button variant="primary" size="sm">Primary</Button>
                                <Badge variant="success">Online</Badge>
                            </div>
                        </div>
                    </div>
                </section>
            </main>
        </div>
    );
}

// ── Sub-components (extracted for readability) ──────────────────────────────

function ModalSection() {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <section id="modals" className="space-y-6">
            <h2 className="border-b pb-2 text-2xl font-semibold">Modals & Dialogs</h2>

            <Button variant="outline" onClick={() => setIsOpen(true)}>
                Open Modal
            </Button>

            {isOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center">
                    {/* Overlay */}
                    <div
                        className="absolute inset-0 bg-black/50 motion-safe:animate-[fade-in_200ms_ease-out]"
                        onClick={() => setIsOpen(false)}
                    />
                    {/* Modal content */}
                    <div className="relative z-10 w-full max-w-md rounded-lg border bg-background p-6 shadow-xl motion-safe:animate-[modal-in_300ms_ease-out]">
                        <h3 className="text-lg font-semibold">Confirm Action</h3>
                        <p className="mt-2 text-sm text-muted-foreground">
                            Destroy the One Ring? This action cannot be undone, and Sauron will
                            be vanquished permanently.
                        </p>
                        <div className="mt-6 flex justify-end gap-3">
                            <Button variant="outline" size="sm" onClick={() => setIsOpen(false)}>
                                Cancel
                            </Button>
                            <Button variant="destructive" size="sm" onClick={() => setIsOpen(false)}>
                                Destroy Ring
                            </Button>
                        </div>
                    </div>
                </div>
            )}
        </section>
    );
}

function MotionSamplerSection() {
    const [showSlideIn, setShowSlideIn] = useState(false);
    const [accordionOpen, setAccordionOpen] = useState(false);
    const [showSkeleton, setShowSkeleton] = useState(true);

    return (
        <section id="motion" className="space-y-6">
            <h2 className="border-b pb-2 text-2xl font-semibold">Motion Sampler</h2>
            <p className="text-sm text-muted-foreground">
                Interactive demos of the defined motion patterns. All animations respect{" "}
                <code className="rounded bg-muted px-1 font-mono text-xs">
                    prefers-reduced-motion
                </code>.
            </p>

            <div className="grid gap-6 md:grid-cols-2">
                {/* Hover lift */}
                <div className="space-y-3">
                    <h3 className="text-sm font-medium">Hover Lift</h3>
                    <div className="flex gap-4">
                        {["Rivendell", "Gondor", "Rohan"].map((realm) => (
                            <div
                                key={realm}
                                className="cursor-pointer rounded-lg border bg-card p-4 text-sm shadow-sm transition-all duration-100 ease-out hover:-translate-y-0.5 hover:shadow-lg"
                            >
                                {realm}
                            </div>
                        ))}
                    </div>
                    <p className="font-mono text-xs text-muted-foreground">
                        duration-instant · ease-out · translateY(-2px)
                    </p>
                </div>

                {/* Slide in */}
                <div className="space-y-3">
                    <h3 className="text-sm font-medium">Slide In</h3>
                    <Button variant="outline" size="sm" onClick={() => setShowSlideIn(!showSlideIn)}>
                        {showSlideIn ? "Reset" : "Trigger"}
                    </Button>
                    {showSlideIn && (
                        <ul className="space-y-2">
                            {["Frodo", "Sam", "Aragorn", "Legolas"].map((name, i) => (
                                <li
                                    key={name}
                                    className="rounded border bg-card p-2 text-sm motion-safe:animate-[slide-in-up_300ms_ease-out_both]"
                                    style={{ animationDelay: `${i * 50}ms` }}
                                >
                                    {name}
                                </li>
                            ))}
                        </ul>
                    )}
                    <p className="font-mono text-xs text-muted-foreground">
                        duration-normal · ease-out · stagger: 50ms
                    </p>
                </div>

                {/* Expand / Collapse */}
                <div className="space-y-3">
                    <h3 className="text-sm font-medium">Expand / Collapse</h3>
                    <button
                        onClick={() => setAccordionOpen(!accordionOpen)}
                        className="flex w-full items-center justify-between rounded-lg border bg-card p-3 text-sm font-medium"
                    >
                        What is the One Ring?
                        <span className={cn(
                            "transition-transform duration-200",
                            accordionOpen ? "rotate-180" : ""
                        )}>
                            ▼
                        </span>
                    </button>
                    <div
                        className="grid transition-[grid-template-rows] duration-300 ease-in-out"
                        style={{ gridTemplateRows: accordionOpen ? "1fr" : "0fr" }}
                    >
                        <div className="overflow-hidden">
                            <p className="rounded-b-lg border border-t-0 p-3 text-sm text-muted-foreground">
                                The One Ring was forged by the Dark Lord Sauron in the fires
                                of Mount Doom. It is the master of all the Rings of Power.
                            </p>
                        </div>
                    </div>
                </div>

                {/* Skeleton → Content */}
                <div className="space-y-3">
                    <h3 className="text-sm font-medium">Skeleton → Content</h3>
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setShowSkeleton(!showSkeleton)}
                    >
                        {showSkeleton ? "Show Content" : "Show Skeleton"}
                    </Button>
                    <div className="space-y-2 rounded-lg border p-4">
                        {showSkeleton ? (
                            <>
                                <div className="h-4 w-3/4 animate-pulse rounded bg-muted" />
                                <div className="h-4 w-1/2 animate-pulse rounded bg-muted" />
                                <div className="h-4 w-2/3 animate-pulse rounded bg-muted" />
                            </>
                        ) : (
                            <>
                                <p className="text-sm font-medium">Gandalf the Grey</p>
                                <p className="text-sm text-muted-foreground">Wizard · Istari Order</p>
                                <p className="text-sm text-muted-foreground">Last seen: Fangorn Forest</p>
                            </>
                        )}
                    </div>
                </div>
            </div>
        </section>
    );
}
