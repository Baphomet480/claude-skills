#!/usr/bin/env bash

# Scaffold the Business Brain Pattern directory structure and templates.

BRAIN_DIR="brain"

if [ -d "$BRAIN_DIR" ]; then
  echo "Brain directory '$BRAIN_DIR' already exists. Aborting to prevent overwriting."
  exit 1
fi

mkdir -p "$BRAIN_DIR"

cat << 'EOF' > "$BRAIN_DIR/brand-voice.md"
# Brand Voice

**Register**: Second person ("you"), active voice, present tense where possible.

**Sentence length**: Short to medium. Avoid sentences over 25 words.

**Energy**: Confident but not hyped. Direct, not blunt.

**Never use**: "leverage," "seamlessly," "empower," "game-changing," "innovative solution"

**Sample — On brand**:
"Most tools dump data at you. This one learns your style and stays out of the way."

**Sample — Off brand**:
"Our innovative solution seamlessly empowers your team to leverage cutting-edge capabilities."
EOF

cat << 'EOF' > "$BRAIN_DIR/audience-profiles.md"
# Audience Profiles

## Segment 1: The Technical Lead
**Care about**: Architecture, scalability, maintenance burden, vendor lock-in.
**Skeptical of**: Marketing fluff, "magic" AI claims, hidden pricing.
**Resonates with**: Direct technical explanations, open-source comparisons, API-first design.

## Segment 2: The Product Manager
**Care about**: Time to market, user adoption, feature parity.
**Skeptical of**: Long implementation timelines, complex training requirements.
**Resonates with**: Workflow improvements, integration speed, ROI.
EOF

cat << 'EOF' > "$BRAIN_DIR/positioning.md"
# Product Positioning

**What we do**: We build developer tools that stay out of the way.
**Who it's for**: Small to mid-sized engineering teams who want to ship faster without adopting complex enterprise frameworks.
**Why us**: Our tools are single-binary, require zero configuration, and integrate with existing CI/CD pipelines in under 5 minutes.

**What we ARE NOT**: 
- We are not a full-stack platform.
- We do not replace your database or hosting provider.
- We do not promise "no-code" magic to non-technical users.
EOF

cat << 'EOF' > "$BRAIN_DIR/content-rules.md"
# Content and Format Rules

**Headers**: Use sentence case for all headers (e.g., "How to get started", not "How To Get Started").
**Lists**: Prefer bulleted lists over long paragraphs when explaining 3 or more items.
**Commas**: Always use the Oxford comma.
**Length**: Keep blog posts under 1,000 words. Keep emails under 150 words.
**Calls to Action (CTAs)**: End every customer-facing communication with exactly one clear CTA. Do not use generic "Click here". Use descriptive actions like "Read the docs" or "Start your free trial".
EOF

echo "✅ Business Brain initialized in ./$BRAIN_DIR/"
echo "Update the templates to match your brand's specific context."
