"use client";

// -- Kitchen Sink -- Starter Template (React / Next.js) ----------------------
//
// A fully working sink page skeleton. Every rendered element is a real component
// defined in this file. Replace these with imports from your component library
// as you build out each component.
//
// Production guard: returns null in production.
// Franchise placeholder: Star Wars (replace with your project's franchise)

import { useState } from "react";
import { cva, type VariantProps } from "class-variance-authority";

// -- Utility ----------------------------------------------------------------

function cn(...classes: (string | false | undefined | null)[]) {
  return classes.filter(Boolean).join(" ");
}

// -- Button (inline -- replace with your real component) --------------------

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        primary: "bg-primary text-primary-foreground hover:bg-primary/90",
        secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        outline: "border border-input bg-transparent hover:bg-accent hover:text-accent-foreground",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
      },
      size: {
        sm: "h-8 px-3 text-xs",
        md: "h-10 px-4 text-sm",
        lg: "h-12 px-6 text-base",
      },
    },
    defaultVariants: { variant: "primary", size: "md" },
  }
);

interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

function Button({ className, variant, size, ...props }: ButtonProps) {
  return (
    <button className={cn(buttonVariants({ variant, size }), className ?? "")} {...props} />
  );
}

// -- Badge (inline -- replace with your real component) ---------------------

function Badge({
  children,
  variant = "default",
}: {
  children: React.ReactNode;
  variant?: "default" | "secondary" | "destructive" | "outline";
}) {
  const base = "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors";
  const variants: Record<string, string> = {
    default: "bg-primary text-primary-foreground",
    secondary: "bg-secondary text-secondary-foreground",
    destructive: "bg-destructive text-destructive-foreground",
    outline: "border border-input text-foreground",
  };
  return <span className={cn(base, variants[variant])}>{children}</span>;
}

// -- Card (inline -- replace with your real component) ----------------------

function Card({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={cn("rounded-lg border bg-card text-card-foreground shadow-sm", className ?? "")}>
      {children}
    </div>
  );
}

// -- Alert (inline -- replace with your real component) ---------------------

function Alert({
  children,
  variant = "info",
}: {
  children: React.ReactNode;
  variant?: "info" | "success" | "warning" | "error";
}) {
  const styles: Record<string, string> = {
    info: "border-blue-200 bg-blue-50 text-blue-900 dark:border-blue-800 dark:bg-blue-950 dark:text-blue-100",
    success: "border-green-200 bg-green-50 text-green-900 dark:border-green-800 dark:bg-green-950 dark:text-green-100",
    warning: "border-yellow-200 bg-yellow-50 text-yellow-900 dark:border-yellow-800 dark:bg-yellow-950 dark:text-yellow-100",
    error: "border-red-200 bg-red-50 text-red-900 dark:border-red-800 dark:bg-red-950 dark:text-red-100",
  };
  return (
    <div role="alert" className={cn("rounded-lg border p-4 text-sm", styles[variant])}>
      {children}
    </div>
  );
}

// -- Section Config ---------------------------------------------------------

const SECTIONS = [
  { id: "tokens", label: "Design Tokens" },
  { id: "voice", label: "Voice & Tone" },
  { id: "typo", label: "Typography" },
  { id: "buttons", label: "Buttons" },
  { id: "badges", label: "Badges" },
  { id: "cards", label: "Cards" },
  { id: "forms", label: "Form Controls" },
  { id: "modals", label: "Modals & Dialogs" },
  { id: "alerts", label: "Alerts" },
  { id: "motion", label: "Motion Sampler" },
  { id: "chaos", label: "Chaos Laboratory" },
] as const;

// -- Main Page --------------------------------------------------------------

export default function KitchenSinkPage() {
  if (process.env.NEXT_PUBLIC_VERCEL_ENV === "production") return null;

  return (
    <div className="flex min-h-screen bg-background text-foreground">
      {/* Sidebar Navigation */}
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

      {/* Main Content */}
      <main className="flex-1 space-y-16 p-6 lg:p-10">
        <header>
          <h1 className="text-4xl font-bold tracking-tight">Kitchen Sink</h1>
          <p className="mt-2 text-lg text-muted-foreground">
            Living source of truth for the design system.
          </p>
          <p className="mt-1 text-sm text-muted-foreground">
            Franchise: <strong>Star Wars</strong>
          </p>
        </header>

        {/* Design Tokens */}
        <section id="tokens" className="space-y-6">
          <h2 className="border-b pb-2 text-2xl font-semibold">Design Tokens</h2>
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
        </section>

        {/* Typography */}
        <section id="typo" className="space-y-6">
          <h2 className="border-b pb-2 text-2xl font-semibold">Typography</h2>
          <div className="space-y-4">
            <h1 className="text-4xl font-bold">H1 -- A New Hope</h1>
            <h2 className="text-3xl font-semibold">H2 -- The Empire Strikes Back</h2>
            <h3 className="text-2xl font-semibold">H3 -- Return of the Jedi</h3>
            <h4 className="text-xl font-medium">H4 -- The Phantom Menace</h4>
            <h5 className="text-lg font-medium">H5 -- Attack of the Clones</h5>
            <h6 className="text-base font-medium">H6 -- Revenge of the Sith</h6>
            <p className="text-base">Body text -- A long time ago in a galaxy far, far away...</p>
            <p className="text-sm text-muted-foreground">Caption text -- Directed by George Lucas</p>
            <ul className="list-disc pl-6 space-y-1">
              <li>Luke Skywalker</li>
              <li>Princess Leia</li>
              <li>Han Solo</li>
            </ul>
            <blockquote className="border-l-4 border-muted pl-4 italic text-muted-foreground">
              &ldquo;Do. Or do not. There is no try.&rdquo; -- Yoda
            </blockquote>
            <p>Inline <code className="rounded bg-muted px-1.5 py-0.5 font-mono text-sm">code</code> example</p>
          </div>
        </section>

        {/* Buttons */}
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
                {(["primary", "secondary", "outline", "ghost", "destructive"] as const).map(
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
          <div className="flex gap-4">
            <Button disabled>Disabled</Button>
          </div>
        </section>

        {/* Badges */}
        <section id="badges" className="space-y-6">
          <h2 className="border-b pb-2 text-2xl font-semibold">Badges</h2>
          <div className="flex flex-wrap gap-3">
            <Badge>Jedi</Badge>
            <Badge variant="secondary">Padawan</Badge>
            <Badge variant="destructive">Sith</Badge>
            <Badge variant="outline">Smuggler</Badge>
          </div>
        </section>

        {/* Cards */}
        <section id="cards" className="space-y-6">
          <h2 className="border-b pb-2 text-2xl font-semibold">Cards</h2>
          <div className="grid gap-6 md:grid-cols-3">
            <Card>
              <div className="p-6">
                <h3 className="text-lg font-semibold">Tatooine</h3>
                <p className="mt-2 text-sm text-muted-foreground">
                  A harsh desert world orbiting twin suns in the galaxy&apos;s Outer Rim.
                </p>
              </div>
            </Card>
            <Card className="transition-transform motion-safe:hover:-translate-y-1 motion-safe:hover:shadow-lg">
              <div className="p-6">
                <h3 className="text-lg font-semibold">Hoth</h3>
                <p className="mt-2 text-sm text-muted-foreground">
                  An ice planet serving as the secret base for the Rebel Alliance.
                </p>
                <Button variant="outline" size="sm" className="mt-4">
                  Explore
                </Button>
              </div>
            </Card>
            <Card>
              <div className="border-b p-4">
                <h3 className="font-semibold">Endor</h3>
              </div>
              <div className="p-4 text-sm text-muted-foreground">
                Forest moon, home to the Ewoks.
              </div>
              <div className="border-t p-4">
                <Button variant="ghost" size="sm">Details</Button>
              </div>
            </Card>
          </div>
        </section>

        {/* Form Controls */}
        <section id="forms" className="space-y-6">
          <h2 className="border-b pb-2 text-2xl font-semibold">Form Controls</h2>
          <div className="max-w-md space-y-4">
            <div>
              <label className="mb-1.5 block text-sm font-medium">Callsign</label>
              <input
                type="text"
                placeholder="Red Five"
                className="w-full rounded-md border bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
              />
            </div>
            <div>
              <label className="mb-1.5 block text-sm font-medium">Mission Briefing</label>
              <textarea
                rows={3}
                placeholder="Describe the mission objectives..."
                className="w-full rounded-md border bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
              />
            </div>
            <div>
              <label className="mb-1.5 block text-sm font-medium">Allegiance</label>
              <select className="w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring">
                <option>Rebel Alliance</option>
                <option>Galactic Empire</option>
                <option>Bounty Hunters Guild</option>
              </select>
            </div>
            <div className="flex items-center gap-2">
              <input type="checkbox" id="force" className="h-4 w-4 rounded border" />
              <label htmlFor="force" className="text-sm">Force-sensitive</label>
            </div>
            <div className="space-y-2">
              <label className="block text-sm font-medium">Rank</label>
              <div className="flex items-center gap-2">
                <input type="radio" name="rank" id="commander" className="h-4 w-4" />
                <label htmlFor="commander" className="text-sm">Commander</label>
              </div>
              <div className="flex items-center gap-2">
                <input type="radio" name="rank" id="captain" className="h-4 w-4" />
                <label htmlFor="captain" className="text-sm">Captain</label>
              </div>
            </div>
            <div>
              <label className="mb-1.5 block text-sm font-medium">Error state</label>
              <input
                type="text"
                defaultValue="INVALID_COORDINATES"
                className="w-full rounded-md border border-destructive bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-destructive"
              />
              <p className="mt-1 text-xs text-destructive">
                Coordinates must be in standard galactic format. Check your nav computer.
              </p>
            </div>
          </div>
        </section>

        {/* Modals */}
        <ModalSection />

        {/* Alerts */}
        <section id="alerts" className="space-y-6">
          <h2 className="border-b pb-2 text-2xl font-semibold">Alerts</h2>
          <div className="space-y-3">
            <Alert variant="info">Scanning for nearby Imperial vessels...</Alert>
            <Alert variant="success">Hyperspace jump completed. Welcome to the Dagobah system.</Alert>
            <Alert variant="warning">Shield generator is at 30%. Seek repairs before your next engagement.</Alert>
            <Alert variant="error">Hyperdrive malfunction. Unable to make the jump to lightspeed.</Alert>
          </div>
        </section>

        {/* Motion Sampler */}
        <section id="motion" className="space-y-6">
          <h2 className="border-b pb-2 text-2xl font-semibold">Motion Sampler</h2>
          <div className="grid gap-6 md:grid-cols-3">
            <div className="space-y-2">
              <p className="text-sm font-medium">Hover Lift</p>
              <div className="flex h-24 items-center justify-center rounded-lg border bg-muted/30 transition-transform duration-100 ease-out motion-safe:hover:-translate-y-1 motion-safe:hover:shadow-lg">
                Hover me
              </div>
              <p className="font-mono text-xs text-muted-foreground">duration-100 ease-out</p>
            </div>
            <div className="space-y-2">
              <p className="text-sm font-medium">Fade In</p>
              <div className="flex h-24 items-center justify-center rounded-lg border bg-muted/30 motion-safe:animate-[fade-in_300ms_ease-out]">
                I faded in
              </div>
              <p className="font-mono text-xs text-muted-foreground">300ms ease-out</p>
            </div>
            <div className="space-y-2">
              <p className="text-sm font-medium">Scale</p>
              <div className="flex h-24 items-center justify-center rounded-lg border bg-muted/30 transition-transform duration-200 motion-safe:hover:scale-105">
                Hover to scale
              </div>
              <p className="font-mono text-xs text-muted-foreground">duration-200 scale-105</p>
            </div>
          </div>
        </section>

        {/* Chaos Laboratory */}
        <section id="chaos" className="space-y-6">
          <h2 className="border-b pb-2 text-2xl font-semibold">Chaos Laboratory</h2>

          {/* Theme Test */}
          <div>
            <h3 className="mb-3 text-lg font-medium">Theme Test</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="rounded-lg border bg-white p-4 text-black dark:bg-white dark:text-black">
                <p className="text-sm font-medium">Light</p>
                <Button variant="primary" size="sm" className="mt-2">Primary</Button>
              </div>
              <div className="rounded-lg border bg-zinc-950 p-4 text-white dark:bg-zinc-950 dark:text-white">
                <p className="text-sm font-medium">Dark</p>
                <Button variant="primary" size="sm" className="mt-2">Primary</Button>
              </div>
            </div>
          </div>

          {/* State Matrix */}
          <div>
            <h3 className="mb-3 text-lg font-medium">State Matrix</h3>
            <div className="flex flex-wrap gap-3">
              <Button variant="primary">Default</Button>
              <Button variant="primary" disabled>Disabled</Button>
              <Button variant="primary" className="ring-2 ring-ring ring-offset-2">Focus</Button>
            </div>
          </div>

          {/* Responsive Stubs */}
          <div>
            <h3 className="mb-3 text-lg font-medium">Responsive Stubs</h3>
            <div className="space-y-4">
              <div>
                <p className="mb-1 text-xs font-medium text-muted-foreground">320px -- Mobile</p>
                <iframe
                  src="/sink"
                  title="Mobile viewport"
                  className="h-64 w-[320px] rounded border"
                  loading="lazy"
                />
              </div>
              <div>
                <p className="mb-1 text-xs font-medium text-muted-foreground">768px -- Tablet</p>
                <iframe
                  src="/sink"
                  title="Tablet viewport"
                  className="h-64 w-[768px] max-w-full rounded border"
                  loading="lazy"
                />
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

// -- Modal Section ----------------------------------------------------------

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
          <div
            className="absolute inset-0 bg-black/50 motion-safe:animate-[fade-in_200ms_ease-out]"
            onClick={() => setIsOpen(false)}
            aria-hidden="true"
          />
          <div
            role="dialog"
            aria-modal="true"
            className="relative z-10 w-full max-w-md rounded-lg border bg-background p-6 shadow-xl motion-safe:animate-[fade-in_200ms_ease-out]"
          >
            <h3 className="text-lg font-semibold">Delete Rebel Base Location?</h3>
            <p className="mt-2 text-sm text-muted-foreground">
              This will permanently erase the coordinates for Echo Base. This action cannot be undone.
            </p>
            <div className="mt-6 flex justify-end gap-3">
              <Button variant="outline" size="sm" onClick={() => setIsOpen(false)}>
                Cancel
              </Button>
              <Button variant="destructive" size="sm" onClick={() => setIsOpen(false)}>
                Delete Base
              </Button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
