# Voice & Tone Reference

Content design guidance for the Kitchen Sink design system. Every design system needs content patterns — a sink without voice guidance is only half a design system.

---

## Voice Definition

Voice is the brand's consistent personality. It never changes across contexts.

### Template

Define voice with 3–5 adjectives and a brief explanation for each:

```markdown
## Brand Voice

Our voice is **[adjective]**, **[adjective]**, and **[adjective]**.

- **[Adjective 1]** — [What this means in practice]
- **[Adjective 2]** — [What this means in practice]
- **[Adjective 3]** — [What this means in practice]
```

### Example: Professional SaaS

```markdown
## Brand Voice

Our voice is **confident**, **approachable**, and **precise**.

- **Confident** — We state things directly. No hedging with "might" or "perhaps."
- **Approachable** — We explain complex things simply. No jargon without context.
- **Precise** — We say exactly what we mean. No filler words or vague instructions.
```

### Example: Consumer Health App

```markdown
## Brand Voice

Our voice is **warm**, **empowering**, and **honest**.

- **Warm** — We talk like a knowledgeable friend, not a medical textbook.
- **Empowering** — We frame actions as choices, not commands. "You can" over "You must."
- **Honest** — We never oversimplify health information for comfort.
```

### Deriving Voice from Existing Guides

If the project has a `GEMINI.md`, brand guide, or agent config with personality descriptors, extract them directly. Look for:
- Explicit adjectives ("our brand is X, Y, Z")
- Implicit tone in example copy
- Do's and Don'ts that reveal personality
- CMS content patterns (if TinaCMS collections exist, read the existing authored content for voice clues)

---

## Tone Map

Tone adapts to the user's emotional state and context. Voice stays the same; tone shifts.

### Template

| User State | Tone | Guidelines | Example |
|---|---|---|---|
| Pleased / celebrating | Enthusiastic | Short, affirming. Acknowledge the win. | — |
| Neutral / browsing | Informative | Clear, concise. State facts. | — |
| Confused / stuck | Supportive | Offer guidance. Break into steps. | — |
| Frustrated / error | Empathetic | Acknowledge the problem. No blame. | — |
| First-time / onboarding | Encouraging | Welcome warmly. Set expectations. | — |

### Filled Example

| User State | Tone | Guidelines | Example |
|---|---|---|---|
| Pleased | Enthusiastic | Keep it brief. No over-the-top celebration. | "You're all set! Your changes are live." |
| Neutral | Informative | State what they see. No unnecessary words. | "3 items in your cart." |
| Confused | Supportive | Lead with what to do, not what went wrong. | "Let's get you back on track. Try refreshing the page." |
| Frustrated | Empathetic | Acknowledge first, then offer the fix. | "Something went wrong saving your work. Your draft is safe — try again in a moment." |
| First-time | Encouraging | Make the first step obvious and low-stakes. | "Welcome! Let's set up your first project — it only takes a minute." |

---

## Content Patterns by UI State

### Empty States

Empty states are onboarding moments. They should tell the user:
1. What belongs here
2. How to populate it
3. (Optional) Why it matters

| ✅ Do | ❌ Don't |
|---|---|
| "No projects yet. Create your first one to get started." | "No data." |
| "Your inbox is empty — nice work! New messages will appear here." | "Empty." |
| "No results for 'flux capacitor.' Try a different search term." | "0 results." |

### Error Messages

Every error message should answer three questions:
1. **What happened?** — Describe the problem clearly
2. **Why?** — Brief context (if useful)
3. **How to fix it** — Actionable next step

| ✅ Do | ❌ Don't |
|---|---|
| "We couldn't save your changes. The file may have been modified. Try refreshing and saving again." | "Error: 409" |
| "This email address is already registered. Try signing in instead." | "Invalid input." |
| "Upload failed — the file is larger than 10 MB. Try compressing it first." | "Error uploading file." |

### Success Confirmations

Keep them concise. Confirm what happened and hint at the next step:

| ✅ Do | ❌ Don't |
|---|---|
| "Profile updated. Changes appear within a few minutes." | "Success!" |
| "Payment received. You'll get a confirmation email shortly." | "Transaction complete." |
| "Saved." (for frequent micro-actions) | "Your data has been successfully saved to the database." |

### Loading States

Set expectations. Tell the user what's loading and (if possible) how long:

| ✅ Do | ❌ Don't |
|---|---|
| "Loading your dashboard..." + skeleton | Spinner with no context |
| "Generating report — this usually takes 10–15 seconds." | Empty white space |
| Skeleton loaders that match the shape of incoming content | Generic "Please wait" |

### Destructive Actions

Confirm with specifics. The user should understand exactly what they're losing:

| ✅ Do | ❌ Don't |
|---|---|
| "Delete 'Project Alpha'? This removes all 12 pages and cannot be undone." | "Are you sure?" |
| "Remove Gandalf from the team? They'll lose access immediately." | "Confirm removal?" |
| "Cancel subscription? You'll keep access until Feb 28." | "Cancel?" |

### Form Labels & Placeholder Text

- Labels should be nouns or noun phrases: "Email address", not "Enter your email"
- Placeholder text shows format or example, not instructions: `gandalf@shire.com`, not "Type email here"
- Keep labels above inputs (not inside) for accessibility
- Error text goes below the field, in the error color, with clear guidance

---

## Franchise Placeholders

Per project conventions, pick a pop-culture franchise as the source for all placeholder content. This creates consistency across form examples, sample data, empty states, and documentation.

### How to Choose

- If the project already specifies a franchise (check `GEMINI.md`), use it
- If not, suggest one that matches the project's personality:
  - **Professional/enterprise** — Star Trek, The West Wing
  - **Playful/consumer** — Lord of the Rings, Star Wars, Marvel
  - **Technical/dev-focused** — Hitchhiker's Guide, Firefly
  - **Health/wellness** — Avatar, Studio Ghibli

### Application

Once chosen, use franchise nouns consistently:

| UI Element | Generic ❌ | Franchise ✅ (LOTR) |
|---|---|---|
| Text input placeholder | "John Doe" | "Frodo Baggins" |
| Email placeholder | "user@example.com" | "frodo@shire.com" |
| Table sample row | "Acme Corp \| Manager" | "Rivendell \| Council Member" |
| Empty state | "No users yet." | "The Fellowship hasn't assembled yet." |
| Error with name | "User not found" | "Hobbit not found in the Shire" |

Document the chosen franchise in the sink page header and in `GEMINI.md`.

---

## Writing Checklist for Components

When building or reviewing a component, check its content patterns:

- [ ] **Labels** — Are they nouns/noun phrases? Consistent capitalization?
- [ ] **Placeholders** — Do they show format, not instructions? Use franchise names?
- [ ] **Error messages** — Do they answer what/why/fix?
- [ ] **Empty states** — Do they guide the user to populate?
- [ ] **Success messages** — Concise and affirming?
- [ ] **Loading text** — Does it set expectations?
- [ ] **Destructive confirmations** — Do they name what's being destroyed?
- [ ] **Tooltips** — Are they helpful, not just restating the label?
- [ ] **Aria labels** — Do screen readers get useful descriptions?

---

## CMS-Authored Content

When the project uses a CMS (TinaCMS, Contentful, Sanity, etc.), the voice & tone guidance splits into two domains:

### UI Chrome (developer-authored)
- Button labels, form labels, error messages, tooltips, empty states
- Controlled directly by the component library
- Covered by the patterns above

### CMS Content (author-authored)
- Marketing copy, blog posts, hero text, about pages
- Authored in the CMS by content creators
- Voice & tone guidance should be documented in the CMS or a shared content style guide
- The sink page can show example CMS-sourced content alongside UI chrome to verify they feel cohesive
