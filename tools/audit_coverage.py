"""Audit our wrapper coverage of every Google Ads v23 settable input.

The audit is the single source for ``API_COVERAGE.md``. It triangulates
every field on every Mutate-able resource across three sources:

1. **Published markdown** at
   ``https://developers.google.com/google-ads/api/reference/rpc/v23/<Name>.md.txt``
2. **Source proto** at
   ``https://raw.githubusercontent.com/googleapis/googleapis/master/google/ads/googleads/v23/resources/<snake>.proto``
3. **Local Python SDK** (``google-ads`` proto-plus classes) inspected via
   ``inspect.getsource`` on the generated class

…and then compares the unioned field set against our wrapper code in
``src/services/`` to produce per-field coverage.

For every covered field we record:

- which wrapper method exposes it (param name or proto write path)
- which **MCP tool name** is registered for that wrapper (parsed out of
  ``register_<x>_tools`` in the service file)
- whether the tool's docstring documents every param it takes
  (``Args:``-block coverage)

The report is written to ``API_COVERAGE.md`` at the repo root. Run:

    uv run python tools/audit_coverage.py            # uses cache
    uv run python tools/audit_coverage.py --refresh  # re-fetch web sources

Cached web sources live at ``tools/.audit_cache/`` (gitignored). The
script is deterministic given the cache: same inputs → identical
report bytes (no timestamps, no run-counters).
"""

from __future__ import annotations

import argparse
import ast
import importlib
import inspect
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

DEVSITE_BASE = "https://developers.google.com/google-ads/api/reference/rpc/v23"
# googleapis/googleapis keeps v22, v23, and v24 side-by-side under their
# own paths, so the v23 path stays correct even on a moving ``master``.
# But the file-level *content* on master can change at any time — Google
# can patch annotations or fix typos. To pin the audit's proto cross-
# check to a specific snapshot, set ``PROTO_REF`` to a tag or commit
# SHA (or pass ``--proto-ref`` on the CLI).
DEFAULT_PROTO_REF = "master"
PROTO_REF = DEFAULT_PROTO_REF
PROTO_VERSION = "v23"
USER_AGENT = "Mozilla/5.0 (audit_coverage.py)"


def _proto_resource_base() -> str:
    return (
        f"https://raw.githubusercontent.com/googleapis/googleapis/{PROTO_REF}/"
        f"google/ads/googleads/{PROTO_VERSION}/resources"
    )


# Services we don't expect to map cleanly onto a single resource —
# query-only, suggestion, upload, manager, or otherwise modeled
# differently.
NO_RESOURCE_SERVICES: set[str] = {
    "GoogleAdsService",
    "GoogleAdsFieldService",
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
    "AdGroupAdLabelService",
    "AdGroupCriterionLabelService",
    "AdGroupLabelService",
    "CampaignLabelService",
    "CustomerLabelService",
}

SERVICE_TO_RESOURCE_OVERRIDES: dict[str, str] = {
    "AdService": "Ad",
    "BiddingStrategyService": "BiddingStrategy",
    "CampaignBudgetService": "CampaignBudget",
    "CustomerSkAdNetworkConversionValueSchemaService": "CustomerSkAdNetworkConversionValueSchema",
    "OfflineUserDataJobService": "OfflineUserDataJob",
    "ConversionUploadService": "",
    "ConversionAdjustmentUploadService": "",
    "UserDataService": "",
    "RecommendationService": "Recommendation",
    "BatchJobService": "BatchJob",
    "GoalService": "Goal",
}

STRUCTURAL_FIELDS = {"resource_name", "id"}

INTENTIONAL_NON_EXPOSURE: dict[str, dict[str, str]] = {
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


# --------------------------------------------------------------------------- #
# Fetch + cache                                                               #
# --------------------------------------------------------------------------- #


def cache_path_for(category: str, name: str) -> Path:
    safe = name.replace("/", "_")
    return CACHE_DIR / category / f"{safe}.txt"


def _http_get(url: str, *, cache_key: tuple[str, str], refresh: bool) -> str | None:
    cp = cache_path_for(*cache_key)
    if cp.exists() and not refresh:
        return cp.read_text()
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise
    cp.parent.mkdir(parents=True, exist_ok=True)
    cp.write_text(body)
    time.sleep(0.05)  # be polite
    return body


def fetch_devsite_md(name: str, *, refresh: bool = False) -> str | None:
    return _http_get(
        f"{DEVSITE_BASE}/{name}.md.txt",
        cache_key=("devsite", name),
        refresh=refresh,
    )


_PROTO_PACKAGE_RE = re.compile(
    r"^package\s+google\.ads\.googleads\.(\w+)\.", re.MULTILINE
)


class ProtoVersionMismatch(RuntimeError):
    """Raised when a fetched .proto declares a different version than expected."""


def _verify_proto_version(body: str, url: str) -> None:
    """Sanity-check the fetched proto's ``package`` line.

    The audit is for v23. If a fetch ever returns a proto declaring
    a different version (e.g. because we silently followed a redirect
    or the v23 directory was relocated), bail out loudly rather than
    produce a coverage report against the wrong version.
    """
    m = _PROTO_PACKAGE_RE.search(body)
    if not m:
        # No package line at all — non-proto file
        raise ProtoVersionMismatch(
            f"{url}: fetched body has no `package google.ads.googleads.<version>` line"
        )
    actual = m.group(1)
    if actual != PROTO_VERSION:
        raise ProtoVersionMismatch(
            f"{url}: expected package google.ads.googleads.{PROTO_VERSION}.* "
            f"but got google.ads.googleads.{actual}.*"
        )


def fetch_proto_source(resource: str, *, refresh: bool = False) -> str | None:
    snake = _snake(resource)
    # The googleapis repo uses a tightened snake_case for some acronyms
    # (e.g. ``YouTubeVideoUpload`` → ``youtube_video_upload``,
    # ``CustomerSkAdNetwork…`` → ``customer_sk_ad_network…``). Try the
    # naive snake first, then a variant that collapses common acronyms.
    candidates = [snake]
    snake_alt = snake.replace("you_tube", "youtube")
    if snake_alt != snake:
        candidates.append(snake_alt)
    base = _proto_resource_base()
    for name in candidates:
        url = f"{base}/{name}.proto"
        body = _http_get(
            url,
            cache_key=("proto", f"{PROTO_REF}_{name}"),
            refresh=refresh,
        )
        if body is not None:
            _verify_proto_version(body, url)
            return body
    return None


# --------------------------------------------------------------------------- #
# Parse markdown (devsite)                                                    #
# --------------------------------------------------------------------------- #


_SERVICE_ROW_RE = re.compile(r"^\| \[`(\w+Service)`\]")
# Field table row in a resource page:
#   | ## `field_name` | `type-or-link` Description starting with annotation |
_FIELD_ROW_RE = re.compile(r"^\| ## `(\w+)` \| (.*?) \|\s*$")


def list_services(refresh: bool = False) -> list[str]:
    md = fetch_devsite_md("overview", refresh=refresh)
    assert md is not None, "Failed to fetch overview"
    out: list[str] = []
    for line in md.splitlines():
        m = _SERVICE_ROW_RE.match(line)
        if m:
            out.append(m.group(1))
    return out


@dataclass
class MdField:
    name: str
    type_: str
    annotation: str  # output_only / immutable / required / input_only / settable
    description: str  # full description (sentence(s) following the type)


def parse_devsite_fields(md: str) -> list[MdField]:
    out: list[MdField] = []
    in_table = False
    for line in md.splitlines():
        if line.startswith("| Fields ||"):
            in_table = True
            continue
        if not in_table:
            continue
        if line.startswith("# "):
            break
        m = _FIELD_ROW_RE.match(line)
        if not m:
            continue
        name = m.group(1)
        rest = m.group(2)
        type_match = re.match(r"`([^`]+)`\s*(.*)", rest)
        if type_match:
            type_ = type_match.group(1)
            desc = type_match.group(2).strip()
        else:
            type_ = ""
            desc = rest
        out.append(
            MdField(
                name=name,
                type_=type_,
                annotation=_annotation_from_desc(desc),
                description=desc,
            )
        )
    return out


def _annotation_from_desc(desc: str) -> str:
    head = desc[:100]
    if head.startswith("Output only."):
        return "output_only"
    if head.startswith("Input only."):
        return "input_only"
    # "Required. Immutable." → immutable (because once set you can't change it)
    if head.startswith("Immutable.") or "Immutable." in head[: head.find(".") + 30]:
        return "immutable"
    if head.startswith("Required."):
        return "required"
    return "settable"


# --------------------------------------------------------------------------- #
# Parse source proto (.proto file from googleapis on GitHub)                  #
# --------------------------------------------------------------------------- #


@dataclass
class ProtoField:
    name: str
    behavior: str  # output_only / immutable / required / input_only / settable


def parse_proto_fields(proto_text: str, message_name: str) -> list[ProtoField]:
    """Extract **top-level** fields from the named message in the .proto.

    Strategy:
      1. Find the top-level message body (regex on ``^message X {`` …
         matching ``^}`` at start of line).
      2. Strip string literals and comments so subsequent brace tracking
         isn't fooled by braces inside ``"customers/{customer_id}"``
         patterns or ``// {`` comments.
      3. Walk char-by-char, tracking brace depth. Collect ``;``-
         terminated statements at depth 0 (top-level fields, plus
         option statements which we then filter out). Statements at
         depth 1 inside a top-level ``oneof { … }`` are also collected
         (oneof members behave like sibling fields).
      4. Skip statements that are nested-message or enum declarations.
    """
    pat = re.compile(
        rf"^message {re.escape(message_name)} \{{(?P<body>.*?)^\}}",
        re.DOTALL | re.MULTILINE,
    )
    m = pat.search(proto_text)
    if not m:
        return []
    body = m.group("body")

    # Strip strings (preserve length doesn't matter; just kill the contents
    # so brace tracking and the field regex aren't confused).
    body = re.sub(r'"(?:[^"\\]|\\.)*"', '""', body)
    body = re.sub(r"/\*.*?\*/", "", body, flags=re.DOTALL)
    body = re.sub(r"//[^\n]*", "", body)

    statements = _split_proto_statements(body)
    out: list[ProtoField] = []
    seen: set[str] = set()
    for stmt in statements:
        for field in _extract_field_from_statement(stmt):
            if field.name in seen:
                continue
            seen.add(field.name)
            out.append(field)
    return out


def _split_proto_statements(body: str) -> list[str]:
    """Split a (string-stripped) proto body into top-level statements.

    A statement at depth 0 ends at ``;`` (when not inside ``[...]``) or
    enters a block at ``{`` (when not inside ``[...]``). Tracking
    ``[``/``]`` is required because field-decl annotations like
    ``[ (google.api.resource_reference) = { type: "" } ]`` contain
    braces that are *not* block openers.

    For ``oneof { … }`` blocks, the inner body is split into
    sub-statements which are returned alongside the top-level ones.
    For ``message { … }`` and ``enum { … }``, the body is dropped.
    """
    statements: list[str] = []
    i = 0
    n = len(body)
    while i < n:
        while i < n and body[i].isspace():
            i += 1
        if i >= n:
            break
        # Read until a top-level ';' or '{' (i.e. one not inside []).
        start = i
        bracket_depth = 0
        while i < n:
            c = body[i]
            if c == "[":
                bracket_depth += 1
            elif c == "]":
                bracket_depth -= 1
            elif bracket_depth == 0 and c in ";{":
                break
            i += 1
        if i >= n:
            break
        if body[i] == ";":
            statements.append(body[start:i].strip())
            i += 1
            continue
        # body[i] == '{' — block opener
        head = body[start:i].strip()
        block_start = i + 1
        depth = 1
        i += 1
        while i < n and depth > 0:
            if body[i] == "{":
                depth += 1
            elif body[i] == "}":
                depth -= 1
            i += 1
        block_body = body[block_start : i - 1]
        if i < n and body[i] == ";":
            i += 1
        head_first = head.split()[0] if head.split() else ""
        if head_first == "oneof":
            statements.extend(_split_proto_statements(block_body))
        elif head_first in {"message", "enum", "service"}:
            continue
        elif head_first == "option" or head.startswith("option "):
            continue
        else:
            continue
    return statements


# Field declarations come in many shapes — types may be qualified
# (``foo.bar.Baz``), ``map<K, V>``, or split across lines. Rather than
# parse the type, we anchor on the field name + ``= <number>`` pattern:
# the *last* identifier before ``= <num>`` in the statement is the
# field name. Options follow inside ``[...]``.
_FIELD_DECL_RE = re.compile(
    r"""
    (?P<name>\w+)
    \s*=\s*\d+
    (?:\s*\[(?P<opts>.*)\])?
    \s*$
    """,
    re.VERBOSE | re.DOTALL,
)
_BEHAVIOR_RE = re.compile(r"\(google\.api\.field_behavior\)\s*=\s*(\w+)")


def _extract_field_from_statement(stmt: str) -> list[ProtoField]:
    """If stmt is a field declaration, yield the ProtoField; else yield nothing."""
    head_first = stmt.split()[0] if stmt.split() else ""
    if head_first in {
        "option",
        "reserved",
        "syntax",
        "package",
        "import",
        "message",
        "enum",
    }:
        return []
    fm = _FIELD_DECL_RE.search(stmt)
    if not fm:
        return []
    name = fm.group("name")
    if name in {"option", "reserved"}:
        return []
    opts = fm.group("opts") or ""
    behavior = "settable"
    for b in _BEHAVIOR_RE.findall(opts):
        b_low = b.lower()
        if b_low == "output_only":
            behavior = "output_only"
            break
        if b_low == "immutable":
            behavior = "immutable"
        elif b_low == "required" and behavior == "settable":
            behavior = "required"
        elif b_low == "input_only" and behavior == "settable":
            behavior = "input_only"
    return [ProtoField(name=name, behavior=behavior)]


# --------------------------------------------------------------------------- #
# SDK introspection                                                           #
# --------------------------------------------------------------------------- #


def load_sdk_class(resource: str):
    snake = _snake(resource)
    snake_alt = snake.replace("you_tube", "youtube")
    snakes = [snake] + ([snake_alt] if snake_alt != snake else [])
    candidates: list[str] = []
    for s in snakes:
        candidates.extend(
            [
                f"google.ads.googleads.v23.resources.types.{s}",
                f"google.ads.googleads.v23.common.types.{s}",
            ]
        )
    for module_path in candidates:
        try:
            mod = importlib.import_module(module_path)
            cls = getattr(mod, resource, None)
            if cls is None:
                # Some classes have alt-cased names (e.g. YouTubeVideoUpload)
                for cand_name in (resource, resource.replace("YouTube", "YouTube")):
                    cls = getattr(mod, cand_name, None)
                    if cls is not None:
                        break
            if cls is not None:
                return cls
        except (ImportError, AttributeError):
            continue
    return None


def sdk_field_names(resource: str) -> set[str]:
    cls = load_sdk_class(resource)
    if cls is None:
        return set()
    try:
        return set(cls.meta.fields.keys())
    except (AttributeError, KeyError):
        return set()


# --------------------------------------------------------------------------- #
# Wrapper introspection                                                       #
# --------------------------------------------------------------------------- #


@dataclass
class WrapperMethod:
    name: str
    file: Path
    kind: str  # 'service' (class method) or 'tool' (registered MCP tool)
    params: set[str] = field(default_factory=set)
    writes: set[str] = field(default_factory=set)
    docstring_args: set[str] = field(default_factory=set)


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


def _method_kind(node: ast.AsyncFunctionDef, ancestry: list[ast.AST]) -> str:
    """Return 'tool' if defined inside ``create_*_tools``, else 'service'."""
    for parent in ancestry:
        if (
            isinstance(parent, ast.FunctionDef)
            and parent.name.startswith("create_")
            and parent.name.endswith("_tools")
        ):
            return "tool"
    return "service"


_DOCSTRING_ARG_RE = re.compile(r"^\s+(\w+)\s*:", re.MULTILINE)


def _extract_documented_args(docstring: str) -> set[str]:
    """Return param names mentioned in an Args:/Returns: structured docstring."""
    if not docstring:
        return set()
    # Capture the Args block: everything from "Args:" up to the next blank
    # double-line or "Returns:" / "Raises:" / EOF.
    m = re.search(
        r"Args:\s*\n(.*?)(?:\n\s*\n|\n\s*Returns:|\n\s*Raises:|\Z)",
        docstring,
        re.DOTALL,
    )
    if not m:
        return set()
    block = m.group(1)
    return set(_DOCSTRING_ARG_RE.findall(block))


SKIP_PREFIXES = ("list_", "search_", "get_", "register_", "_", "remove_")


def collect_wrappers(file_path: Path) -> list[WrapperMethod]:
    src = file_path.read_text()
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return []
    out: list[WrapperMethod] = []

    # Walk with parent tracking so we can classify tool vs service methods.
    def walk(node: ast.AST, ancestry: list[ast.AST]) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.AsyncFunctionDef):
                if not child.name.startswith(SKIP_PREFIXES):
                    wm = _build_wrapper_method(file_path, child, ancestry)
                    if wm is not None:
                        out.append(wm)
            walk(child, ancestry + [child])

    walk(tree, [])
    return out


def _build_wrapper_method(
    file_path: Path,
    node: ast.AsyncFunctionDef,
    ancestry: list[ast.AST],
) -> WrapperMethod | None:
    kind = _method_kind(node, ancestry)
    wm = WrapperMethod(name=node.name, file=file_path, kind=kind)
    wm.params = {a.arg for a in node.args.args} | {a.arg for a in node.args.kwonlyargs}
    wm.params.discard("self")
    wm.params.discard("ctx")
    docstring = ast.get_docstring(node) or ""
    wm.docstring_args = _extract_documented_args(docstring)
    for sub in ast.walk(node):
        if isinstance(sub, ast.Assign):
            for tgt in sub.targets:
                p = _attr_chain(tgt)
                if p:
                    wm.writes.add(p)
        elif isinstance(sub, ast.AugAssign):
            p = _attr_chain(sub.target)
            if p:
                wm.writes.add(p)
        elif isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute):
            if sub.func.attr in {"append", "extend", "MergeFrom", "CopyFrom", "add"}:
                p = _attr_chain(sub.func.value)
                if p:
                    wm.writes.add(p)
    return wm


# --------------------------------------------------------------------------- #
# Map wrapper file → list of MCP tool names                                   #
# --------------------------------------------------------------------------- #


def collect_mcp_tool_names(file_path: Path) -> list[str]:
    """Parse a service file and return the list of MCP tool names registered.

    A tool is registered when a function defined inside ``create_*_tools``
    appears in the ``tools.extend([...])`` or ``tools.append(...)`` call.
    Falls back to the set of all async funcs defined inside ``create_*_tools``.
    """
    try:
        tree = ast.parse(file_path.read_text())
    except SyntaxError:
        return []
    names: list[str] = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.FunctionDef)
            and node.name.startswith("create_")
            and node.name.endswith("_tools")
        ):
            for sub in ast.walk(node):
                if isinstance(sub, ast.AsyncFunctionDef):
                    names.append(sub.name)
    # Dedup while preserving order.
    seen: set[str] = set()
    out: list[str] = []
    for n in names:
        if n not in seen:
            seen.add(n)
            out.append(n)
    return out


def find_wrapper_file(resource: str) -> Path | None:
    snake = _snake(resource)
    snake_alt = snake.replace("you_tube", "youtube").replace("sk_ad", "skad")
    candidates: list[str] = []
    for s in (snake, snake_alt):
        candidates.extend([f"{s}_service.py", f"{s}.py"])
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
# Field merge across the three sources                                        #
# --------------------------------------------------------------------------- #


@dataclass
class UnifiedField:
    name: str
    type_: str
    annotation: str
    description: str
    in_md: bool
    in_proto: bool
    in_sdk: bool
    sources_agree: bool


def merge_field_sources(
    md_fields: list[MdField],
    proto_fields: list[ProtoField],
    sdk_fields: set[str],
) -> list[UnifiedField]:
    """Use markdown as the authoritative field list, cross-validate with proto + SDK.

    The markdown table on the published resource page is the canonical
    user-facing inventory of top-level fields. Proto and SDK are
    secondary sources used to validate annotations and presence — not
    to *add* fields the markdown doesn't list. (If the markdown is ever
    missing a field that proto/sdk has, it'll show up in the
    ``extras_in_proto`` / ``extras_in_sdk`` summary numbers.)
    """
    proto_by_name = {f.name: f for f in proto_fields}
    out: list[UnifiedField] = []
    # Annotations that the markdown and proto can legitimately disagree on
    # without it being a data error — e.g. a field annotated
    # "Input only. Immutable." in markdown classifies as input_only (the
    # leading sentence wins); the proto's field_behavior=IMMUTABLE wins
    # the same coin flip the other way. Both signals are correct.
    EQUIVALENT_ANNOTATIONS = {
        frozenset({"input_only", "immutable"}),
    }
    for md in md_fields:
        pf = proto_by_name.get(md.name)
        in_proto = pf is not None
        # Python-keyword aliasing: proto-plus exposes `type` as `type_` and
        # so on for any field whose name collides with a Python keyword.
        in_sdk = md.name in sdk_fields or f"{md.name}_" in sdk_fields
        agree = True
        if in_proto and pf is not None and md.annotation != pf.behavior:
            pair = frozenset({md.annotation, pf.behavior})
            if pair not in EQUIVALENT_ANNOTATIONS:
                agree = False
        if not in_proto:
            agree = False
        if not in_sdk:
            agree = False
        out.append(
            UnifiedField(
                name=md.name,
                type_=md.type_,
                annotation=md.annotation,
                description=md.description,
                in_md=True,
                in_proto=in_proto,
                in_sdk=in_sdk,
                sources_agree=agree,
            )
        )
    return out


# --------------------------------------------------------------------------- #
# Coverage scoring                                                            #
# --------------------------------------------------------------------------- #


@dataclass
class FieldCoverage:
    field_name: str
    type_: str
    annotation: str
    description: str
    in_md: bool
    in_proto: bool
    in_sdk: bool
    sources_agree: bool
    service_methods: list[str] = field(default_factory=list)
    mcp_tools: list[str] = field(default_factory=list)
    suppression_reason: str = ""


def _wrapper_covers(field_name: str, wm: WrapperMethod) -> bool:
    candidates = {field_name}
    if field_name == "type":
        candidates.add("type_")
    if candidates & wm.params:
        return True
    for w in wm.writes:
        if candidates & set(w.split(".")):
            return True
    return False


def score_coverage(
    resource: str,
    fields: list[UnifiedField],
    wrappers: list[WrapperMethod],
) -> list[FieldCoverage]:
    suppress = INTENTIONAL_NON_EXPOSURE.get(resource, {})
    out: list[FieldCoverage] = []
    for fld in fields:
        cov = FieldCoverage(
            field_name=fld.name,
            type_=fld.type_,
            annotation=fld.annotation,
            description=fld.description,
            in_md=fld.in_md,
            in_proto=fld.in_proto,
            in_sdk=fld.in_sdk,
            sources_agree=fld.sources_agree,
        )
        if fld.name in STRUCTURAL_FIELDS:
            cov.service_methods.append("(structural)")
            out.append(cov)
            continue
        if fld.name in suppress:
            cov.suppression_reason = suppress[fld.name]
            out.append(cov)
            continue
        for wm in wrappers:
            if _wrapper_covers(fld.name, wm):
                if wm.kind == "service":
                    cov.service_methods.append(wm.name)
                else:
                    cov.mcp_tools.append(wm.name)
        out.append(cov)
    return out


# --------------------------------------------------------------------------- #
# Docstring coverage scoring                                                  #
# --------------------------------------------------------------------------- #


@dataclass
class DocstringFinding:
    tool: str
    missing_args: list[str]
    documented_args: list[str]


def docstring_findings(wrappers: list[WrapperMethod]) -> list[DocstringFinding]:
    out: list[DocstringFinding] = []
    for wm in wrappers:
        if wm.kind != "tool":
            continue
        # Excluded params that don't need docstring documentation
        relevant = wm.params - {"self", "ctx"}
        missing = sorted(relevant - wm.docstring_args)
        documented = sorted(relevant & wm.docstring_args)
        out.append(
            DocstringFinding(
                tool=wm.name, missing_args=missing, documented_args=documented
            )
        )
    return out


# --------------------------------------------------------------------------- #
# Report                                                                      #
# --------------------------------------------------------------------------- #


@dataclass
class ServiceReport:
    service: str
    resource: str
    wrapper_file: Path | None
    fields: list[FieldCoverage] = field(default_factory=list)
    mcp_tools: list[str] = field(default_factory=list)
    docstring_findings: list[DocstringFinding] = field(default_factory=list)
    fetch_error: str | None = None
    md_fetched: bool = False
    proto_fetched: bool = False
    sdk_loaded: bool = False


def _resource_for_service(svc: str) -> str:
    if svc in SERVICE_TO_RESOURCE_OVERRIDES:
        return SERVICE_TO_RESOURCE_OVERRIDES[svc]
    if svc.endswith("Service"):
        return svc[: -len("Service")]
    return svc


def _emoji(annotation: str) -> str:
    return {
        "output_only": "🚫",
        "immutable": "🔒",
        "required": "❗",
        "input_only": "📥",
        "settable": "✏️",
    }.get(annotation, "?")


def _coverage_mark(cov: FieldCoverage) -> str:
    if cov.annotation == "output_only":
        return "—"
    if cov.suppression_reason:
        return "🛡️"
    if cov.service_methods or cov.mcp_tools:
        return "✅"
    return "❌"


def _agreement_mark(cov: FieldCoverage) -> str:
    sources = []
    if cov.in_md:
        sources.append("md")
    if cov.in_proto:
        sources.append("proto")
    if cov.in_sdk:
        sources.append("sdk")
    if cov.sources_agree:
        return "agree"
    return "/".join(sources) if sources else "—"


def render_report(reports: list[ServiceReport]) -> str:
    lines: list[str] = []
    lines.append("# API Coverage")
    lines.append("")
    lines.append(
        "Auto-generated by `tools/audit_coverage.py`. **Do not hand-edit.** "
        "Re-run the tool whenever the SDK or wrappers change."
    )
    lines.append("")
    lines.append("Sources cross-checked, in order of preference:")
    lines.append("")
    lines.append(f"1. **Devsite markdown** — `{DEVSITE_BASE}/<Name>.md.txt`")
    lines.append(
        f"2. **Source proto** — `{_proto_resource_base()}/<snake>.proto` "
        f"(ref `{PROTO_REF}`, version `{PROTO_VERSION}`; each fetched file's "
        f"`package` line is verified to declare `google.ads.googleads.{PROTO_VERSION}.*`)"
    )
    lines.append(
        f"3. **Local SDK** — `google.ads.googleads.{PROTO_VERSION}.resources.types.<snake>`"
    )
    lines.append("")

    # ---------- Summary ----------
    total_fields = 0
    settable = settable_cov = 0
    immutable = immutable_cov = 0
    required = required_cov = 0
    out_only = 0
    docstring_total = 0
    docstring_documented = 0
    sources_disagreement = 0
    no_wrapper_resources = 0
    skipped = 0
    for r in reports:
        if r.fetch_error or not r.fields:
            skipped += 1
            continue
        if r.wrapper_file is None and r.resource:
            no_wrapper_resources += 1
        for fc in r.fields:
            total_fields += 1
            covered = bool(
                fc.service_methods
                or fc.mcp_tools
                or fc.suppression_reason
                or fc.field_name in STRUCTURAL_FIELDS
            )
            if fc.annotation == "settable":
                settable += 1
                if covered:
                    settable_cov += 1
            elif fc.annotation == "immutable":
                immutable += 1
                if covered:
                    immutable_cov += 1
            elif fc.annotation == "required":
                required += 1
                if covered:
                    required_cov += 1
            elif fc.annotation == "output_only":
                out_only += 1
            if not fc.sources_agree and (fc.in_md or fc.in_proto or fc.in_sdk):
                sources_disagreement += 1
        for d in r.docstring_findings:
            for _ in d.missing_args:
                docstring_total += 1
            for _ in d.documented_args:
                docstring_total += 1
                docstring_documented += 1

    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Resources audited: **{len(reports)}**")
    lines.append(f"- Skipped (no resource / fetch error): **{skipped}**")
    lines.append(f"- Resources with **no wrapper file**: **{no_wrapper_resources}**")
    lines.append(f"- Total fields across all resources: **{total_fields}**")
    lines.append(
        f"- Settable: **{settable_cov} / {settable}** ({_pct(settable_cov, settable)})"
    )
    lines.append(
        f"- Immutable (create-only): **{immutable_cov} / {immutable}** ({_pct(immutable_cov, immutable)})"
    )
    lines.append(
        f"- Required: **{required_cov} / {required}** ({_pct(required_cov, required)})"
    )
    lines.append(f"- Output-only (skipped intentionally): **{out_only}**")
    lines.append(
        f"- Source disagreements (md vs proto vs sdk): **{sources_disagreement}**"
    )
    lines.append(
        f"- Tool-wrapper docstring args documented: **{docstring_documented} / {docstring_total}** ({_pct(docstring_documented, docstring_total)})"
    )
    lines.append("")
    lines.append(
        "Legend: ✏️ settable · 🔒 immutable (create-only) · ❗ required · 📥 input-only · 🚫 output-only · "
        "✅ exposed by wrapper · ❌ gap · 🛡️ intentionally suppressed · — n/a"
    )
    lines.append("")

    # ---------- Per-service sections ----------
    for r in sorted(reports, key=lambda x: x.service):
        lines.extend(_render_service(r))
    return "\n".join(lines) + "\n"


def _render_service(r: ServiceReport) -> list[str]:
    out: list[str] = [f"## {r.service}", ""]
    if r.fetch_error:
        out.append(f"⚠️  {r.fetch_error}")
        out.append("")
        return out
    if not r.resource:
        out.append(
            "- _No resource (query-only, suggestion, upload, or label-link service)._"
        )
        out.append("")
        return out
    out.append(f"- **Resource**: `{r.resource}`")
    sources = []
    sources.append("md ✅" if r.md_fetched else "md ❌")
    sources.append("proto ✅" if r.proto_fetched else "proto ❌")
    sources.append("sdk ✅" if r.sdk_loaded else "sdk ❌")
    out.append(f"- **Sources**: {' · '.join(sources)}")
    if r.wrapper_file is None:
        out.append("- **Wrapper**: ❌ no file found — service is unimplemented")
        out.append("")
        return out
    out.append(f"- **Wrapper file**: `{r.wrapper_file.relative_to(REPO_ROOT)}`")
    if r.mcp_tools:
        out.append(
            f"- **MCP tools registered** ({len(r.mcp_tools)}): "
            + ", ".join(f"`{t}`" for t in r.mcp_tools)
        )
    out.append("")
    out.append("### Fields")
    out.append("")
    out.append(
        "| Field | Annot. | Status | MCP tool(s) | Service method(s) | Sources | Description |"
    )
    out.append("|---|---|---|---|---|---|---|")
    for fc in r.fields:
        annot = _emoji(fc.annotation)
        mark = _coverage_mark(fc)
        tools = ", ".join(f"`{t}`" for t in sorted(set(fc.mcp_tools))) or "—"
        methods = ", ".join(sorted(set(fc.service_methods))) or "—"
        agreement = _agreement_mark(fc)
        if fc.suppression_reason:
            mark_cell = f"{mark} _{fc.suppression_reason}_"
        else:
            mark_cell = mark
        # Compress description: first sentence only, escape pipes.
        desc = fc.description.split(". ")[0]
        desc = desc.replace("|", "\\|").replace("\n", " ").strip()
        if len(desc) > 200:
            desc = desc[:197] + "..."
        out.append(
            f"| `{fc.field_name}` | {annot} | {mark_cell} | {tools} | {methods} | {agreement} | {desc} |"
        )
    # Gap callout
    gaps = [
        fc
        for fc in r.fields
        if not (
            fc.service_methods
            or fc.mcp_tools
            or fc.suppression_reason
            or fc.field_name in STRUCTURAL_FIELDS
        )
        and fc.annotation != "output_only"
    ]
    if gaps:
        out.append("")
        out.append("**Field gaps:**")
        for g in gaps:
            out.append(
                f"- {_emoji(g.annotation)} `{g.field_name}` — {g.annotation}: {g.description.split('. ')[0]}"
            )
    # Docstring callout
    doc_gaps = [d for d in r.docstring_findings if d.missing_args]
    if doc_gaps:
        out.append("")
        out.append("**Docstring gaps:**")
        for d in doc_gaps:
            out.append(
                f"- `{d.tool}` — missing: "
                + ", ".join(f"`{a}`" for a in d.missing_args)
            )
    out.append("")
    return out


def _pct(num: int, denom: int) -> str:
    if denom == 0:
        return "n/a"
    return f"{100 * num / denom:.1f}%"


# --------------------------------------------------------------------------- #
# Main                                                                        #
# --------------------------------------------------------------------------- #


def build_reports(refresh: bool = False) -> list[ServiceReport]:
    services = list_services(refresh=refresh)
    # Pre-load every wrapper file's methods.
    wrappers_by_file: dict[Path, list[WrapperMethod]] = {}
    tools_by_file: dict[Path, list[str]] = {}
    for path in SERVICES_DIR.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        ms = collect_wrappers(path)
        if ms:
            wrappers_by_file[path] = ms
            tools_by_file[path] = collect_mcp_tool_names(path)

    reports: list[ServiceReport] = []
    for svc in services:
        resource = _resource_for_service(svc)
        if svc in NO_RESOURCE_SERVICES or not resource:
            reports.append(ServiceReport(service=svc, resource="", wrapper_file=None))
            continue
        md_text = fetch_devsite_md(resource, refresh=refresh)
        proto_text = fetch_proto_source(resource, refresh=refresh)
        sdk_fields = sdk_field_names(resource)
        sdk_loaded = bool(sdk_fields)

        if md_text is None and proto_text is None and not sdk_loaded:
            reports.append(
                ServiceReport(
                    service=svc,
                    resource=resource,
                    wrapper_file=None,
                    fetch_error=f"All three sources missing for `{resource}`.",
                )
            )
            continue
        md_fields = parse_devsite_fields(md_text) if md_text else []
        proto_fields = parse_proto_fields(proto_text, resource) if proto_text else []
        unified = merge_field_sources(md_fields, proto_fields, sdk_fields)

        wrapper_file = find_wrapper_file(resource)
        wrappers = wrappers_by_file.get(wrapper_file, []) if wrapper_file else []
        mcp_tools = tools_by_file.get(wrapper_file, []) if wrapper_file else []
        coverage = score_coverage(resource, unified, wrappers)
        d_findings = docstring_findings(wrappers)

        reports.append(
            ServiceReport(
                service=svc,
                resource=resource,
                wrapper_file=wrapper_file,
                fields=coverage,
                mcp_tools=mcp_tools,
                docstring_findings=d_findings,
                md_fetched=md_text is not None,
                proto_fetched=proto_text is not None,
                sdk_loaded=sdk_loaded,
            )
        )
    return reports


def main(argv: Iterable[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Re-fetch all reference markdown and .proto sources, ignoring cache.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=REPORT_PATH,
        help="Where to write the report (default: API_COVERAGE.md at repo root).",
    )
    parser.add_argument(
        "--proto-ref",
        default=DEFAULT_PROTO_REF,
        help=(
            "git ref (branch / tag / commit SHA) on googleapis/googleapis to fetch "
            "the v23 .proto sources from. Defaults to 'master'. Pin to a commit SHA "
            "for fully deterministic runs across days."
        ),
    )
    args = parser.parse_args(list(argv))
    global PROTO_REF
    PROTO_REF = args.proto_ref
    reports = build_reports(refresh=args.refresh)
    text = render_report(reports)
    args.out.write_text(text)
    print(f"Wrote {args.out} ({len(reports)} services, proto ref={PROTO_REF}).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
