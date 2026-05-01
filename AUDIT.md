# API Coverage Audit

How to verify, end-to-end, that every input the v23 Google Ads API accepts is exposed by some wrapper method in this codebase.

The deliverable is [`API_COVERAGE.md`](API_COVERAGE.md) — auto-generated, checked-in, one section per resource showing per-field ✅/❌ against the published v23 RPC reference.

## TL;DR

```bash
uv run python tools/audit_coverage.py            # uses cached markdown
uv run python tools/audit_coverage.py --refresh  # re-fetch every page
```

Read `API_COVERAGE.md` from the top: the **Summary** block tells you the headline numbers (settable / immutable / required coverage). Each per-resource section ends with a **Gaps:** list — those are the fields the wrapper does not currently expose.

## Why a tool, not a manual review

113 services × dozens of fields each is too large to review by hand and impossible to keep current as the SDK evolves. The audit tool is deterministic, re-runnable, and can be wired into CI. The MD report is the human-readable artifact a reviewer can scan in a few minutes.

## Source of truth

Every reference page on the v23 RPC docs has a clean markdown sibling at:

```
https://developers.google.com/google-ads/api/reference/rpc/v23/<Name>.md.txt
```

Examples:

- Overview (lists every Service): https://developers.google.com/google-ads/api/reference/rpc/v23/overview.md.txt
- Resource page: https://developers.google.com/google-ads/api/reference/rpc/v23/Customer.md.txt
- Service page: https://developers.google.com/google-ads/api/reference/rpc/v23/CustomerService.md.txt

These pages are generated from the same `.proto` files Google publishes, so they are authoritative for field names, types, and annotations (`Output only.`, `Immutable.`, `Required.`, `Input only.`, or unannotated = settable). We use the Markdown variant rather than the HTML page because the HTML is JavaScript-rendered and unparseable from a script; the `.md.txt` is plain text generated server-side.

The local Python SDK (`google-ads==30.0.0`) carries the same annotations as docstring text inside each `proto-plus` Message subclass, so SDK introspection would give identical field-level data — but the `.md.txt` is the canonical published spec, and that is what the audit consults.

## Methodology

The tool does five things per run:

### 1. Enumerate Services from the overview

`fetch_md("overview")` pulls the overview markdown. Service rows look like:

```markdown
| [`AccountBudgetProposalService`](.../v23/AccountBudgetProposalService) | description |
```

A regex extracts every `Service` name. The current overview returns 111 services.

### 2. Map Service → Resource

By convention `<Resource>Service` manages `<Resource>` (e.g. `CampaignBudgetService` → `CampaignBudget`). Edge cases live in `SERVICE_TO_RESOURCE_OVERRIDES` inside `tools/audit_coverage.py`. Services that don't map cleanly to a single resource (query-only, suggestion, upload, manager) are listed in `NO_RESOURCE_SERVICES` and skipped — they get a "no resource (query-only / suggestion / upload service)" line in the report.

### 3. Parse the resource's field table

For each resource, fetch `<Resource>.md.txt` and find the `| Fields ||` table header. Every field row is shaped:

```markdown
| ## `field_name` | `type-or-link` Description starting with annotation |
```

`parse_resource_fields` extracts `(name, type_, description)` per row and classifies each field by the leading sentence of the description:

- `Output only.` → `output_only` (skipped — read-only fields)
- `Immutable.` → `immutable` (settable on create only)
- `Required.` → `required`
- `Input only.` → `input_only`
- Otherwise → `settable`

`Required. Immutable.` is a pattern that means "must be provided on create, can't be changed afterward." That gets classified as `immutable`.

### 4. Map Resource → wrapper file and AST-walk every method

`find_wrapper_file` looks under `src/services/` for a file matching the resource's snake_case (`CustomerSkAdNetworkConversionValueSchema` → `customer_sk_ad_network_service.py`). Aliases handle legitimate naming mismatches (`CampaignBudget` → `budget_service.py`, `Ad` → `ad_service.py`, `ConversionAction` → `conversion_service.py`, `YouTubeVideoUpload` → `youtube_video_upload_service.py`).

`collect_wrappers` parses the file with `ast` and walks every `async def` whose name does NOT start with one of `list_`, `search_`, `get_`, `register_`, `_`, `remove_`. For each method it collects:

- **Params** — every positional and keyword-only argument name.
- **Writes** — every `obj.foo.bar = ...` assignment target as a dotted path, plus every `obj.foo.append(...)` / `extend(...)` / `MergeFrom(...)` / `CopyFrom(...)` / `add(...)` call target. The dotted paths are the audit's signal for "this method touched this proto attribute."

### 5. Score coverage per field

A field is considered "covered" by a method if the field name appears in the method's params *or* as a path segment in any of its writes. Python-keyword aliases are normalized: proto field `type` matches wrapper param `type_`.

Special handling:

- `resource_name` and `id` are auto-covered as **structural** identifiers (the operation framework handles them; they are never user-facing wrapper params per se).
- `INTENTIONAL_NON_EXPOSURE` registers per-resource fields that are intentionally not exposed even though the proto says they're settable. Currently:
  - `KeywordPlanCampaignKeyword.negative`, `SharedCriterion.negative`, `CustomerNegativeCriterion.negative` — Phase 9.1 hardcoded `negative=True` on dedicated negative-only methods.

If you find a real "intentionally not exposed" case during triage, add it to `INTENTIONAL_NON_EXPOSURE` with a one-line reason. That keeps the coverage number honest without polluting the gap list.

## Reading `API_COVERAGE.md`

Each per-service section looks like:

```markdown
## CustomerService
- Resource: `Customer`
- Wrapper: `src/services/account/customer_service.py`

| Field | Status | Covered by |
|---|---|---|
| `currency_code` 🔒 | ✅ | create_customer_client |
| `tracking_url_template` ✏️ | ✅ | mutate_customer |
| `video_customer` ✏️ | ❌ |  |
...

**Gaps:**
- ✏️ `video_customer` — settable
```

Legend (also rendered at the top of the report):

- ✏️ settable · 🔒 immutable (create-only) · ❗ required · 📥 input-only · 🚫 output-only (skipped)
- ✅ exposed by wrapper · ❌ gap

## Triaging gaps

Most ❌ rows are real gaps to fix. A few patterns are false positives that need handling:

**1. Wrapper uses a different param name than the proto field.**
For example, `asset_set_type` in the wrapper that converts to `AssetSet.type_`. The audit can't follow `getattr(...)` indirection. If the gap is genuinely covered, either rename the wrapper param to match the proto, or add the field to `INTENTIONAL_NON_EXPOSURE`. Renaming is preferred when reasonable.

**2. The wrapper method has an unrecognized prefix.**
`collect_wrappers` accepts `create_` / `update_` / `mutate_` / `add_` / `link_`. If you add a verb (e.g. `attach_`, `apply_`), update `SKIP_PREFIXES` (the inverse list) in `tools/audit_coverage.py` so the new methods are scanned.

**3. The proto field is reachable via a oneof and the audit can't infer the discriminator.**
Example: `Ad.text_ad`, `Ad.image_ad`, `Ad.hotel_ad`, etc. are members of a oneof, and each `create_<type>_ad` method targets exactly one. The audit will flag the unused ones on every method. This is a known limitation; document it in the gap callout (the report already calls these out structurally) and move on.

**4. A whole service is missing.**
Two cases on the 2026-05-01 baseline: `CampaignLifecycleGoalService` and `CustomerLifecycleGoalService`. The report flags these explicitly with `❌ **No wrapper file found**`. They need wrappers built from scratch.

## Adding/extending suppressions

When you decide a field is intentionally not exposed, edit `tools/audit_coverage.py`:

```python
INTENTIONAL_NON_EXPOSURE: dict[str, dict[str, str]] = {
    "<ResourceName>": {
        "<field_name>": "Reason — link to phase / commit / decision.",
    },
    ...
}
```

The reason string is shown in the report's `Covered by` column so the suppression is auditable. **Never silently suppress without a reason.**

For new naming aliases (resource ↔ wrapper file mismatches), edit `find_wrapper_file`'s `aliases` dict:

```python
aliases: dict[str, list[str]] = {
    "campaign_budget": ["budget_service.py"],
    ...
}
```

For Service overrides (when `<Resource>Service` doesn't strip cleanly to `<Resource>`), edit `SERVICE_TO_RESOURCE_OVERRIDES`.

For services with no underlying resource (query-only, etc.), add to `NO_RESOURCE_SERVICES`.

## When to re-run

- After adding/removing a settable field on any wrapper method.
- After upgrading the `google-ads` SDK to a new minor version (Google can add new fields).
- Before tagging a release.
- In CI, ideally as a non-blocking informational step at first, then as a gate once coverage is high.

If the cache is stale and the SDK has changed shape, run with `--refresh` to force re-fetch. The cache lives at `tools/.audit_cache/` and is gitignored.

## Limits and known gaps

- **Heuristic match.** A field name appearing as a path segment is enough to count as "covered." A wrapper that takes `foo` as a param but never actually wires it to the request will be marked ✅ — the audit cannot verify *correctness*, only *exposure*. Tests catch the second half.
- **Markdown format dependency.** If Google changes the field-table markup, `_FIELD_ROW_RE` will need updating. The regex pattern is documented at the top of `tools/audit_coverage.py`.
- **Submessage fields are listed as a single entry.** `Campaign.shopping_setting` is one row in the report; whether the wrapper exposes every field *inside* `ShoppingSetting` is not recursively checked. Submessage gaps are treated as "the parent field isn't exposed, so the whole submessage is uncovered." Recursive-submessage auditing is future work.
- **Per-method coverage is aggregated.** A field is covered if *any* eligible method touches it. A wrapper that exposes a field on `create_*` but not on `update_*` is reported as covered — partial coverage is invisible in the current report. Future iterations could split coverage per method type.

## See also

- [`tools/audit_coverage.py`](tools/audit_coverage.py) — the script.
- [`API_COVERAGE.md`](API_COVERAGE.md) — the latest run.
- [`API_PROGRESS.md`](API_PROGRESS.md) Phase 15 — context for why this exists and the follow-up gap-fix buckets.
- [`CLAUDE.md`](CLAUDE.md) — the project's rule that wrapper docstrings are the LLM-facing interface; this audit is the structural counterpart.
