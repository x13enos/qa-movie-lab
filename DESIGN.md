---
name: Movie QA Lab
description: User-selected light neutral movie catalog
colors:
  primary: "#2055ad"
  ink: "#202a36"
  muted: "#586574"
  line: "#d9e0e8"
  canvas: "#f6f8fa"
  surface: "#ffffff"
typography:
  body:
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'
    lineHeight: 1.55
  title:
    fontSize: "17px"
    fontWeight: 700
    lineHeight: 1.35
  label:
    fontSize: "13px"
rounded:
  control: "4px"
  poster: "5px"
spacing:
  compact: "8px"
  medium: "16px"
  group: "24px"
components:
  button:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.primary}"
    rounded: "{rounded.control}"
    padding: "10px 18px"
---

# Design System: Movie QA Lab

## Overview

Light, neutral and minimal, as selected by the user. Content and familiar pagination lead; the page is an operating surface, not a promotional landing page. Local fictional poster illustrations provide visual distinction without external fonts or image services.

## Colors

Blue is reserved for actionable controls, links and focus. Slate ink and muted text sit on a cool near-white canvas, with white header and controls. The TMDB mark retains its original branding; illustration palettes are content, not UI tokens.

## Typography

The operating UI uses the system sans stack, not a separately branded display face. Main title 26px (23px on mobile), section heading 20px, movie title 17px, descriptions and buttons 14px, metadata 13px. Ratings and page labels use tabular numerals. Footer text is constrained to 75ch.

## Layout

Shared container: maximum 1200px, horizontal padding 28px, reduced to 20px at 680px. Movie grid: four columns; three at 950px, two at 680px, one at 380px. Desktop gaps: 30px vertically and 24px horizontally; mobile: 24px and 16px. Header wraps identity and source label. Pagination remains centered after the catalog.

## Elevation & Depth

Flat tonal separation and thin dividers, no shadows, glass or decorative movement. Content is visible without entrance animation.

## Shapes

Poster ratio 2:3 with gently rounded corners. Small-radius rectangular buttons and mode badge; no nested card shells. Cards have no border or background separate from the canvas.

## Components

- **Movie card:** poster, linked title, year, rating, three-line description. Titles use the established blue underlined link treatment to open details. Missing posters and descriptions have clear text fallbacks. Image failures also show the poster placeholder.
- **Rating field:** native number input, visible label and range hint, white fill, thin neutral border and existing control radius. Apply and Reset reuse the outlined button. Filter controls wrap on narrow screens.
- **Movie details:** back link, movie heading, poster beside a definition list and complete description. Below 680px, poster and content stack. Missing values use explicit text; loading, not-found and error states remain plain live text.
- **Pagination:** native buttons, 44px minimum height, outlined blue default, tonal hover/active, muted disabled. A 3px blue outline with 4px offset marks keyboard focus.
- **Mode label:** compact noninteractive badge; source is not a filter.
- **Status:** plain live text for loading/empty, red text and recovery advice for errors.
- **Credits:** small official logo with required disclaimer, fictional demo data identified separately.

## Do's and Don'ts

- **Do** preserve readable titles, visible focus, responsive whole-card reflow and explicit UI states.
- **Do** bundle fixture assets locally and keep synthetic content clearly labelled.
- **Don't** expose future functionality as working controls or make cards appear clickable when no details exist.
- **Don't** recolor, stretch or prominently feature the TMDB mark above the application name.

Not canonized: repeated poster artwork is a bounded MVP fixture asset choice, not a rule for real movie data.
