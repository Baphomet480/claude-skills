# Design Sources Reference

## Fetch Method Key

- **WebFetch** = Use WebFetch directly (fastest)
- **Playwright** = Use `scripts/fetch_page.py` (Cloudflare-protected or SPA)
- **GitHub raw** = Fetch SVGs directly via raw GitHub URLs with WebFetch

## CSS Components & UI Elements

| Source | URL | Fetch Method | Best For | Search Tips |
|--------|-----|--------------|----------|-------------|
| **CodePen** | `codepen.io` | Playwright (`--codepen-code`) | Interactive demos, animations, full components | `site:codepen.io {query}` to discover pens, then fetch with Playwright. |
| **UIVerse** | `uiverse.io` | Playwright | Buttons, cards, loaders, inputs, toggles | `site:uiverse.io {component type}` to discover, then fetch component pages. |
| **CSS-Tricks** | `css-tricks.com` | WebFetch | Tutorials, techniques, CSS almanac | `site:css-tricks.com {technique}` — articles have full inline code. |
| **CSS.GG** | `css.gg` | Playwright | Pure CSS icons (no SVG needed) | `site:css.gg {icon name}` to discover icons. |
| **Animista** | `animista.net` | Playwright | CSS animations and transitions | `site:animista.net {animation type}` — generator, link user to tweak. |
| **dev.to** | `dev.to` | WebFetch | CSS tutorials with inline code | `site:dev.to {CSS component} tutorial` |
| **Smashing Magazine** | `smashingmagazine.com` | WebFetch | In-depth CSS/SVG articles | `site:smashingmagazine.com {topic}` |

## SVG Icon Libraries

All major icon libraries have fetchable GitHub raw URLs. Use WebSearch to discover icon names, then fetch the SVG directly.

| Library | Icon Count | GitHub Raw URL Pattern |
|---------|------------|----------------------|
| **Lucide** | 1500+ | `https://raw.githubusercontent.com/lucide-icons/lucide/main/icons/{name}.svg` |
| **Heroicons** | 450+ | `https://raw.githubusercontent.com/tailwindlabs/heroicons/master/optimized/24/outline/{name}.svg` (also `solid/`, `20/solid/`, `20/outline/`) |
| **Tabler** | 5900+ | `https://raw.githubusercontent.com/tabler/tabler-icons/main/icons/outline/{name}.svg` (also `filled/`) |
| **Feather** | 280+ | `https://raw.githubusercontent.com/feathericons/feather/main/icons/{name}.svg` |
| **Simple Icons** | 3000+ | `https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/{name}.svg` |

**Icon name discovery:** Use WebSearch with `site:lucide.dev {concept}` or `site:tabler.io/icons {concept}` to find icon names, then fetch via the raw URL.

**Other icon sources:**

| Source | URL | Best For |
|--------|-----|----------|
| **Iconoir** | `iconoir.com` | Modern open-source icons (1600+) |
| **Phosphor** | `phosphoricons.com` | Flexible icon family (1000+, 6 weights) |
| **Material Symbols** | `fonts.google.com/icons` | Google's icon set (2500+) |
| **Flaticon** | `flaticon.com` | Diverse styles (attribution may be required) |
| **SVGRepo** | `svgrepo.com` | 500k+ SVGs |

## SVG Illustrations & Graphics

| Source | URL | Best For |
|--------|-----|----------|
| **UnDraw** | `undraw.co` | Open-source SVG illustrations, color-customizable |
| **Humaaans** | `humaaans.com` | Mix-and-match people illustrations |
| **Open Peeps** | `openpeeps.com` | Hand-drawn people illustrations |
| **Blush** | `blush.design` | Customizable illustration collections |

## CSS & SVG Generators

Interactive tools — link the user to them for tweaking. Can also use Playwright to fetch if needed.

| Source | URL | Generates |
|--------|-----|-----------|
| **Get Waves** | `getwaves.io` | SVG wave dividers |
| **Blobmaker** | `blobmaker.app` | Organic SVG blob shapes |
| **Haikei** | `haikei.app` | SVG backgrounds (waves, blobs, gradients, stacks) |
| **CSS Gradient** | `cssgradient.io` | CSS gradient code |
| **Neumorphism.io** | `neumorphism.io` | Neumorphic CSS box-shadows |
| **Glassmorphism** | `ui.glass/generator` | Glassmorphism CSS effects |
| **Fancy Border Radius** | `9elements.github.io/fancy-border-radius` | Organic CSS border-radius shapes |
| **CSS Pattern** | `css-pattern.com` | Pure CSS background patterns |
| **Clippy** | `bennettfeely.com/clippy` | CSS clip-path polygons |
| **Keyframes** | `keyframes.app` | CSS animations, shadows, colors |

## Design Inspiration (Visual, Not Code)

| Source | URL | Best For |
|--------|-----|----------|
| **Dribbble** | `dribbble.com` | UI/UX design shots |
| **Mobbin** | `mobbin.com` | Real app UI patterns and flows |
| **Awwwards** | `awwwards.com` | Award-winning web design |
| **Collect UI** | `collectui.com` | Daily UI inspiration by category |

## Search Strategy by Request Type

| User Wants | Primary Sources | Extraction Method |
|------------|-----------------|-------------------|
| CSS component (button, card, loader) | CodePen, UIVerse | WebSearch → Playwright to extract code |
| SVG icon | Lucide, Heroicons, Tabler, Feather | WebSearch to find name → WebFetch raw GitHub URL |
| CSS animation/effect | CodePen, CSS-Tricks | WebSearch → Playwright (CodePen) or WebFetch (CSS-Tricks) |
| SVG illustration | UnDraw, Humaaans, Blush | Link user to generators |
| SVG shape/background | Haikei, Get Waves, Blobmaker | Link user to generator tools |
| CSS pattern/texture | CSS Pattern | Link user to generator |
| Design inspiration | Dribbble, Awwwards, Collect UI | WebSearch for curated links |
| Brand logo SVG | Simple Icons | `site:simpleicons.org {brand}` → WebFetch raw GitHub URL |
