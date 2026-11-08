# Figma Integration & Design System Rules

This file is the design-system addendum to [`AGENTS.md`](./AGENTS.md). `AGENTS.md` covers commands,
the backend data contract, and runtime gotchas. This file covers **how to translate Figma designs into
this codebase through the Figma MCP server without breaking its conventions**.

Read this before calling any Figma design-to-code tool or editing UI files.

---

## 0. Ground rules (read first)

1. **This is a small, hand-rolled design system.** There is no component library, no Tailwind, no
   CSS-in-JS, no CSS Modules, no Storybook, and no token build pipeline. Do not introduce one.
2. **Reuse before creating.** Map every Figma layer to an existing component or a plain HTML element
   styled with existing tokens. Create a new component only when no existing component fits.
3. **Colors come from CSS variables only.** Never write a hex value in a new rule except `#fff` for
   text on `--primary` (the existing convention) or the existing menu shadow.
4. **One CSS file per component, imported by that component.** No global class additions unless the
   change is genuinely app-wide (then it belongs in `frontend/src/styles/global.css`).
5. **Match the existing BEM-like naming**: `block`, `block__element`, `block__element--modifier`,
   plus shared state classes `is-active`, `is-open`, `is-invalid`, `is-selected`.
6. **No new dependencies** for styling, icons, fonts, animation, or UI primitives.
7. **Verify with `npm run build`.** There is no test runner, linter, or typechecker. Build + manual
   visual comparison is the acceptance bar.
8. **Do not change the backend response shapes** to fit a design. Adapt the UI to the data
   (`backend/app/schemas/accounts.py`, `backend/app/schemas/dashboard.py`).

---

## 1. Design System Structure

### 1.1 Token definitions

**Location:** `frontend/src/styles/global.css` (the only token file).

**Format:** plain CSS custom properties on `:root`, consumed with `var(--token)`. There is **no**
JSON/YAML token source, no Style Dictionary, no PostCSS/Tailwind config, and no runtime theme provider.

```css
/* frontend/src/styles/global.css */
:root {
  --bg: #f4f6fa;
  --surface: #ffffff;
  --border: #e3e7ef;
  --text: #1b2230;
  --muted: #667085;
  --primary: #3b5bdb;

  --income: #2f9e44;
  --savings: #1c7ed6;
  --expenses: #e8590c;
  --investments: #7048e8;

  --positive: #2f9e44;
  --negative: #e03131;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg: #11151c;
    --surface: #1a2029;
    --border: #2a323f;
    --text: #e6e9ef;
    --muted: #9aa4b2;
    --primary: #5c7cfa;
  }
}
```

**Canonical token table**

| Token | Light | Dark | Meaning |
| --- | --- | --- | --- |
| `--bg` | `#f4f6fa` | `#11151c` | App background / inset controls |
| `--surface` | `#ffffff` | `#1a2029` | Cards, taskbar, panels |
| `--border` | `#e3e7ef` | `#2a323f` | All 1px borders and dividers |
| `--text` | `#1b2230` | `#e6e9ef` | Primary text |
| `--muted` | `#667085` | `#9aa4b2` | Labels, metadata, secondary text |
| `--primary` | `#3b5bdb` | `#5c7cfa` | Active mode, primary action, focus |
| `--income` | `#2f9e44` | *(unchanged)* | Income category accent |
| `--savings` | `#1c7ed6` | *(unchanged)* | Savings category accent |
| `--expenses` | `#e8590c` | *(unchanged)* | Expenses category accent |
| `--investments` | `#7048e8` | *(unchanged)* | Investments category accent |
| `--positive` | `#2f9e44` | *(unchanged)* | Positive amounts / trends |
| `--negative` | `#e03131` | *(unchanged)* | Negative amounts / errors |

Notes:
- `--income` and `--positive` currently share a value but are **semantically distinct**. Keep both.
- `--accent` is **not** a global token. It is a component-local custom property set inline per card
  from data (see §1.2). Do not add it to `:root`.
- Dark mode is OS-driven via `prefers-color-scheme`; there is no class toggle or theme context.
  Dark mode only overrides the six base neutrals/brand; semantic category and status colors do not
  change. If a Figma dark frame introduces dark variants for those, add them to the dark block as part
  of the change and call it out.
- There are **no spacing, radius, typography, shadow, or z-index tokens**. Do not invent a token layer
  opportunistically. Use the literal values already in the scale:

| Concern | Values in use |
| --- | --- |
| Spacing (px) | `2, 3, 4, 8, 10, 12, 14, 16, 18, 20, 24, 28` |
| Radii (px) | `5, 7, 8, 10, 12` (pills/carets use borders, not radii) |
| Font sizes (rem) | `0.75, 0.8, 0.85, 0.95, 1, 1.05, 1.1, 1.5, 1.9` |
| Font weights | `400, 500, 600, 700` |
| Border width | `1px`; card accents use `4px` top border |
| Shadow | one only: `0 12px 28px rgba(15, 23, 42, 0.18)` (picker menu) |
| Z-index | `10` sticky taskbar, `20` picker menu |
| Transition | `0.15s` on `background`, `color`, `transform` |

**Token transformation:** none. Figma variables should be authored to mirror these names/values
exactly (see §2.1).

### 1.2 Component library

**Location:** `frontend/src/components/<ComponentName>/<ComponentName>.jsx` +
`<ComponentName>.css`. Page-level compositions live in `frontend/src/pages/<PageName>/`.

**Architecture:** function components, default export, props down / callbacks up. No context, no
state library, no compound-component API. Small local subcomponents are declared in the same file
when private (e.g. `Section` and `Field` inside `AccountDetails.jsx`).

**Inventory**

| Component | Path | Props | Key classes | States |
| --- | --- | --- | --- | --- |
| `App` | `frontend/src/App.jsx` | — | `app`, `app__content` | — |
| `Taskbar` | `components/Taskbar/Taskbar.jsx` | `mode`, `onModeChange`, `accounts`, `accountId`, `onAccountChange` | `taskbar`, `taskbar__brand`, `taskbar__controls`, `taskbar__actions`, `taskbar__btn` | `is-active` + `aria-pressed` |
| `AccountPicker` | `components/AccountPicker/AccountPicker.jsx` | `accounts`, `accountId`, `onChange` | `picker`, `picker__label`, `picker__control`, `picker__input`, `picker__toggle`, `picker__caret`, `picker__menu`, `picker__option`, `picker__option-id`, `picker__option-meta`, `picker__empty` | `is-open`, `is-active`, `is-selected`, `is-invalid`; combobox/listbox/option a11y |
| `CategoryCard` | `components/CategoryCard/CategoryCard.jsx` | `category: { key, title, amount, change }` | `card`, `card__header`, `card__icon`, `card__title`, `card__amount`, `card__change`, `card__change--up/down/flat` | trend up/down/flat |
| `AiInsights` | `components/AiInsights/AiInsights.jsx` | `mode` | `ai`, `ai__header`, `ai__title`, `ai__model`, `ai__form`, `ai__input`, `ai__button`, `ai__error`, `ai__text` | disabled/loading, error, result |
| `AccountDetails` | `components/AccountDetails/AccountDetails.jsx` | `accountId` | `details`, `details__section`, `details__title`, `details__count`, `details__fields`, `details__field`, `details__table-wrap`, `details__table`, `details__more`, `details__loading`, `details__error` | loading, error, paginated |
| `ScenarioForm` | `components/ScenarioForm/ScenarioForm.jsx` | `accountId`, optional `onSubmit({ type, amount })` | `scenario`, `scenario__field`, `scenario__field--grow`, `scenario__label`, `scenario__select`, `scenario__input`, `scenario__button`, `scenario__output`, `scenario__output-meta`, `scenario__output-placeholder`, `scenario__output-error` | `is-invalid` + `aria-invalid`; output box (`aria-live`) shows the Gemini financial plan from `POST /api/scenario/plan` (loading, error, result; recovery vs. debt plan); rendered only in Plan mode |
| `Dashboard` | `pages/Dashboard/Dashboard.jsx` | `mode`, `accountId` | `dashboard`, `dashboard__heading`, `dashboard__notice`, `dashboard__grid` | offline notice, plan notice |
| `AccountDashboard` | `pages/AccountDashboard/AccountDashboard.jsx` | routed params | `account-dashboard__*` | **Unused/legacy — see §7.3** |

**Documentation/storybook:** none in the repo. The components themselves and this table are the
documentation. A matching Figma component library is authored in the design-system file — see §2.1.1
for pages, component sets, variant names, and node IDs.

**The canonical accent pattern** (copy this for any new category-colored surface):

```jsx
// frontend/src/components/CategoryCard/CategoryCard.jsx
import { CATEGORY_META } from "../../constants/categories.js";
import "./CategoryCard.css";

export default function CategoryCard({ category }) {
  const { key, title, amount, change } = category;
  const meta = CATEGORY_META[key];
  const trend = change > 0 ? "up" : change < 0 ? "down" : "flat";

  return (
    <article className="card" style={{ "--accent": meta.accent }}>
      <div className="card__header">
        <span className="card__icon" aria-hidden="true">{meta.icon}</span>
        <h2 className="card__title">{title}</h2>
      </div>
      <p className="card__amount">{currency.format(amount)}</p>
      <p className={`card__change card__change--${trend}`}>…</p>
    </article>
  );
}
```

```css
/* frontend/src/components/CategoryCard/CategoryCard.css */
.card {
  padding: 20px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-top: 4px solid var(--accent);
  border-radius: 12px;
}

.card__icon {
  color: var(--accent);
  background: color-mix(in srgb, var(--accent) 14%, transparent);
}
```

Use `color-mix(in srgb, var(--accent) 14%, transparent)` for accent tints. This is the only tint
recipe in the codebase; do not add new alpha hex values.

### 1.3 Frameworks & libraries

| Layer | Choice | Source |
| --- | --- | --- |
| UI | React `18.3.1` | `frontend/package.json` |
| DOM | `react-dom` `18.3.1` | `frontend/package.json` |
| Routing | `react-router` `7.18.5` installed but **not mounted** | `frontend/package.json`; `App.jsx` renders no router |
| Styling | Plain CSS + CSS custom properties | `frontend/src/**/*.css` |
| Build/dev | Vite `5.4.8` + `@vitejs/plugin-react` `4.3.1` | `frontend/vite.config.js` |
| Backend | FastAPI + pandas (separate app) | `backend/` |

Vite config is minimal: React plugin, port `5173`, `/api` proxied to `http://127.0.0.1:8000`.
No path aliases, no CSS preprocessor, no PostCSS config, no env files.

### 1.4 Asset management

- **There are no image/video/font assets in the repo.** No `frontend/public/`, no `src/assets/`,
  no `@font-face`, no `url(...)` references, no favicon, no CDN configuration.
- `frontend/dist/` exists locally but is **gitignored** and is a build artifact. Never edit it.
- If a design requires an asset:
  1. Put raster/SVG files under `frontend/src/assets/` and import them so Vite fingerprints them:
     `import logo from "../../assets/logo.svg";` then `<img src={logo} alt="…" />`.
  2. Prefer inline SVG React markup for icons that must inherit `currentColor`.
  3. Do not hotlink external URLs or add a CDN. Do not add an image-optimization dependency.
- Fonts: keep the system stack. Do not add Google Fonts or self-hosted fonts unless the task
  explicitly asks for a typography change; the stack is
  `system-ui, -apple-system, "Segoe UI", Roboto, sans-serif` (`global.css`).

### 1.5 Icon system

- **No icon library and no icon files.** Icons are Unicode glyphs defined in
  `frontend/src/constants/categories.js`:

```js
export const CATEGORY_META = {
  income:      { icon: "↗", accent: "var(--income)" },
  savings:     { icon: "◎", accent: "var(--savings)" },
  expenses:    { icon: "↘", accent: "var(--expenses)" },
  investments: { icon: "▲", accent: "var(--investments)" },
};
```

- Usage: `CATEGORY_META[key].icon`, always rendered inside a decorative span with
  `aria-hidden="true"` (`CategoryCard.jsx`).
- The dropdown caret is pure CSS (border triangle) in `AccountPicker.css`
  (`.picker__caret`), rotated with `.is-open`.
- **Convention:** the registry key (`income`, `savings`, …) is the contract; the glyph is an
  implementation detail. If a Figma design replaces glyphs with SVG icons, keep the registry shape
  (`{ icon, accent }`) and swap only the render, or introduce a single `Icon` component in
  `frontend/src/components/Icon/` with the same keys. Do not scatter icon imports across files.
- Icons that convey meaning must have an accessible label; purely decorative icons stay
  `aria-hidden`.

### 1.6 Styling approach

- **Methodology:** plain global CSS with BEM-like, component-scoped class names. There is no
  scoping mechanism (no CSS Modules, no Shadow DOM, no styled-components), so prefixes must stay
  unique per component.
- **Global styles:** `frontend/src/styles/global.css`, imported once in `frontend/src/main.jsx`.
  It contains the token blocks, `box-sizing: border-box`, the `body` base, and the `.app__content`
  container (`max-width: 1100px; margin: 0 auto; padding: 28px 24px`).
- **Per-component styles:** each component/page imports its own CSS file at the top of the JSX.
  Keep the CSS file next to the component and named identically.
- **Responsive strategy:** mobile-down max-width media queries at a single breakpoint, `720px`,
  plus intrinsically responsive grids (`repeat(auto-fill, minmax(180px, 1fr))`) and `flex-wrap`.
  Existing breakpoints: `Dashboard.css`, `AiInsights.css`, `AccountDashboard.css` (all `720px`).
  Do not introduce `768px`/`1024px` breakpoints unless the task explicitly requires a new layout.
- **Layout primitives:** flex for rows/columns, CSS grid for card grids and the account field list.
  No utility classes, no spacing helpers.
- **Focus:** only `.picker__input:focus` defines a focus ring
  (`outline: 2px solid var(--primary); outline-offset: -1px;`). Native buttons rely on the browser
  ring. Never add a blanket `outline: none`; preserve or improve visible focus.
- **Motion:** only `0.15s` transitions on color/background/transform. No keyframes. If you add
  motion, gate it with `@media (prefers-reduced-motion: reduce)`.

### 1.7 Project structure & patterns

```
frontend/
  index.html                     # single entry, #root, /src/main.jsx
  vite.config.js                 # react plugin, :5173, /api proxy
  src/
    main.jsx                     # ReactDOM root + global.css
    App.jsx                      # shell: mode + selected account state
    components/<Name>/           # reusable UI (JSX + matching CSS)
    pages/<Name>/                # page-level composition (JSX + matching CSS)
    services/api.js              # all HTTP calls, BASE_URL = "/api"
    constants/categories.js      # MODES, CATEGORY_META, FALLBACK_CATEGORIES
    styles/global.css            # tokens, reset, app container
    viewModels/AccountPageViewModel.jsx  # one hook-style data view model
backend/
  app/main.py                    # FastAPI, CORS, /api routers
  app/api/routes/                # dashboard.py, accounts.py, insights.py
  app/schemas/                   # Pydantic response models (source of truth)
  app/data/store.py              # pandas-backed CSV reads
```

**Patterns to follow**

- **Data fetching** belongs in `services/api.js`; components call the service in `useEffect` with a
  `cancelled` flag. Do not `fetch` directly from a component (the legacy
  `AccountPageViewModel.jsx` is the one exception — do not copy it).
- **Enums and visual metadata** belong in `frontend/src/constants/categories.js`.
- **Server data shape** comes from `backend/app/schemas/*.py`; never reshape it in CSS/JSX beyond
  display formatting.
- **Formatting** uses local `Intl.NumberFormat` instances (`CategoryCard.jsx`,
  `AccountDetails.jsx`). There is no shared formatter; keep new formatting local unless you are
  explicitly refactoring.
- **Pages** are composed in `App.jsx`; there is no route table today.

---

## 2. Figma MCP workflow rules

### 2.1 Authoring the Figma side (when pushing code → design)

**Target file:** [Finance Dashboard Design System](https://www.figma.com/design/sCkuf8XLNVZcBTaJMoLNYU)
(file key `sCkuf8XLNVZcBTaJMoLNYU`). The `Color` collection is already authored with `Light`/`Dark`
modes and the 12 variables in the table below; update it in place rather than creating a new collection.

1. Parse the URL: `figma.com/design/:fileKey/:name?node-id=:nodeId` → `nodeId` uses `:` not `-`;
   branches use `branchKey` as `fileKey`; FigJam uses `board/` + `get_figjam`.
2. Call `create_session` with the `fileKey` and a concise task description **before** any file tool.
3. Call `search_design_system` first, then `get_libraries`. Reuse published components/variables;
   do not recreate the card/taskbar/picker from scratch.
4. Load the `/figma-use` skill before `use_figma`.
5. Author variables with **exactly these names and Light/Dark modes**:

   | Figma variable | CSS token | Light | Dark |
   | --- | --- | --- | --- |
   | `bg` | `--bg` | `#f4f6fa` | `#11151c` |
   | `surface` | `--surface` | `#ffffff` | `#1a2029` |
   | `border` | `--border` | `#e3e7ef` | `#2a323f` |
   | `text` | `--text` | `#1b2230` | `#e6e9ef` |
   | `muted` | `--muted` | `#667085` | `#9aa4b2` |
   | `primary` | `--primary` | `#3b5bdb` | `#5c7cfa` |
   | `income` | `--income` | `#2f9e44` | `#2f9e44` |
   | `savings` | `--savings` | `#1c7ed6` | `#1c7ed6` |
   | `expenses` | `--expenses` | `#e8590c` | `#e8590c` |
   | `investments` | `--investments` | `#7048e8` | `#7048e8` |
   | `positive` | `--positive` | `#2f9e44` | `#2f9e44` |
   | `negative` | `--negative` | `#e03131` | `#e03131` |

6. Mirror the component inventory in §1.2: `Taskbar`, `AccountPicker`, `CategoryCard`, `AiInsights`,
   `AccountDetails`, `Dashboard`. Use the same state names (`is-active`, `is-open`, `is-invalid`,
   `is-selected`, `up/down/flat`) so design and code vocabulary match.

#### 2.1.1 Authored Figma library (current state)

**File:** [Finance Dashboard Design System](https://www.figma.com/design/sCkuf8XLNVZcBTaJMoLNYU)
(file key `sCkuf8XLNVZcBTaJMoLNYU`).

**Pages**

| Page | Node ID | Contents |
| --- | --- | --- |
| `Foundations` | `0:1` | `Color Tokens` specimen (`6:464`): 12 tokens × Light/Dark swatches, bound to the `Color` collection |
| `Components` | `2:2` | Component sets and `AccountDetails` (table below) |
| `Screens` | `2:3` | `Dashboard / Light` (`6:2`) and `Dashboard / Dark` (`6:291`), both 1100 px wide |

**Component sets** (all fills, strokes, and text colors are bound to the `Color` variables; the only
raw paint is `#fff` on `--primary` buttons, matching code)

| Set / component | Node ID | Variants | Mirrors |
| --- | --- | --- | --- |
| `ModeToggle` | `3:14` | `Mode=Current`, `Mode=Plan` | `.taskbar__actions` + `.taskbar__btn` |
| `AccountPicker` | `3:46` | `State=Closed`, `State=Open`, `State=Invalid` | `.picker` (menu uses `Shadow/Menu`) |
| `Taskbar` | `3:77` | `Mode=Current`, `Mode=Plan` | `.taskbar` (composes picker + toggle instances) |
| `CategoryCard` | `3:186` | `Category={Income,Savings,Expenses,Investments}` × `Trend={Up,Down,Flat}` = 12 | `.card`, accent top rule, 14% icon tint |
| `AiInsights` | `3:226` | `State=Default`, `State=Loading`, `State=Error`, `State=Result` | `.ai` |
| `DetailsSection` | `3:298` | `Type=Fields`, `Type=Table`; text properties `Title` + `Count` | `.details__section` / `.details__fields` / `.details__table` |
| `AccountDetails` | `3:410` | single component (Account Fields + Transactions Table) | `.details` |

`DetailsSection` exposes `Title` and `Count` text properties; `Type=Table` uses both, while
`Type=Fields` uses only `Title`. Override them on instances (e.g. `AccountDetails` sets the table to
`Transactions` / `50 of 240`) instead of detaching or editing the main component.

**Effect style:** `Shadow/Menu` (`S:39a98233780ca2c96201328cf05d8be634953abe,`) =
`0 12px 28px rgba(15, 23, 42, 0.18)`, applied to the open picker menu only.

**Theming:** `Dashboard / Dark` sets an explicit `Dark` mode override on the `Color` collection, so
the screen previews the same tokens the `prefers-color-scheme: dark` block produces in code. Do not
add per-node dark colors to the components; keep them bound to the variables.

**Typography caveat:** the Figma file uses Inter (Figma's default UI family) as a neutral stand-in for
the code's `system-ui, -apple-system, "Segoe UI", Roboto, sans-serif` stack. This is a design-file
approximation only. Do **not** translate Inter into CSS or add a font dependency (§1.4, §7.13).

**Updating the library:** edit the variant components inside their sets (not detached copies), then
refresh the `Screens` instances. Keep set names, variant property names, and node descriptions intact
so design↔code vocabulary stays aligned with §1.2.

### 2.2 Reading a design into code (design → code)

1. Call `create_session` with the `fileKey` and a concise task description.
2. Load the `/figma-design-to-code` skill **before** `get_design_context` (mandatory).
3. Call `get_design_context` with the target `nodeId` and `fileKey` — treat output as a
   **reference**, not final code. Use `get_screenshot` for the visual target and `get_metadata` for
   structure/layer names.
4. Build a mapping table before writing code:

   | Figma layer | Code target | Action |
   | --- | --- | --- |
   | Card frame | `components/CategoryCard/CategoryCard.jsx` | extend props/classes |
   | Mode toggle | `components/Taskbar/Taskbar.jsx` | reuse `taskbar__btn` + `is-active` |
   | Account dropdown | `components/AccountPicker/AccountPicker.jsx` | reuse combobox states |
   | Section panel | `details__section` / `.ai` / `.card` | reuse surface recipe |
   | New visual with no match | new `components/<Name>/` pair | create, then document here |

5. Replace every Figma color with the matching `var(--token)`. Replace spacing/radii/font sizes with
   the literal values from the scale in §1.1 (round to the nearest existing value; do not add a new
   value for a one-off).
6. Reuse existing class recipes instead of duplicating CSS:
   - **Panel:** `padding: 20px; background: var(--surface); border: 1px solid var(--border);
     border-radius: 12px;`
   - **Accent panel:** the panel recipe + `border-top: 4px solid var(--accent);`
   - **Muted label:** `font-size: 0.75rem; color: var(--muted);`
   - **Numeric cell:** `text-align: right; font-variant-numeric: tabular-nums;`
   - **Table:** `.details__table` inside `.details__table-wrap` (`overflow-x: auto`).
7. Run `npm run build` in `frontend/`. Then run the dev server and compare against the screenshot.
8. If the design changes behavior (new data, new state), update the relevant schema/store **only if
   the task asks**; otherwise adapt the design to existing data.

### 2.3 Hard "never" list for Figma-driven changes

- Never add Tailwind, PostCSS plugins, Sass, CSS Modules, styled-components, Emotion, Radix, shadcn,
  MUI, Chakra, Framer Motion, lucide/heroicons, or any icon/font package.
- Never add a `public/` directory, external image URLs, or a CDN.
- Never introduce TypeScript or `.tsx` files; the project is `.jsx`.
- Never introduce a theme provider, `data-theme` attribute, or class-based dark mode; dark mode is
  `prefers-color-scheme` in `global.css`.
- Never create a second styling system (e.g. inline-style objects for layout). Inline styles are
  reserved for the data-driven `--accent` custom property.
- Never rename existing classes, files, props, or tokens to match Figma layer names.
- Never edit `frontend/dist/` or `backend/app/data/*.csv` as part of a design task.
- Never "fix" the backend-offline fallback by hardcoding figures; zeroed fallback cards are
  intentional (`FALLBACK_CATEGORIES` + "Backend offline" notice).

---

## 3. Component creation template

When (and only when) no existing component fits:

```
frontend/src/components/<Name>/
  <Name>.jsx
  <Name>.css
```

```jsx
// frontend/src/components/Example/Example.jsx
import "./Example.css";

export default function Example({ title, children }) {
  return (
    <section className="example">
      <h2 className="example__title">{title}</h2>
      {children}
    </section>
  );
}
```

```css
/* frontend/src/components/Example/Example.css */
.example {
  padding: 20px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
}

.example__title {
  margin: 0 0 12px;
  font-size: 1.1rem;
}

@media (max-width: 720px) {
  /* only if the layout genuinely needs a mobile override */
}
```

Rules for new components:
- Default export; named local subcomponents stay private in the same file.
- Props are plain data + callbacks; no context, no render props.
- All colors via `var(--token)`; all surfaces use the panel recipe.
- Add a row to the inventory table in §1.2 in the same change.
- If the component introduces a new semantic color, add it to `:root` (and the dark block) in
  `global.css` and to the Figma variable table in §2.1.

---

## 4. Data-driven UI contract (do not break)

The four category keys and two modes are duplicated across three layers. Any design that adds,
renames, or removes one must update all of them:

1. `backend/app/schemas/dashboard.py` — `Mode = Literal["current", "plan"]`,
   `Category.key = Literal["income", "savings", "expenses", "investments"]`.
2. `frontend/src/constants/categories.js` — `MODES`, `CATEGORY_META`, `FALLBACK_CATEGORIES`.
3. `frontend/src/styles/global.css` — `--income`, `--savings`, `--expenses`, `--investments`.

Dashboard API shapes used by the UI:

```jsonc
// GET /api/dashboard/current?account_id=1
{
  "mode": "current",
  "account_id": 1,
  "month": "YYYY-MM",
  "categories": [
    { "key": "income", "title": "Income", "amount": 12345.0, "change": 2.4 }
  ]
}
```

`AccountDetails` consumes `AccountDetail` from `backend/app/schemas/accounts.py`
(`account`, `district`, `clients[].cards`, `loans`, `standing_orders`, `monthly_summary`,
`transactions`). `transactions` is a page: `{ total, offset, limit, items }`.

If a Figma design shows a field that does not exist in these schemas, either omit it or raise the
data change explicitly — do not fabricate it in the frontend.

---

## 5. Responsive & accessibility rules

- Breakpoint: `max-width: 720px`. Two-column grids collapse to one; `.ai__form` stacks.
  Everything else relies on `flex-wrap`, `minmax()`, and `overflow-x: auto` for tables.
- Container width: `1100px` max, `24px` horizontal padding (`global.css`).
- Interactive elements are native `<button>` / `<input>`; do not replace them with divs.
- Preserve existing ARIA: `aria-pressed` on mode buttons, `role="combobox"` + `aria-expanded` +
  `aria-controls` + `aria-activedescendant` on the account input, `role="listbox"`/`role="option"` +
  `aria-selected` on the menu.
- Decorative glyphs: `aria-hidden="true"`. Inputs keep their `<label htmlFor>`.
- Loading states use text (`Loading…`, `Thinking…`) and `disabled`; errors use `--negative`.
- Do not remove focus outlines. New interactive components need a visible focus style using
  `var(--primary)`.

---

## 6. Verification checklist

Run from `frontend/`:

```sh
npm run build     # the only automated check; must pass
npm run dev       # http://localhost:5173 (use localhost, not 127.0.0.1 — CORS)
```

Backend (from `backend/`, if the design needs real data):

```sh
.venv/bin/python run.py   # http://127.0.0.1:8000
```

Manual checks after implementing a Figma frame:
- [ ] Every color resolves to an existing `var(--token)`; no new hex values.
- [ ] Dark mode (OS setting) still looks correct; no invisible text or borders.
- [ ] Layout collapses cleanly at ≤720px.
- [ ] All four category cards still render, including the offline fallback (stop the backend).
- [ ] Account picker still opens on click/focus and supports Arrow/Enter/Escape.
- [ ] Tables scroll horizontally instead of breaking the layout.
- [ ] `npm run build` succeeds.
- [ ] New component/state names were added to §1.2; new tokens to §1.1/§2.1.

---

## 7. Known pitfalls in this repo

1. **`AccountDashboard` is legacy and not mounted.** `App.jsx` never renders it and never sets up
   `react-router`, despite the dependency. Its expected data (`owners`, `cards` at top level) does
   not match the current `AccountDetail` schema (`clients[].cards`). Do not use it as a reference.
2. **`react-router` is installed but unused** in the live tree. Do not add routes just to place a
   design; extend `App.jsx` or the relevant page instead.
3. **Stale CSS:** `.card__body` still exists in `CategoryCard.css` (lines 52–57) but the element was
   removed from `CategoryCard.jsx`. Do not resurrect it unless the design calls for a card body area.
4. **Dark mode is partial by design:** only the six neutral/brand tokens change. Semantic colors
   (`--income`, `--savings`, `--expenses`, `--investments`, `--positive`, `--negative`) stay the same.
5. **`backend/app/schemas/account.py` is legacy/unused.** The live models are in
   `backend/app/schemas/accounts.py` (note the plural).
6. **`backend/app/main.py` includes the accounts router twice** (lines 33 and 36). It is harmless
   duplicate route registration; don't copy the pattern.
7. **`frontend/dist/` exists locally but is gitignored.** It is stale build output. Never edit it
   or use it as source.
8. **CORS allows only `http://localhost:5173`.** Open the app at `localhost`, not `127.0.0.1`.
9. **No tests, lint, or typecheck.** `npm run build` is the only gate. Do not claim a check ran if it
   doesn't exist.
10. **All-zero cards are usually not a UI bug.** The frontend intentionally falls back to zeroed
    `FALLBACK_CATEGORIES` when the backend is offline.
11. **`--accent` is inline and data-driven.** If you add an accent-colored surface, set
    `style={{ "--accent": ... }}`; don't create a global `--accent`.
12. **Formatting is duplicated inline** (`Intl.NumberFormat` in `CategoryCard.jsx` and
    `AccountDetails.jsx`). Keep new formatting local unless the task is a refactor.
13. **No custom fonts.** Any Figma typography using a non-system family is a design-system change;
    flag it rather than silently adding a font.
