# API Coverage Audit

How to verify, end-to-end, that every input the v23 Google Ads API accepts is exposed by some wrapper method in this codebase **and** every wrapper-tool docstring documents every parameter it takes.

The deliverable is [`API_COVERAGE.md`](API_COVERAGE.md) — auto-generated, one section per resource showing per-field ✅/❌ against the published v23 RPC reference, the wrapper method that exposes it, the registered MCP tool name, and source-of-truth agreement across three independent sources.

## TL;DR

```bash
uv run python tools/audit_coverage.py            # uses cached web sources
uv run python tools/audit_coverage.py --refresh  # re-fetch every page
```

Read `API_COVERAGE.md` from the top: the **Summary** block tells you the headline numbers (settable/immutable/required coverage, source disagreements, docstring coverage). Each per-resource section ends with a **Field gaps** list and a **Docstring gaps** list — those are the two work queues.

## Why a tool, not a manual review

113 services × dozens of fields each is too large to review by hand and impossible to keep current as the SDK evolves. The audit tool is deterministic, re-runnable, and idempotent. The MD report is the human-readable artifact a reviewer can scan in a few minutes.

## Three sources of truth

The audit cross-references every settable input against three independent sources, in order of preference:

1. **Devsite markdown** — `https://developers.google.com/google-ads/api/reference/rpc/v23/<Name>.md.txt`. The published reference rendered to Markdown. Authoritative for the user-facing field list and field annotations (`Output only.`, `Immutable.`, `Required.`, `Input only.`).
2. **Source proto** — `https://raw.githubusercontent.com/googleapis/googleapis/<ref>/google/ads/googleads/v23/resources/<snake>.proto`. The actual protobuf definition that generates the website and the SDK. Authoritative for `(google.api.field_behavior)` annotations.
3. **Local Python SDK** — `google.ads.googleads.v23.resources.types.<snake>`. The proto-plus class shipped in `google-ads==30.0.0`. Authoritative for what fields the SDK actually exposes (which is what our wrapper has access to).

If any of the three is missing the field, or the markdown annotation disagrees with the proto's `field_behavior`, the row is flagged as a **source disagreement** in the report. Disagreements indicate either a stale cache, a docs/proto bug, or our acronym/aliasing logic missing a case.

The script tolerates known equivalent annotations — e.g. `Input only.` + `Immutable.` is one combined behavior that the markdown and proto each pick a single representative for; the audit treats those as agreement.

### Version pinning

`googleapis/googleapis` ships every Google Ads version side-by-side under its own subdirectory (`google/ads/googleads/v22/`, `v23/`, `v24/`, …). The default audit ref is `master`, which keeps the v23 subdirectory current with whatever Google last patched. To pin against a frozen snapshot — e.g. when releasing — pass a commit SHA or tag:

```bash
uv run python tools/audit_coverage.py --proto-ref <commit-sha>
```

The cache key includes the ref, so cached protos from one ref don't pollute another's run.

**Version sanity check.** Every fetched `.proto` file has its `package google.ads.googleads.<version>.*` line verified to declare `v23`. If a fetch ever returns a different version (e.g. because Google ever moves or removes the v23 subdirectory), the audit raises `ProtoVersionMismatch` and aborts rather than silently producing a coverage report against the wrong version. The current state on master keeps `v22`, `v23`, and `v24` all present, so the default ref is safe today.

## What the audit produces (per resource)

```
## CustomerService

- **Resource**: `Customer`
- **Sources**: md ✅ · proto ✅ · sdk ✅
- **Wrapper file**: `src/services/account/customer_service.py`
- **MCP tools registered** (3): `create_customer_client`, `list_accessible_customers`, `mutate_customer`

### Fields

| Field | Annot. | Status | MCP tool(s) | Service method(s) | Sources | Description |
|---|---|---|---|---|---|---|
| `currency_code` | 🔒 | ✅ | `create_customer_client` | create_customer_client | agree | Immutable |
| `video_customer` | ✏️ | ❌ | — | — | agree | Video specific information about a Customer. |
…

**Field gaps:**
- ✏️ `video_customer` — settable: Video specific information about a Customer.

**Docstring gaps:**
- `mutate_customer` — missing: `partial_failure`, `response_content_type`, `validate_only`
```

Every column is filled in deterministically by the audit. The MCP tool list is parsed out of `register_<x>_tools` and the inner `create_<x>_tools` function. The Service method list is the AST-walked `async def` whose body writes to the proto field or whose param matches the field name. Docstring gaps are tool-wrapper params that don't appear in the docstring's `Args:` block.

## The pipeline

The tool does six things per run:

### 1. Enumerate Services from the overview

`fetch_devsite_md("overview")` pulls `<DEVSITE_BASE>/overview.md.txt`. Service rows look like:

```markdown
| [`AccountBudgetProposalService`](.../v23/AccountBudgetProposalService) | description |
```

A regex extracts every `Service` name. The current overview returns 111 services.

### 2. Map Service → Resource → wrapper file

By convention `<Resource>Service` manages `<Resource>` (e.g. `CampaignBudgetService` → `CampaignBudget`). Edge cases live in `SERVICE_TO_RESOURCE_OVERRIDES`. Services that don't map cleanly to a single resource (query-only, suggestion, upload, manager) are listed in `NO_RESOURCE_SERVICES` and skipped — they get an `_No resource_` line in the report.

`find_wrapper_file` looks under `src/services/` for a file matching the resource's snake_case (`CustomerSkAdNetworkConversionValueSchema` → `customer_sk_ad_network_service.py`). Aliases handle legitimate naming mismatches (`CampaignBudget` → `budget_service.py`, `Ad` → `ad_service.py`, `ConversionAction` → `conversion_service.py`, `YouTubeVideoUpload` → `youtube_video_upload_service.py`).

### 3. Pull the three sources

For each resource, in parallel:

- `fetch_devsite_md(resource)` → markdown body. `parse_devsite_fields` extracts every `| ## \`field_name\` | \`type\` Description |` row.
- `fetch_proto_source(resource)` → raw `.proto` text from the googleapis GitHub repo. `parse_proto_fields` walks the message body brace-aware (string- and comment-stripped, with `[...]` annotation tracking so braces inside annotations don't fool the depth counter) and extracts top-level fields plus `oneof` members.
- `load_sdk_class(resource)` + `sdk_field_names` → the set of field names exposed by the proto-plus class, with Python-keyword aliasing (`type` ↔ `type_`).

Both web sources are cached at `tools/.audit_cache/{devsite,proto}/`. Pass `--refresh` to ignore the cache.

### 4. Merge field sources

`merge_field_sources` uses the **markdown field list as authoritative for the inventory of settable inputs**. Proto and SDK are consulted to verify that every markdown field is also present in proto and SDK, and that their annotations agree. Fields in proto/sdk but not in markdown are not added — those would indicate a website lag and are tracked separately.

### 5. AST-walk wrappers + parse register_* for MCP tool names

`collect_wrappers` parses each service file with `ast` and walks every `async def` whose name doesn't start with `list_`, `search_`, `get_`, `register_`, `_`, or `remove_`. For each method it collects:

- **Params** — every positional and keyword-only argument name (minus `self` and `ctx`).
- **Writes** — every dotted attribute write (`obj.foo.bar = …`) and every repeated-field call (`obj.foo.append(...)`, `extend`, `MergeFrom`, `CopyFrom`, `add`).
- **Kind** — `tool` if the method is defined inside `create_*_tools`, else `service`.
- **Docstring args** — set of param names appearing in the docstring's `Args:` block.

`collect_mcp_tool_names` separately walks the `create_*_tools` function and returns the list of `async def` defined inside it — these are the FastMCP-registered tool names users see.

### 6. Score coverage and emit the report

For every markdown-listed field, find every wrapper method whose params or writes touch it. The coverage row records both the service method name(s) and the MCP tool name(s) — they're listed separately because tool wrappers and service methods often share names but live in different scopes. Auto-cover `resource_name` and `id` as **structural** identifiers (handled by the operation framework, not user-facing). `INTENTIONAL_NON_EXPOSURE` registers per-resource fields that are intentionally not exposed (e.g. `KeywordPlanCampaignKeyword.negative` is hardcoded True in Phase 9.1).

Docstring coverage scoring: for every tool wrapper, compute `(params - {self, ctx}) - documented_args` and report missing names in the **Docstring gaps** callout.

## Triaging gaps

Most ❌ rows are real gaps to fix. A few patterns are false positives that need handling:

**1. Wrapper uses a different param name than the proto field.**
For example, `asset_set_type` in the wrapper that converts to `AssetSet.type_`. The audit can't follow `getattr(...)` indirection. If the gap is genuinely covered, either rename the wrapper param to match the proto, or add the field to `INTENTIONAL_NON_EXPOSURE`. Renaming is preferred when reasonable.

**2. The wrapper method has an unrecognized prefix.**
`collect_wrappers` accepts everything except `list_` / `search_` / `get_` / `register_` / `_` / `remove_`. If you add a wrapper whose name starts with one of those (e.g. `_helper_*`), the audit will skip it. Update `SKIP_PREFIXES` if you genuinely add a new public verb.

**3. The proto field is reachable via a oneof and the audit can't infer the discriminator.**
Example: `Ad.text_ad`, `Ad.image_ad`, `Ad.hotel_ad`, etc. are members of a oneof, and each `create_<type>_ad` method targets exactly one. The audit will flag the unused ones on every method. This is a known limitation; document it in the gap callout.

**4. A whole service is missing.**
Two cases on the 2026-05-01 baseline: `CampaignLifecycleGoalService` and `CustomerLifecycleGoalService`. The report flags these explicitly with `❌ no file found — service is unimplemented`. They need wrappers built from scratch.

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

The reason string is shown in the report's Status column with the 🛡️ marker so the suppression is auditable. **Never silently suppress without a reason.**

For new naming aliases (resource ↔ wrapper file mismatches), edit `find_wrapper_file`'s `aliases` dict. For Service overrides (when `<Resource>Service` doesn't strip cleanly to `<Resource>`), edit `SERVICE_TO_RESOURCE_OVERRIDES`. For services with no underlying resource (query-only, etc.), add to `NO_RESOURCE_SERVICES`. For acronyms that don't follow normal snake_case (`YouTube`, `SkAd`), update `fetch_proto_source` and `load_sdk_class`'s acronym lists.

## Determinism

Same inputs → identical report bytes. The script writes no timestamps, run-counters, or environment-dependent data into `API_COVERAGE.md`. With `tools/.audit_cache/` populated, two runs on the same machine produce byte-identical output. With `--refresh`, output can drift only if Google has updated the published markdown, the source proto on `googleapis/googleapis@master`, or you've upgraded the local SDK.

For full reproducibility across machines, commit `tools/.audit_cache/` (currently gitignored — opt-in if you need that). For CI use the `--refresh` form to always check against the live reference.

## When to re-run

- After adding or removing a settable field on any wrapper method.
- After upgrading the `google-ads` SDK to a new minor version (Google can add new fields).
- Before tagging a release.
- In CI, ideally as a non-blocking informational step at first, then as a gate once coverage is high.

## Limits and known gaps

- **Heuristic match.** A field name appearing as a path segment in a write is enough to count as "covered." A wrapper that takes `foo` as a param but never actually wires it to the request will be marked ✅ — the audit cannot verify *correctness*, only *exposure*. Tests catch the second half.
- **No recursive submessage check.** `Campaign.shopping_setting` is one row; the audit does not descend into `ShoppingSetting`'s own fields. Submessage gaps are treated as "the parent field isn't exposed, so the whole submessage is uncovered." Recursive auditing is future work.
- **Per-method coverage is aggregated.** A field is covered if *any* eligible method touches it. A wrapper that exposes a field on `create_*` but not on `update_*` is reported as covered — partial coverage is invisible. Future iterations could split coverage per method type.
- **Markdown format dependency.** If Google changes the field-table markup, `_FIELD_ROW_RE` will need updating (documented at the top of `tools/audit_coverage.py`).
- **GitHub `master` dependency.** Default `--proto-ref` is `master`. The version sanity check catches accidental cross-version fetches; pin to a SHA via `--proto-ref` for full determinism across days.

## See also

- [`tools/audit_coverage.py`](tools/audit_coverage.py) — the script.
- [`API_COVERAGE.md`](API_COVERAGE.md) — the latest run.
- [`API_PROGRESS.md`](API_PROGRESS.md) Phase 15 — context for why this exists and the follow-up gap-fix buckets.
- [`CLAUDE.md`](CLAUDE.md) — the project's rule that wrapper docstrings are the LLM-facing interface; this audit is the structural counterpart.
