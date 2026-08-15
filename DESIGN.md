---
name: AthletIQ
description: Local NBA stats-desk lookup for a disclosed home-win estimate.
colors:
  navy: "#17408b"
  navy-ink: "#0b1c3a"
  red: "#c8102e"
  paper: "#e8eaee"
  white: "#ffffff"
  rule: "#d5dae2"
  ink: "#12161c"
  muted: "#3d4a5c"
  focus: "#1d4ed8"
  banner-wash: "#fdecee"
  input-stroke: "#8b95a5"
  bar-track: "#dbe3ee"
  health-idle: "#93a4c0"
  health-ok: "#22c55e"
  health-down: "#f87171"
typography:
  display:
    fontFamily: '"Source Sans 3", "Helvetica Neue", Helvetica, Arial, sans-serif'
    fontSize: "1.35rem"
    fontWeight: 700
    lineHeight: 1
    letterSpacing: "0.02em"
  headline:
    fontFamily: '"Source Sans 3", "Helvetica Neue", Helvetica, Arial, sans-serif'
    fontSize: "0.95rem"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "0.06em"
  title:
    fontFamily: '"Source Sans 3", "Helvetica Neue", Helvetica, Arial, sans-serif'
    fontSize: "0.95rem"
    fontWeight: 700
    lineHeight: 1
    letterSpacing: "normal"
  body:
    fontFamily: '"Source Sans 3", "Helvetica Neue", Helvetica, Arial, sans-serif'
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.45
    letterSpacing: "normal"
  label:
    fontFamily: '"Source Sans 3", "Helvetica Neue", Helvetica, Arial, sans-serif'
    fontSize: "0.72rem"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "0.06em"
rounded:
  sheet: "6px"
  pill: "999px"
  circle: "50%"
spacing:
  xs: "0.4rem"
  sm: "0.55rem"
  md: "0.7rem"
  lg: "1.2rem"
  xl: "1.35rem"
components:
  button-primary:
    backgroundColor: "{colors.navy}"
    textColor: "{colors.white}"
    typography: "{typography.title}"
    rounded: "{rounded.sheet}"
    padding: "0.7rem 1.35rem"
  button-primary-hover:
    backgroundColor: "{colors.navy-ink}"
    textColor: "{colors.white}"
    typography: "{typography.title}"
    rounded: "{rounded.sheet}"
    padding: "0.7rem 1.35rem"
  input-game:
    backgroundColor: "{colors.white}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sheet}"
    padding: "0.55rem 0.7rem"
    width: "20rem"
  card-sheet:
    backgroundColor: "{colors.white}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sheet}"
    padding: "1.05rem 1.2rem"
  chip-health:
    backgroundColor: "transparent"
    textColor: "{colors.white}"
    typography: "{typography.title}"
    rounded: "{rounded.pill}"
    padding: "0.22rem 0.7rem 0.22rem 0.5rem"
  nav-mast:
    backgroundColor: "{colors.navy}"
    textColor: "{colors.white}"
    typography: "{typography.display}"
    height: "3.5rem"
    padding: "0 1.35rem"
  table-head:
    backgroundColor: "{colors.navy}"
    textColor: "{colors.white}"
    typography: "{typography.label}"
    padding: "0.65rem 0.8rem"
  banner-error:
    backgroundColor: "{colors.banner-wash}"
    textColor: "{colors.navy-ink}"
    rounded: "{rounded.sheet}"
    padding: "0.7rem 0.8rem"
---

# Design System: AthletIQ

## Overview

**Creative North Star: "The NBA.com/Stats Desk"**

AthletIQ is a local stats-desk query: enter a loaded `game_id`, read the home-win call, then read the pin, methodology, and limitations. The craft is NBA.com/Stats executed straight — navy mast, a single red Q in the AthletIQ wordmark, white sheets on cool gray paper, navy box-score heads, Source Sans 3. It is not a betting board, not a live odds rail, and not a circular win meter.

Density is compact and tabular. Interactive labels stay title case. The page is one centered desk column, not an app shell with side rails. Probability is a numeric percent plus a linear navy fill. The home-win call is the words Yes or No in desk ink. Health is a labeled pill on the mast; color never carries that state alone.

This is a category-standard sports-analytics dashboard. Copy is English and names real endpoints. Focus rings are visible. The prediction is a disclosed estimate, not a scoreboard celebration.

**Key Characteristics:**

- Full-bleed navy mast: AthletIQ with a red Q, white-outline Health pill
- Cool gray paper field; exactly two white lifted sheets (lookup + result)
- Source Sans 3 at 400 / 600 / 700; no second display face
- Title-case Game ID, Predict, and Health; uppercase reserved for table heads, disclose titles, and error codes
- Ink Yes/No; navy linear P(home win) bar; 32px navy circular medals on the paper, not on a third card

## Colors

A cool navy desk with one league-red signal. Neutrals do the paper, ink, and rules. Green exists only as the health-ok pulse.

### Primary

- **League Navy** (`navy`): Mast, Predict fill, box-score header, disclose titles, probability fill, and the medal discs. This is the structural color of the desk.

### Secondary

- **League Red** (`red`): The Q in AthletIQ, error-banner stroke, and the uppercase error-code line. It is identity and fault chrome, not a win color.

### Tertiary

- **Focus Blue** (`focus`): 2px keyboard rings on the game field and Predict. Do not use it as a fill.

### Neutral

- **Cool Paper** (`paper`): Page field behind the sheets and the disclose columns.
- **Sheet White** (`white`): Lookup and result sheets, table cells, mast type, Health outline.
- **Desk Ink** (`ink`): Body copy and the Yes/No call.
- **Mast Ink** (`navy-ink`): Game ID label, Predict hover fill, banner body type.
- **Quiet Slate** (`muted`): Pin hint, captions, empty states, meta, colophon, bar cap.
- **Hairline Rule** (`rule`): Sheet stroke and row rules.
- **Field Stroke** (`input-stroke`): Game ID border at rest.
- **Track Mist** (`bar-track`): Probability track behind the navy fill.
- **Alert Wash** (`banner-wash`): Error banner field.
- **Pulse Idle / OK / Down** (`health-idle`, `health-ok`, `health-down`): 8px Health dots only. The pill label still names the state.

### Named Rules

**The Red Q Rule.** Red is the Q and fault chrome. It is never a win, probability, or health-success fill.

**The Ink Call Rule.** Home-win Yes/No is desk ink on a white cell. Never green, never red, never a filled badge.

## Typography

**Display Font:** Source Sans 3 (Helvetica Neue, Helvetica, Arial)
**Body Font:** Source Sans 3 (same stack)
**Label/Mono Font:** none — `<code>` is the body face at 0.9em

**Character:** One news-desk sans. Weight and case carry hierarchy; no serif, no condensed scoreboard face, no display italic for headlines.

### Hierarchy

- **Display** (700, 1.35rem, line-height 1, 0.02em): AthletIQ in the mast.
- **Headline** (700, 0.95rem, 0.06em, uppercase): Methodology and Limitations. Pair with the 32px navy medal; do not sit a kicker above them.
- **Title** (700, 0.95rem, normal case): Game ID and Predict. Health is 0.875rem / 600, still title case.
- **Body** (400, 1rem, 1.45): Page default, methodology and limitations prose (0.9rem in those columns). Input value is 600 / 1rem / 1.2.
- **Label** (700, 0.72rem, 0.06em, uppercase): Box-score column heads on navy. Caption/hint/meta sit at 0.88–0.9rem in Quiet Slate; colophon at 0.8rem.

### Named Rules

**The Title-Case Controls Rule.** Game ID, Predict, and Health stay title case with no tracking. Uppercase is only for box-score heads, disclose section titles, and error codes.

## Layout

One full-bleed navy mast, then a centered column `min(56rem, calc(100% - 2rem))`. Vertical order is lookup sheet, pin hint, result sheet, two-column disclose, colophon. Horizontal rhythm on the desk is 1.2rem sheet padding and 1.35rem page/disclose gaps. Lookup is a wrapping row: label, 20rem field, Predict. Disclose is two equal columns with 2.25rem column gap, sitting on the paper. At 640px the lookup stacks and stretches, Predict goes full width, disclose becomes one column, the 100% cap hides, and the probability track shortens to 3.75rem.

### Named Rules

**The Desk Column Rule.** One stats-desk column. No sidebar, no betting rail, no app-shell navigation beyond the mast.

## Elevation & Depth

Hybrid: tonal bands (navy mast / paper field / white sheets) plus one ambient shadow on the sheets. Disclose, hint, and colophon stay flat on the paper. No hover lift, no offset neobrutalist shadow, no overlay scrim.

### Shadow Vocabulary

- **Sheet** (`box-shadow: 0 2px 8px rgba(15, 23, 42, 0.14)`): Lookup and result cards only, with a 1px Hairline Rule.

### Named Rules

**The Two-Sheet Rule.** Only the lookup row and the result sheet lift. Methodology and Limitations stay on the paper, not in a third card.

## Shapes

Sheets, fields, Predict, and error banners share a 6px corner. The Health chip is the only pill (999px) and the only 1px white stroke on navy. Health dots and medals are true circles. The probability track is a sharp 0.5rem-tall rectangle — no stadium cap, no ring.

### Named Rules

**The Soft Sheet Rule.** 6px on sheets and controls. The Health chip is the only pill. Probability is a sharp rectangular bar, never a circular meter.

## Components

### Buttons

- **Shape:** Soft sheet corners (6px).
- **Primary:** League Navy fill, white 700 title-case Predict, padding 0.7rem 1.35rem. No letter-spacing, no uppercase.
- **Hover / Focus:** Hover and active darken to Mast Ink. Focus-visible is a 2px Focus Blue ring, offset 2px. Disabled is 0.55 opacity, not a new color.
- **Secondary / Ghost / Tertiary:** none. Do not add ghost buttons on the mast.

### Chips

- **Style:** Health is a transparent pill on the mast, 1px white border, 0.875rem / 600 white type, 8px circular pulse, gap 0.4rem.
- **State:** Idle pulse is `health-idle`; ok is `health-ok` with the label Health; down uses `health-down` and the error code as the label. Color is not the only signal.

### Cards / Containers

- **Corner Style:** 6px.
- **Background:** Sheet White.
- **Shadow Strategy:** Sheet shadow only (see Elevation).
- **Border:** 1px Hairline Rule.
- **Internal Padding:** Lookup 1.05rem / 1.2rem; result 1rem / 1.2rem. Empty result keeps a 5.25rem min-height.

### Inputs / Fields

- **Style:** White field, 1px Field Stroke, 6px corners, 600 ink, padding 0.55rem / 0.7rem, width 20rem (full width when stacked).
- **Focus:** 2px Focus Blue outline, 1px offset. No glow, no navy border swap.
- **Error / Disabled:** Invalid lookup is not a red input; it is a banner in the result sheet.

### Navigation

- **Style:** Full-bleed League Navy mast, min-height 3.5rem, space-between brand and Health, padding 0 1.35rem (tighter on small screens). Brand is Display weight with the Q in League Red. No extra nav links. Skip link is a white chip with navy type that appears on focus.

### Box-score table

Navy uppercase heads with a near-white vertical rule between columns. White cells, Hairline row rules, 0.65rem / 0.8rem padding, 0.95rem body (0.82rem on small screens). Home win is 700 Desk Ink. P(home win) is a percent, a Track Mist bar, a League Navy fill, and a 100% cap in Quiet Slate.

### Error banner

6px sheet, Alert Wash field, 1px League Red stroke. Strong line is League Red, 0.8rem, 0.04em, uppercase (the API code). Body is Mast Ink. Used in the result sheet and, on model failure, in both disclose columns.

### Disclose medals

32px navy discs with white glyphs (bar chart for Methodology, shield for Limitations). They sit in the section heading row, 0.55rem from the uppercase navy title. Do not replace them with icon fonts.

### Named Rules

**The Linear Probability Rule.** P(home win) is a percent plus a navy fill in a cool rectangular track. No gauges, rings, or pie meters.

**The Medal Pair Rule.** Methodology and Limitations are a paired heading-plus-medal on the paper. Do not promote them into cards or kickers.

## Do's and Don'ts

### Do:

- **Do** keep the navy mast, red Q, Cool Paper field, and two white 6px sheets.
- **Do** set Game ID, Predict, and Health in title case.
- **Do** set Yes/No in Desk Ink and P(home win) as a linear navy bar.
- **Do** show a 2px Focus Blue ring on keyboard focus.
- **Do** pair disclose titles with the navy circular medals and leave those columns on the paper.

### Don't:

- **Don't** color the home-win call green or red, or wrap it in a success/fail badge.
- **Don't** use a circular win meter, gauge, or pie for probability.
- **Don't** lift Methodology/Limitations into a third card or add a sidebar/odds rail.
- **Don't** all-caps Game ID, Predict, or Health, or add eyebrow kickers above titles.
- **Don't** introduce a second display face or a glyph-icon font.
- **Don't** spread Pulse OK green beyond the Health dot.
