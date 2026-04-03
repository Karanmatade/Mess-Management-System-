# Design System Document: Premium Mess Management Interface

## 1. Overview & Creative North Star: "The Culinary Concierge"
The Creative North Star for this design system is **"The Culinary Concierge."** We are moving away from the "utility software" aesthetic and toward a high-end, editorial hospitality experience. This system treats hostel mess management not as a logistical chore, but as a premium service.

To break the "template" look, we utilize **Intentional Asymmetry**. Instead of perfectly centered grids, we use weighted layouts where the Fixed Left Sidebar acts as a heavy anchor, allowing the main content to breathe with varying card widths and overlapping glass layers. We lean into high-contrast typography scales—pairing massive, thin display headers with dense, functional metadata—to create a sense of digital craftsmanship.

---

## 2. Colors & Surface Philosophy
The palette is rooted in deep obsidian tones, punctuated by vibrant, "bio-luminescent" accents that signify freshness (Green) and urgency (Red).

### The "No-Line" Rule
**Explicit Instruction:** Designers are prohibited from using 1px solid borders to section off content. Physical boundaries must be defined solely through:
1.  **Background Shifts:** e.g., A `surface-container-low` card nested within a `surface` background.
2.  **Tonal Transitions:** Using depth and layering to imply edges rather than drawing them.

### Surface Hierarchy & Nesting
Treat the UI as a series of physical layers of smoked glass. 
- **Base Layer:** `surface` (#131313) for the main application background.
- **Sectioning:** Use `surface-container-lowest` (#0e0e0e) for "sunken" areas like the sidebar or secondary utility panels.
- **Elevated Cards:** Use `surface-container-high` (#2a2a2a) with 60% opacity and a 20px Backdrop Blur to create the signature glassmorphism effect.

### The "Glass & Gradient" Rule
To add "soul," never use flat green for primary CTAs. Instead, apply a linear gradient from `primary` (#4be277) to `primary_container` (#22c55e) at a 135-degree angle. This creates a subtle inner glow that mimics premium hardware interfaces.

---

## 3. Typography: Editorial Precision
We utilize a dual-font strategy: **Plus Jakarta Sans** for expressive, high-impact moments and **Inter** for rigorous data density.

*   **Display & Headlines (Plus Jakarta Sans):** Used for "Daily Menu" titles or "Total Balance." Large scales (Display-LG) should use tight letter-spacing (-0.02em) to feel authoritative.
*   **Body & Labels (Inter):** Used for meal descriptions (e.g., "Paneer Butter Masala"), currency units (₹), and timestamps. Inter’s tall x-height ensures legibility against dark, blurred backgrounds.
*   **Hierarchy Note:** Use `title-lg` for meal types (Breakfast, Lunch, Dinner) in semi-bold to ensure they anchor the card, while using `label-md` in `on_surface_variant` (#bccbb9) for nutritional info or server names.

---

## 4. Elevation & Depth: Tonal Layering
Traditional drop shadows are too "cheap" for this system. We achieve lift through light, not darkness.

*   **The Layering Principle:** Place a `surface-container-highest` card atop a `surface-container-low` section. The delta in luminance creates a natural "pop" without a single pixel of shadow.
*   **Ambient Shadows:** For floating modals, use a shadow with a 40px blur, 0% spread, and an opacity of 8% using the `on_primary_fixed` color. This simulates a soft green ambient glow reflecting off the surface.
*   **The "Ghost Border" Fallback:** If accessibility requires a container edge, use `outline_variant` (#3d4a3d) at **15% opacity**. It should be felt, not seen.
*   **Glassmorphism:** All primary cards must use `surface_container_high` with a `saturate(180%) blur(20px)` CSS filter. This allows the background colors of the mess schedule to bleed through softly.

---

## 5. Components

### Buttons
*   **Primary:** Gradient fill (`primary` to `primary_container`), white text (`on_primary`), 12px radius. No shadow; use a 1px "Ghost Border" inner glow.
*   **Secondary:** Ghost style. Transparent background, `outline` color text, and a 10% opacity `primary` hover state.

### Input Fields (The "Mess Entry" Style)
*   **Form Factor:** Forgo the "box" look. Use a `surface-container-highest` fill with a bottom-only 2px accent in `primary` when focused. 
*   **Currency Inputs:** The ₹ symbol should be `title-md` and colored in `primary_fixed` to highlight financial transactions.

### Cards (Meal & Rebate Cards)
*   **Constraint:** **Strictly no dividers.** 
*   **Separation:** Use vertical whitespace (1.5rem / `xl` scale) to separate the "Main Course" from "Sides." 
*   **Status Indicators:** Use a `secondary` (#ffb3b6) soft glow for "Missed Meals" and a `primary` glow for "Consumed."

### Additional Contextual Components
*   **The "Meal-Slider":** A horizontal glass carousel for switching between Monday–Sunday, using `surface_bright` to indicate the active day.
*   **QR Scanner Overlay:** A full-screen glass blur (`surface` at 40% alpha) with a `primary` corner-bracket frame for student ID verification.

---

## 6. Do's and Don'ts

### Do
*   **Do** use `secondary` (Deep Red) sparingly for "Low Balance" or "Mess Off" alerts.
*   **Do** embrace negative space. If a card feels crowded, increase the padding to `xl` (1.5rem) rather than adding a border.
*   **Do** use `display-sm` for the ₹ balance to make the financial status feel "designed" rather than just "calculated."

### Don't
*   **Don't** use pure white (#FFFFFF) for text. Always use `on_surface` (#e5e2e1) to prevent eye strain against the dark background.
*   **Don't** use standard 4px border radii. This system lives in the **12px–16px (md to lg)** range to maintain a "soft-tech" feel.
*   **Don't** use icons with heavy fills. Use thin-stroke (1.5pt) "Linear" icons to match the Inter typography weight.