---
name: AthletIQ
description: Broadcast win-probability gamecast for a disclosed home-win estimate.
colors:
  field: "#0d1117"
  producer: "#07090c"
  home: "#3ec6ff"
  away: "#ffb020"
  ink-fill: "#0a0c10"
  type: "#f4f7fb"
  muted: "#9aa8b8"
  rule: "#2a313c"
  market: "#12161c"
  track: "#1c232d"
  dormant: "#1a212b"
  dormant-type: "#d8dee8"
  error: "#ff8a8a"
  error-wash: "#2a1214"
  health-ok: "#22c55e"
  health-down: "#f87171"
  health-idle: "#8b9bb0"
typography:
  display:
    fontFamily: '"Barlow Condensed", "Arial Narrow", "Helvetica Neue", sans-serif'
    fontSize: "clamp(2.8rem, 9vw, 6rem)"
    fontWeight: 800
    lineHeight: 0.85
    letterSpacing: "-0.02em"
  headline:
    fontFamily: '"Barlow Condensed", "Arial Narrow", "Helvetica Neue", sans-serif'
    fontSize: "clamp(2.4rem, 7vw, 5.2rem)"
    fontWeight: 800
    lineHeight: 0.9
    letterSpacing: "-0.03em"
  title:
    fontFamily: '"Barlow Condensed", "Arial Narrow", "Helvetica Neue", sans-serif'
    fontSize: "1.85rem"
    fontWeight: 800
    lineHeight: 1
    letterSpacing: "0.04em"
  body:
    fontFamily: '"Barlow Condensed", "Arial Narrow", "Helvetica Neue", sans-serif'
    fontSize: "1.05rem"
    fontWeight: 500
    lineHeight: 1.35
    letterSpacing: "normal"
  label:
    fontFamily: '"Barlow Condensed", "Arial Narrow", "Helvetica Neue", sans-serif'
    fontSize: "0.82rem"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "0.08em"
rounded:
  none: "0"
spacing:
  xs: "0.4rem"
  sm: "0.65rem"
  md: "1.25rem"
  lg: "1.4rem"
  xl: "2.5rem"
components:
  button-primary:
    backgroundColor: "{colors.producer}"
    textColor: "{colors.home}"
    rounded: "{rounded.none}"
    padding: "0.5rem 1.15rem"
  button-primary-hover:
    backgroundColor: "{colors.home}"
    textColor: "{colors.ink-fill}"
    rounded: "{rounded.none}"
    padding: "0.5rem 1.15rem"
  input-game:
    backgroundColor: "{colors.field}"
    textColor: "{colors.type}"
    rounded: "{rounded.none}"
    padding: "0.48rem 0.55rem"
    width: "7.5rem"
  chip-pin:
    backgroundColor: "{colors.track}"
    textColor: "{colors.home}"
    typography: "{typography.label}"
    rounded: "{rounded.none}"
    padding: "0.22rem 0.5rem"
  chip-health:
    backgroundColor: "transparent"
    textColor: "{colors.type}"
    typography: "{typography.label}"
    rounded: "{rounded.none}"
    padding: "0.28rem 0.65rem"
  nav-producer:
    backgroundColor: "{colors.producer}"
    textColor: "{colors.type}"
    height: "4.5rem"
    padding: "0.65rem 1.25rem"
  seg-league:
    backgroundColor: "transparent"
    textColor: "{colors.type}"
    rounded: "{rounded.none}"
    padding: "0.38rem 0.7rem"
  seg-league-pressed:
    backgroundColor: "{colors.type}"
    textColor: "{colors.ink-fill}"
    rounded: "{rounded.none}"
    padding: "0.38rem 0.7rem"
  split-home:
    backgroundColor: "{colors.home}"
    textColor: "{colors.ink-fill}"
    padding: "1.4rem 1.35rem 1.2rem"
  split-away:
    backgroundColor: "{colors.away}"
    textColor: "{colors.ink-fill}"
    padding: "1.4rem 1.35rem 1.2rem"
  split-dormant:
    backgroundColor: "{colors.dormant}"
    textColor: "{colors.dormant-type}"
    padding: "1.4rem 1.35rem 1.2rem"
  market-ribbon:
    backgroundColor: "{colors.market}"
    textColor: "{colors.muted}"
    height: "2.6rem"
    padding: "0.55rem 1.25rem"
  banner-error:
    backgroundColor: "{colors.error-wash}"
    textColor: "{colors.type}"
    padding: "0.75rem 1.25rem"
  chyron:
    backgroundColor: "{colors.field}"
    textColor: "{colors.type}"
    padding: "1.35rem 1.25rem"
---

# Design System: AthletIQ

## Overview

**Creative North Star: "The Powered-On Gamecast"**

AthletIQ is a local lookup instrument drawn as a powered-on broadcast win-probability graphic. Pick NBA or WNBA, enter a loaded `game_id`, TAKE, and read Home versus Away as a full-bleed horizontal split of model P against implied 1−P, then a labeled synthetic Market P ribbon, the served pin, and legal Methodology / Limitations chyrons. The craft is matte charcoal, ice-cyan Home plates, amber Away plates, Barlow Condensed gothic, hard edges, and a producer bar. It is not an NBA.com/Stats desk, not a scorebug, and not a sportsbook.

Density is broadcast-tight: all lookup chrome lives in one full-bleed producer strip. Idle plates sit dormant with em dashes; a successful TAKE slams them into cyan and amber widths. Type on live plates is near-black plate ink. Health is a labeled hard chip with an authored waveform; color never carries that state alone. Copy is English and names real endpoints. The prediction is a disclosed estimate, not a scoreboard celebration.

This is sports-broadcast graphic language on a local demo. Keyboard focus is a 2px ice-cyan ring. There is no second display face and no rounded sheet.

**Key Characteristics:**

- Full-bleed producer bar: ATHLETIQ, NBA/WNBA, Health waveform, pin chips, Game ID, TAKE, Gamecast/Slate/Board switch, 2px ice-cyan underline
- Giant horizontal split: dormant charcoal and dashes at rest; live ice-cyan / amber widths equal model P vs 1−P
- Market ribbon under the split, labeled Synthetic · not a book, echoing the same two-color split
- Two legal chyron columns on the field (Methodology | Limitations) with underlined gothic titles
- Barlow Condensed at 400 / 500 / 700 / 800; producer chrome uppercase; chyron body sentence case
- Hard edges (0 radius); flat band stack; no lifted sheets

## Colors

A matte charcoal broadcast field with two live plate colors — ice cyan for Home, amber for Away. Neutrals do producer chrome, type, and rules. Green exists only on the health waveform.

### Primary

- **Ice Cyan** (`home`): Live Home plate, 2px producer underline, TAKE stroke and type, pin-chip type, idle-hint links, and keyboard focus. Structural live-Home chrome, not the page field.

### Secondary

- **Away Amber** (`away`): Live Away plate and the Market ribbon’s away echo. Never a producer fill, never a focus ring, never Health.

### Neutral

- **Matte Charcoal** (`field`): Page field and the Game ID input fill.
- **Producer Black** (`producer`): Producer bar fill, TAKE rest fill, and the 2px rule between live plates.
- **Plate Ink** (`ink-fill`): Type on live cyan and amber plates, TAKE hover type, pressed league cell, skip-link type.
- **Broadcast White** (`type`): Body type on charcoal, wordmark, idle producer chrome, skip-link fill, pressed-segment fill, chyron title underline.
- **Quiet Steel** (`muted`): Market labels, idle hint, chyron empty/meta, colophon.
- **Hairline Graphite** (`rule`): Split bottom rule, market bottom rule, pin-chip stroke.
- **Market Ribbon** (`market`): Full-bleed band under the split.
- **Track Slate** (`track`): Pin-chip fill.
- **Dormant Plate** (`dormant`): Idle/error/loading split plates and the idle Market echo.
- **Dormant Type** (`dormant-type`): Type on dormant plates.
- **Fault Pink** (`error`): Error-code line and banner bottom stroke.
- **Fault Wash** (`error-wash`): Error banner field.
- **Wave Idle / OK / Down** (`health-idle`, `health-ok`, `health-down`): Health waveform stroke only. The chip label still names the state.

### Named Rules

**The Two-Plate Rule.** Live Home is ice cyan; live Away is amber. Width is model P versus implied 1−P. Type on live plates is plate ink. Idle plates are dormant charcoal with dashes — never franchise colors, never a third meter language.

**The Ice-Cyan Chrome Rule.** Ice cyan is Home’s live fill, the producer underline, TAKE, pin type, idle-hint links, and focus rings. It is not Away, not a page field, and not health-success.

## Typography

**Display Font:** Barlow Condensed (Arial Narrow, Helvetica Neue)
**Body Font:** Barlow Condensed (same stack)
**Label/Mono Font:** none — `<code>` is the gothic at a slightly smaller size

**Character:** One condensed broadcast gothic. Weight, tracking, and uppercase carry hierarchy. No serif, no news-desk grotesque, no italic display.

### Hierarchy

- **Display** (800, `clamp(2.8rem, 9vw, 6rem)`, line-height 0.85, −0.02em): Team abbr on each plate (HOME / AWAY or served names), uppercase. At 720px this steps to `clamp(1.8rem, 12vw, 2.6rem)`.
- **Headline** (800, `clamp(2.4rem, 7vw, 5.2rem)`, line-height 0.9, −0.03em): Live probability numerals. Dormant numerals sit smaller (`clamp(2rem, 5vw, 3.4rem)` with 0.12em tracking). At 720px live numerals step to `clamp(1.6rem, 10vw, 2.2rem)`.
- **Title** (800, 1.85rem, 0.04em, uppercase): ATHLETIQ wordmark in the producer bar. Disclose headings use the same weight and case at 1.05rem / 0.14em with a 1px Broadcast White underline.
- **Body** (500, 1.05rem, 1.35): Page default. Chyron prose is 400 / 0.98rem / 1.4, max 75ch. Idle hint is 0.95rem Quiet Steel. Input value is 700 / 1.15rem. Plate role labels (Home / Away) are 700 / 1rem / 0.16em uppercase.
- **Label** (700, 0.82rem, 0.08em, uppercase): League cells, Health, Game ID, pin chips (0.78rem), market copy, error codes, TAKE (800 / 1rem / 0.12em). Implied-P captions are 0.72rem / 0.1em at 80% opacity. Colophon is 0.85rem / 0.04em Quiet Steel.

### Named Rules

**The Gothic Case Rule.** Producer chrome, TAKE, league codes, Health, chips, market copy, disclose titles, and plate abbr/role stay uppercase condensed. Chyron body stays sentence case at 400. Visible TAKE is the word TAKE (accessible name Predict).

## Layout

Full-bleed producer bar (`min-height` 4.5rem, padding 0.65rem / 1.25rem) holds brand, league, Health, pin chips, Game ID, and TAKE. TAKE’s lookup cluster is `margin-left: auto`. Below it, a flex column stage: optional error banner, giant horizontal split (`min-height: min(52vh, 28rem)`), market ribbon (`min-height` 2.6rem), idle hint, two chyron columns, colophon. Horizontal gutter is 1.25rem. Disclose is two equal columns with 2.5rem column gap, sitting on the charcoal field. No centered desk column, no identity band, no sidebar.

At 720px the lookup cluster goes full width, the Game ID field flexes, TAKE stays right, the split min-height becomes 16rem, and disclose stacks to one column.

### Named Rules

**The Producer Bar Rule.** Lookup lives in the producer bar. Do not reintroduce a white identity band, a lifted lookup sheet, or a second header.

## Elevation & Depth

Flat tonal banding. Depth is stacked broadcast bands: Producer Black, Matte Charcoal, live plates or Dormant Plate, Market Ribbon. No `box-shadow`. No hover lift. Live plates and the Market echo ease width and fill (220ms, `cubic-bezier(0.16, 1, 0.3, 1)`) when `prefers-reduced-motion: no-preference`.

### Named Rules

**The Band Stack Rule.** Surfaces are flat. Separate regions with fill change and 1–2px rules, never shadow or rounded lift.

## Shapes

Every control, chip, field, plate, and banner is a hard rectangle (`border-radius: 0`). The producer underline is a hard 2px Ice Cyan stripe. TAKE is a 2px Ice Cyan outline. League, Health, and pin chips use 1px hairlines. The Home plate’s inner edge is a 2px Producer Black divider. The Market echo is a sharp 0.85rem-tall rectangle. Health is not a pill. Probability is plate width, never a stadium bar or a ring.

### Named Rules

**The Hard-Edge Rule.** Radius is 0. No pills, no 6px sheets, no stadium tracks, no circular meters.

## Components

### Buttons

- **Shape:** Hard rectangle (0).
- **Primary:** TAKE. Producer Black fill, 2px Ice Cyan stroke, Ice Cyan 800 uppercase, padding 0.5rem / 1.15rem, tracking 0.12em. Visible label TAKE.
- **Hover / Focus:** Hover fills Ice Cyan with Plate Ink type. Focus-visible is a 2px Ice Cyan ring, offset 2px. Disabled is 0.55 opacity (`cursor: wait` while a lookup runs).
- **Text control:** Idle-hint fixture id is Ice Cyan, 800, underlined, no chrome.

### Chips

- **Health:** Hard rectangle on the producer, 1px Broadcast White stroke at 55%, 0.82rem / 700 / 0.08em uppercase, authored 24×12 waveform SVG. Wave idle / ok / down colors the stroke only. Down replaces the Health label with the error code.
- **Pin:** Track Slate fill, 1px Hairline Graphite, Ice Cyan 700 uppercase, padding 0.22rem / 0.5rem. Model pin and feature version only.

### Cards / Containers

- **Corner Style:** None (0). This system has no lifted sheets.
- **Background:** Regions are full-bleed bands (producer, split, market, field), not cards.
- **Shadow Strategy:** None (see Elevation).
- **Border:** 1–2px rules between bands.
- **Internal Padding:** Plates 1.4rem / 1.35rem / 1.2rem. Chyrons 1.35rem / 1.25rem / 2rem.

### Inputs / Fields

- **Style:** Matte Charcoal fill, hard corners, Broadcast White 700 at 1.15rem, padding 0.48rem / 0.55rem, width 7.5rem (flexes full remaining width at 720px).
- **Focus:** 2px Ice Cyan outline, 2px offset. No glow.
- **Error / Disabled:** Invalid lookup is the error banner, not a red input.

### Navigation

- **Producer:** Full-bleed Producer Black, min-height 4.5rem, wrapping row, 2px Ice Cyan bottom border. Brand is ATHLETIQ at title size. Tools are league, Health, pin chips; lookup is Game ID + TAKE on the right. **CR-005:** a hard segmented surface switch (Gamecast / Slate / Board) sits in the producer bar on all three paths. Skip link is a Broadcast White chip with Plate Ink, uppercase, that appears on focus.
- **League switch:** Hard segmented control, 1px Broadcast White stroke at 45% on Producer Black. Cells are 700 / 0.85rem / 0.08em / uppercase. Pressed cell inverts to Broadcast White / Plate Ink. Hover on an idle cell is white at 12%. Focus-visible is a 2px Ice Cyan ring.
- **Slate (`/slate`):** Same producer family. Demo-user switch updates `?user=`. Next unplayed game uses the Home/Away split; remaining games are stacked lower-thirds (cyan/amber plates), not a gray table. LOCK places an integer e-coin stake. Copy may say stake/settle. Forbidden: odds/juice/moneyline/payout/wager.
- **Board (`/board`):** Same producer family. In-progress plates may show provider scores. Clock only if the JSON included one — never invented. Gamecast still has no score/clock.

### Win-probability split

Two flex plates. Idle, loading, and error: equal 50% Dormant Plate, Dormant Type, dashes for percents, implied caption hidden. Live: Home flex-basis is model P (Ice Cyan, Plate Ink); Away is 1−P (Away Amber, Plate Ink). Abbr, role, and percent stack to the bottom. Away may show an uppercase implied caption at the bottom-right.

### Market ribbon

Full-bleed Market Ribbon band under the split. Uppercase Quiet Steel label (`Market P · Synthetic · not a book` when that is the source) and percent. Echo bar is 0.85rem tall: dormant until live, then the same cyan/amber width split as the plates.

### Error banner

Full-bleed Fault Wash, 1px Fault Pink bottom stroke, padding 0.75rem / 1.25rem. Strong line is Fault Pink, 0.82rem, 0.08em, uppercase (the API code). Body is Broadcast White.

### Legal chyrons

Two columns on the field. Titles are 800 uppercase with a 1px Broadcast White underline. Prose is 400 Broadcast White, max 75ch. Empty and meta lines are Quiet Steel. No medals, no cards, no kickers.

### Named Rules

**The Market Echo Rule.** Market P is a labeled ribbon echo of the split (synthetic, not a book). It is not a box-score cell, not a sportsbook line, and not unlabeled.

**The Chyron Pair Rule.** Methodology and Limitations are two underlined chyron columns on the field. Do not promote them into cards, medals, or kickers.

**The Waveform Health Rule.** Health is a labeled hard chip with an authored waveform. Color never carries the state alone. Pulse OK green stays on the waveform.

## Do's and Don'ts

### Do:

- **Do** keep the matte charcoal field, Producer Black bar with a 2px Ice Cyan underline, Barlow Condensed, and hard edges.
- **Do** paint live Home ice cyan and live Away amber, widths from model P vs 1−P, with Plate Ink type.
- **Do** keep TAKE uppercase and outlined in the producer bar, with Game ID beside it.
- **Do** label Market P as Synthetic · not a book on the ribbon when that is the source.
- **Do** show a 2px Ice Cyan focus ring, and name Health in type — not by color alone.
- **Do** set Methodology / Limitations as two underlined chyron columns on the field.

### Don't:

- **Don't** round corners, pill Health, or lift white 6px sheets.
- **Don't** revive the NBA.com/Stats desk (league navy/red, Source Sans, STATS lockup, red Q disc, identity band, box-score table, circular medals).
- **Don't** use franchise palettes, a scorebug clock/score/quarter, or PRE-GAME kickers.
- **Don't** use sportsbook language or treat Market P as a book line.
- **Don't** color a Yes/No call green or red; this surface has no Yes/No cell.
- **Don't** spread Pulse OK green beyond the health waveform.
- **Don't** introduce a second display face or a glyph-icon font.
