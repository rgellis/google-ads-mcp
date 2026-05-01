"""Compare every Google Ads v23 resource's published fields against our wrapper.

Source of truth: the official Google Ads v23 RPC reference markdown
(``https://developers.google.com/google-ads/api/reference/rpc/v23/<Name>.md.txt``).
For every resource, we parse the field table out of the published markdown,
classify each field by its leading annotation (``Output only.``, ``Immutable.``,
``Required.``, ``Input only.``, or unannotated = settable), and check whether
our wrapper exposes it.

For each Service in the overview:

  - identify the resource it manages (``<Resource>Service`` → ``<Resource>``)
  - resolve the wrapper file (``src/services/**/*_service.py`` matching the
    resource name) and AST-walk every ``async def create_*``/``update_*``/
    ``mutate_*`` method to collect (a) parameter names and (b) attribute
    write paths into the proto resource
  - for each field on the resource, decide whether it's covered by any
    method's params or writes
  - record a row: resource, field, annotation, methods that cover it,
    methods that should but don't

The result is written to API_COVERAGE.md at the repo root, with one section
per resource. Re-run the script to refresh the report.

Caching: fetched markdown is cached at ``tools/.audit_cache/`` so repeated
runs are fast and offline-friendly. Pass ``--refresh`` to force re-fetch.
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parent.parent
SERVICES_DIR = REPO_ROOT / "src" / "services"
CACHE_DIR = Path(__file__).resolve().parent / ".audit_cache"
REPORT_PATH = REPO_ROOT / "API_COVERAGE.md"

V23_BASE = "https://developers.google.com/google-ads/api/reference/rpc/v23"
USER_AGENT = "Mozilla/5.0 (audit_coverage.py)"

# Services we don't expect to map cleanly onto a single resource — they're
# either query-only, span multiple resources, or wrap RPCs we model differently.
NO_RESOURCE_SERVICES = {
    "GoogleAdsService",  # query/search
    "GoogleAdsFieldService",  # metadata
    "KeywordPlanIdeaService",
    "ReachPlanService",
    "TravelAssetSuggestionService",
    "AudienceInsightsService",
    "ContentCreatorInsightsService",
    "BenchmarksService",
    "BrandSuggestionService",
    "SmartCampaignSuggestService",
    "ShareablePreviewService",
    "PaymentsAccountService",
    "InvoiceService",
    "GeoTargetConstantService",
    "KeywordThemeConstantService",
    "IdentityVerificationService",
    "AssetGenerationService",
    "AutomaticallyCreatedAssetRemovalService",
    "ReservationService",
    "IncentiveService",
    "DataLinkService",
    # Linkages — managed by us but the field-level audit on them is
    # a single-link entity (resource_name only) and not informative.
    "AdGroupAdLabelService",
    "AdGroupCriterionLabelService",
    "AdGroupLabelService",
    "CampaignLabelService",
    "CustomerLabelService",
}

# Some Service names don't strip cleanly to a Resource. Override here.
SERVICE_TO_RESOURCE_OVERRIDES: dict[str, str] = {
    "AdService": "Ad",
    "BiddingStrategyService": "BiddingStrategy",
    "CampaignBudgetService": "CampaignBudget",
    "CustomerSkAdNetworkConversionValueSchemaService": "CustomerSkAdNetworkConversionValueSchema",
    "OfflineUserDataJobService": "OfflineUserDataJob",
    "ConversionUploadService": "",  # uploads, not mutate
    "ConversionAdjustmentUploadService": "",
    "UserDataService": "",
    "RecommendationService": "Recommendation",
    "BatchJobService": "BatchJob",
    "GoalService": "Goal",
}


# --------------------------------------------------------------------------- #
# Fetch + cache                                                               #
# --------------------------------------------------------------------------- #


def cache_path_for(name: str) -> Path:
    safe = name.replace("/", "_")
    return CACHE_DIR / f"{safe}.md"


def fetch_md(name: str, *, refresh: bool = False) -> str | None:
    """Return the markdown for ``<V23_BASE>/<name>.md.txt``, or None on 404."""
    cp = cache_path_for(name)
    if cp.exists() and not refresh:
        return cp.read_text()
    url = f"{V23_BASE}/{name}.md.txt"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cp.write_text(body)
    # be polite
    time.sleep(0.05)
    return body


# --------------------------------------------------------------------------- #
# Parse markdown                                                              #
# --------------------------------------------------------------------------- #


# Service overview: rows look like
#   | [`AccountBudgetProposalService`](...) | description |
_SERVICE_ROW_RE = re.compile(r"^\| \[`(\w+Service)`\]")

# Field table row in a resource page:
#   | ## `field_name` | `type-or-link` Description starting with annotation |
_FIELD_ROW_RE = re.compile(r"^\| ## `(\w+)` \| (.*?) \|\s*$")


def list_services(refresh: bool = False) -> list[str]:
    md = fetch_md("overview", refresh=refresh)
    assert md is not None, "Failed to fetch overview"
    services = []
    for line in md.splitlines():
        m = _SERVICE_ROW_RE.match(line)
        if m:
            services.append(m.group(1))
    return services


@dataclass
class ProtoField:
    name: str
    type_: str  # human-readable, possibly a URL to a sub-message
    annotation: str  # one of: settable, output_only, immutable, required, input_only
    required: bool  # additionally true when description starts with "Required."
    raw: str  # full description text


def parse_resource_fields(md: str) -> list[ProtoField]:
    """Parse the field table from a resource's markdown body."""
    out = []
    in_field_table = False
    for line in md.splitlines():
        if line.startswith("| Fields ||"):
            in_field_table = True
            continue
        if not in_field_table:
            continue
        if line.startswith("|---") or line.strip() == "":
            # delimiter or end of table; tables usually end before next ##
            if line.strip() == "" or line.startswith("# "):
                # empty line is fine; only break on a heading
                if line.startswith("# "):
                    break
            continue
        m = _FIELD_ROW_RE.match(line)
        if not m:
            # could be the start of a different table or a heading
            if line.startswith("|") and "Fields" not in line:
                continue
            if line.startswith("#") or line.startswith("---"):
                break
            continue
        name = m.group(1)
        rest = m.group(2)
        # Type is the first backticked token.
        type_match = re.match(r"`([^`]+)`\s*(.*)", rest)
        if type_match:
            type_ = type_match.group(1)
            desc = type_match.group(2).strip()
        else:
            type_ = ""
            desc = rest
        annotation = _annotation_from_desc(desc)
        required = desc.startswith("Required.")
        out.append(
            ProtoField(
                name=name,
                type_=type_,
                annotation=annotation,
                required=required,
                raw=desc,
            )
        )
    return out


def _annotation_from_desc(desc: str) -> str:
    # Order matters: "Required. Immutable." should classify as immutable
    # (the field is required AND can only be set on create).
    if "Output only." in desc.split(".")[0:2]:
        return "output_only"
    if desc.startswith("Output only."):
        return "output_only"
    if desc.startswith("Input only."):
        return "input_only"
    if desc.startswith("Immutable."):
        return "immutable"
    if "Immutable." in desc[: desc.find(".") + 30]:
        # "Required. Immutable." pattern
        return "immutable"
    if desc.startswith("Required."):
        return "required"
    return "settable"


# --------------------------------------------------------------------------- #
# Wrapper introspection                                                       #
# --------------------------------------------------------------------------- #


@dataclass
class WrapperMethod:
    name: str
    file: Path
    params: set[str] = field(default_factory=set)
    writes: set[str] = field(default_factory=set)


def _attr_chain(node: ast.AST) -> str | None:
    parts: list[str] = []
    cur = node
    while isinstance(cur, ast.Attribute):
        parts.append(cur.attr)
        cur = cur.value
    if isinstance(cur, ast.Name):
        parts.append(cur.id)
        return ".".join(reversed(parts))
    return None


def collect_wrappers(file_path: Path) -> list[WrapperMethod]:
    src = file_path.read_text()
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return []
    out: list[WrapperMethod] = []
    # Read-only / metadata methods that don't represent user-facing input.
    SKIP_PREFIXES = ("list_", "search_", "get_", "register_", "_", "remove_")
    for node in ast.walk(tree):
        if not isinstance(node, ast.AsyncFunctionDef):
            continue
        if node.name.startswith(SKIP_PREFIXES):
            continue
        wm = WrapperMethod(name=node.name, file=file_path)
        wm.params = {a.arg for a in node.args.args} | {
            a.arg for a in node.args.kwonlyargs
        }
        for sub in ast.walk(node):
            for cand in (
                sub.targets
                if isinstance(sub, ast.Assign)
                else [sub.target]
                if isinstance(sub, ast.AugAssign)
                else []
            ):
                p = _attr_chain(cand)
                if p:
                    wm.writes.add(p)
            if isinstance(sub, ast.Call):
                if isinstance(sub.func, ast.Attribute) and sub.func.attr in (
                    "append",
                    "extend",
                    "MergeFrom",
                    "CopyFrom",
                    "add",
                ):
                    p = _attr_chain(sub.func.value)
                    if p:
                        wm.writes.add(p)
        out.append(wm)
    return out


def find_wrapper_file(resource: str) -> Path | None:
    """Find a service file whose name matches the resource snake_case."""
    snake = _snake(resource)
    # Acronym fixups: collapse "you_tube" → "youtube" and similar.
    snake_alt = snake.replace("you_tube", "youtube").replace("sk_ad", "skad")
    candidates: list[str] = []
    for s in (snake, snake_alt):
        candidates.extend([f"{s}_service.py", f"{s}.py"])
    # Aliased / shortened wrappers — Resource → service file basename.
    aliases: dict[str, list[str]] = {
        "campaign_budget": ["budget_service.py"],
        "ad": ["ad_service.py"],
        "customer_sk_ad_network_conversion_value_schema": [
            "customer_sk_ad_network_service.py"
        ],
        "you_tube_video_upload": ["youtube_video_upload_service.py"],
        "conversion_action": ["conversion_service.py"],
    }
    for basename in candidates + aliases.get(snake, []):
        for path in SERVICES_DIR.rglob(basename):
            return path
    return None


def _snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


# --------------------------------------------------------------------------- #
# Coverage scoring                                                            #
# --------------------------------------------------------------------------- #


@dataclass
class FieldCoverage:
    field_name: str
    annotation: str
    required: bool
    type_: str
    # methods that expose this field via param or write path
    covered_by: list[str] = field(default_factory=list)


# Identifier fields that don't belong in the coverage gap report:
# resource_name is the structural identifier (set on update/remove via param
# like ``<resource>_resource_name``); id is Output-only on every resource.
STRUCTURAL_FIELDS = {"resource_name", "id"}

# Per-resource fields that are intentionally NOT exposed as user-facing
# params, even though the proto marks them settable. Document the reason
# inline so the suppression is auditable.
INTENTIONAL_NON_EXPOSURE: dict[str, dict[str, str]] = {
    # Phase 9.1 — `negative` is hardcoded True on dedicated negative-only
    # add_* methods (placement, content_label, custom_audience, etc.).
    "KeywordPlanCampaignKeyword": {
        "negative": "Phase 9.1 — hardcoded True; this resource is negative-only."
    },
    "SharedCriterion": {
        "negative": "Phase 9.1 — hardcoded True for negative shared sets."
    },
    "CustomerNegativeCriterion": {
        "negative": "Phase 9.1 — resource is by definition negative.",
    },
}


def _wrapper_covers(field_name: str, wm: WrapperMethod) -> bool:
    """Heuristic match between a proto field name and a wrapper method.

    Handles Python-keyword aliases: proto ``type`` ↔ wrapper ``type_``.
    """
    candidates = {field_name}
    if field_name == "type":
        candidates.add("type_")
    if field_name in wm.params or candidates & wm.params:
        return True
    for w in wm.writes:
        segs = w.split(".")
        seg_set = set(segs)
        if candidates & seg_set:
            return True
    return False


def score_coverage(
    resource: str,
    fields: list[ProtoField],
    wrappers: list[WrapperMethod],
) -> list[FieldCoverage]:
    out: list[FieldCoverage] = []
    suppress = INTENTIONAL_NON_EXPOSURE.get(resource, {})
    for fld in fields:
        cov = FieldCoverage(
            field_name=fld.name,
            annotation=fld.annotation,
            required=fld.required,
            type_=fld.type_,
        )
        if fld.name in STRUCTURAL_FIELDS:
            cov.covered_by.append("(structural)")
            out.append(cov)
            continue
        if fld.name in suppress:
            cov.covered_by.append(f"(suppressed: {suppress[fld.name]})")
            out.append(cov)
            continue
        for wm in wrappers:
            if _wrapper_covers(fld.name, wm):
                cov.covered_by.append(wm.name)
        out.append(cov)
    return out


# --------------------------------------------------------------------------- #
# Report rendering                                                            #
# --------------------------------------------------------------------------- #


@dataclass
class ServiceReport:
    service: str
    resource: str
    wrapper_file: Path | None
    fields: list[FieldCoverage]
    fetch_error: str | None = None


def _resource_for_service(svc: str) -> str:
    if svc in SERVICE_TO_RESOURCE_OVERRIDES:
        return SERVICE_TO_RESOURCE_OVERRIDES[svc]
    if svc.endswith("Service"):
        return svc[: -len("Service")]
    return svc


def _emoji_for_annotation(annotation: str) -> str:
    return {
        "output_only": "🚫",  # not user-settable
        "immutable": "🔒",  # create-only
        "required": "❗",
        "input_only": "📥",
        "settable": "✏️",
    }.get(annotation, "?")


def render_report(reports: list[ServiceReport]) -> str:
    lines: list[str] = []
    lines.append("# API Coverage")
    lines.append("")
    lines.append(
        "Auto-generated by `tools/audit_coverage.py`. Do not hand-edit. "
        "Re-run the tool whenever the SDK or wrappers change."
    )
    lines.append("")
    lines.append("Source of truth: ")
    lines.append(
        "[Google Ads v23 RPC reference]"
        f"({V23_BASE}/overview) (one .md.txt per resource)."
    )
    lines.append("")

    # Summary
    total_fields = 0
    total_settable = 0
    total_settable_covered = 0
    total_immutable = 0
    total_immutable_covered = 0
    total_required = 0
    total_required_covered = 0
    skipped = 0
    no_wrapper = 0
    for r in reports:
        if r.fetch_error or not r.fields:
            skipped += 1
            continue
        if r.wrapper_file is None:
            no_wrapper += 1
        for fc in r.fields:
            total_fields += 1
            covered = bool(fc.covered_by)
            if fc.annotation == "settable":
                total_settable += 1
                if covered:
                    total_settable_covered += 1
            elif fc.annotation == "immutable":
                total_immutable += 1
                if covered:
                    total_immutable_covered += 1
            elif fc.annotation == "required":
                total_required += 1
                if covered:
                    total_required_covered += 1

    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Resources audited: **{len(reports)}**")
    lines.append(f"- Skipped (no resource / fetch error): **{skipped}**")
    lines.append(f"- No wrapper file found: **{no_wrapper}**")
    lines.append(f"- Total fields: **{total_fields}**")
    lines.append(
        f"- Settable user-input fields: **{total_settable_covered} / "
        f"{total_settable}** covered "
        f"({_pct(total_settable_covered, total_settable)})"
    )
    lines.append(
        f"- Immutable (create-only) fields: **{total_immutable_covered} / "
        f"{total_immutable}** covered "
        f"({_pct(total_immutable_covered, total_immutable)})"
    )
    lines.append(
        f"- Required fields: **{total_required_covered} / {total_required}** "
        f"covered ({_pct(total_required_covered, total_required)})"
    )
    lines.append("")
    lines.append(
        "Legend: ✏️ settable · 🔒 immutable (create-only) · ❗ required · "
        "📥 input-only · 🚫 output-only (skipped) · ✅ exposed by wrapper · "
        "❌ gap"
    )
    lines.append("")

    # Per-resource sections
    for r in sorted(reports, key=lambda x: x.service):
        lines.append(f"## {r.service}")
        if r.fetch_error:
            lines.append(f"- ⚠️  {r.fetch_error}")
            lines.append("")
            continue
        if not r.resource:
            lines.append("- No resource (query-only, suggestion, or upload service).")
            lines.append("")
            continue
        lines.append(f"- Resource: `{r.resource}`")
        if r.wrapper_file is None:
            lines.append("- ❌ **No wrapper file found** for this resource.")
            lines.append("")
            continue
        lines.append(f"- Wrapper: `{r.wrapper_file.relative_to(REPO_ROOT)}`")
        lines.append("")
        lines.append("| Field | Status | Covered by |")
        lines.append("|---|---|---|")
        for fc in r.fields:
            mark = _emoji_for_annotation(fc.annotation)
            cov = (
                "✅"
                if fc.covered_by
                else ("—" if fc.annotation == "output_only" else "❌")
            )
            covered_by = ", ".join(sorted(set(fc.covered_by))) if fc.covered_by else ""
            note = ""
            if fc.annotation == "output_only":
                note = " _(skipped intentionally)_"
            lines.append(f"| `{fc.field_name}` {mark} | {cov}{note} | {covered_by} |")
        # Gap callout
        gaps = [
            fc
            for fc in r.fields
            if not fc.covered_by and fc.annotation != "output_only"
        ]
        if gaps:
            lines.append("")
            lines.append("**Gaps:**")
            for g in gaps:
                badge = _emoji_for_annotation(g.annotation)
                lines.append(f"- {badge} `{g.field_name}` — {g.annotation}")
        lines.append("")
    return "\n".join(lines) + "\n"


def _pct(num: int, denom: int) -> str:
    if denom == 0:
        return "n/a"
    return f"{100 * num / denom:.1f}%"


# --------------------------------------------------------------------------- #
# Main                                                                        #
# --------------------------------------------------------------------------- #


def build_reports(refresh: bool = False) -> list[ServiceReport]:
    services = list_services(refresh=refresh)
    # Pre-load every wrapper file's methods (one walk over the tree).
    wrappers_by_file: dict[Path, list[WrapperMethod]] = {}
    for path in SERVICES_DIR.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        ms = collect_wrappers(path)
        if ms:
            wrappers_by_file[path] = ms

    reports: list[ServiceReport] = []
    for svc in services:
        resource = _resource_for_service(svc)
        if svc in NO_RESOURCE_SERVICES or not resource:
            reports.append(
                ServiceReport(
                    service=svc,
                    resource="",
                    wrapper_file=None,
                    fields=[],
                )
            )
            continue
        resource_md = fetch_md(resource, refresh=refresh)
        if resource_md is None:
            reports.append(
                ServiceReport(
                    service=svc,
                    resource=resource,
                    wrapper_file=None,
                    fields=[],
                    fetch_error=f"Failed to fetch {resource}.md.txt",
                )
            )
            continue
        fields = parse_resource_fields(resource_md)
        wrapper_file = find_wrapper_file(resource)
        wrappers = wrappers_by_file.get(wrapper_file, []) if wrapper_file else []
        coverage = score_coverage(resource, fields, wrappers)
        reports.append(
            ServiceReport(
                service=svc,
                resource=resource,
                wrapper_file=wrapper_file,
                fields=coverage,
            )
        )
    return reports


def main(argv: Iterable[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Re-fetch all reference markdown, ignoring cache.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=REPORT_PATH,
        help="Where to write the report (default: API_COVERAGE.md at repo root).",
    )
    args = parser.parse_args(list(argv))
    reports = build_reports(refresh=args.refresh)
    text = render_report(reports)
    args.out.write_text(text)
    print(f"Wrote {args.out} ({len(reports)} services).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
