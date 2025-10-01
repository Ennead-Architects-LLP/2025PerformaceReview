## Feature Proposal: Click-to-Enlarge Employee Card in Overlay Modal (Letter-Size Export)

### Summary
Add a click-to-enlarge interaction to the existing employee card without changing its current design. Clicking a card opens a full-screen overlay modal that shows a new, print-friendly layout sized to a letter aspect ratio for export. The modal content is dedicated to detailed information and is optimized for exporting each employee to files/folders.

### Goals
- Preserve current employee card design and layout as-is.
- Add minimal, non-invasive hooks to trigger a modal overlay on click.
- Render a new detailed layout inside the modal that adheres to a letter-size ratio (portrait by default).
- Enable exporting modal views for all employees to files organized in folders.
- Keep changes minimal, debuggable, and easy to toggle on/off.

### Clarification Questions
- Interaction scope: Should the click target be the entire card or a specific button/icon on the card?
- Modal layout: Portrait letter (8.5×11) only, or support landscape too?
- Export format: Do you want image files (PNG/JPG), PDF, or printable HTML saved per employee?
- Export destination: Single folder per run, or one subfolder per department/employee?
- File naming: Preferred convention (e.g., "Lastname_Firstname_2025.pdf")?
- Data content: Should modal show exactly the same fields as the card plus extras, or a separate curated set?
- Branding: Any headers/footers, logos, or page numbers required in the modal/export?
- Trigger context: Should the modal also be accessible from the GUI app, or only in the generated HTML?
- Performance: Typical number of employees per export run (to estimate batching and progress feedback)?
- Toggle: Should we gate the feature behind a config flag (default on/off)?

### Minimal-Edit Plan
- Do not alter existing card markup/styles; only add a small clickable hook.
- Inject or append a modal container at the end of the HTML with a new detailed layout template.
- Add minimal CSS for overlay/backdrop and a letter-size content container using a fixed aspect ratio and print rules.
- Add lightweight JS handlers to:
  - Open modal on card click; load the corresponding employee details into the modal.
  - Close modal via backdrop click or close button; prevent scroll bleed.
- Add an export routine to render/save the modal layout for each employee to files.
- Add a config flag to enable modal and export features without affecting existing flows.
- Add concise debug logs around open/close and export operations.

### Proposed Action Items (Minimal Edits)
- HTML: Add a `data-employee-id` attribute and a small clickable element on each existing card.
- HTML: Append a single modal container with a dedicated detailed layout section.
- CSS: Add overlay/backdrop rules and a `.letter-page` container sized to letter ratio; include `@media print` rules if needed.
- JS: Add open/close handlers and dynamic content population by employee id.
- Python (generator): Gate modal injection and export via `config.py` flag; keep current generation intact.
- Python (export): Add an export step to iterate employees and save the modal layout per employee.
- Logging: Emit debug logs for modal lifecycle and export progress/errors.

### Technical Touchpoints (anticipated)
- app/html_generator.py: Inject modal markup and card hooks (data attributes) when feature flag is enabled.
- docs/css/styles.css (or injected styles): Minimal overlay and letter sizing rules.
- docs/js/script.js (or injected script): Click handlers and content population.
- app/config.py: Feature flag(s) for `ENABLE_ENLARGE_MODAL` and `EXPORT_MODAL_VIEWS`.
- app/orchestrator.py (or similar): Conditional export routine and progress reporting.

### Export Details
- Letter sizing: Use a fixed ratio container (e.g., 816×1056 CSS px for 96dpi) or `@page size: letter` for print/PDF workflows.
- Naming: Default to `Lastname_Firstname_2025.[ext]` unless otherwise specified.
- Structure: `OUTPUT/LetterExports/<Department>/<Lastname_Firstname>/` or a single flat folder per your preference.

### Risks/Considerations
- Performance for large batches; we may need debounced rendering and progress bars.
- Image assets must scale crisply within letter layout; consider higher-res logos.
- Accessibility: Focus trap inside modal and keyboard close (Esc) if feasible.
- Browser differences if viewed outside packaged app.

### Open Decisions (please answer)
1. Click target: entire card vs a small "View Details" button?
2. Orientation: portrait only, or both portrait/landscape?
3. Export format: PDF vs PNG/JPG vs HTML?
4. Folder strategy and file naming convention?
5. Exact fields/sections in the detailed modal layout?
6. Branding elements (logo, footer, page numbers)?
7. Default state for the feature flag (on/off)?

### Next Steps
After your answers, I'll finalize the implementation plan and start with minimal edits touching `html_generator.py`, `styles.css`, and `script.js`, then wire the export path and config toggle.


