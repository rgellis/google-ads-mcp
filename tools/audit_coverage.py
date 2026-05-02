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
    "CustomerConversionGoal": {
        "category": "Identity-encoded in resource_name — cannot be set as a standalone field.",
        "origin": "Identity-encoded in resource_name — cannot be set as a standalone field.",
    },
    "CampaignConversionGoal": {
        "campaign": "Identity-encoded in resource_name (customers/X/campaignConversionGoals/Y).",
    },
    "ConversionGoalCampaignConfig": {
        "campaign": "Identity-encoded in resource_name (customers/X/conversionGoalCampaignConfigs/Y).",
    },
    "CustomerCustomizer": {
        "value": "Wired through value_type + string_value via create_customer_customizer_operation helper (audit can't follow sync helpers).",
    },
    "AdGroupCustomizer": {
        "value": "Wired through value_type + string_value via create_ad_group_customizer_operation helper.",
    },
    "CampaignCustomizer": {
        "value": "Wired through value_type + string_value via create_campaign_customizer_operation helper.",
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
# Field table row in a resource or submessage page:
#   | ## `field_name` | `type-or-link` Description starting with annotation |
# Top-level fields use ``##``; oneof members under a ``Union field``
# header use ``###``. Repeated fields are rendered with ``[]`` suffix
# on the name (e.g. ``final_urls[]``); deprecated fields carry a
# `` (deprecated)`` suffix inside the backticks. Both are stripped to
# yield the canonical field name.
_FIELD_ROW_RE = re.compile(
    r"^\| #{2,3} `(\w+)(?:\[\])?(?:\s*\(deprecated\))?` \| (.*?) \|\s*$"
)


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


def _find_message_body(proto_text: str, qualname: str) -> str | None:
    """Return the body (between matching braces) of the named message.

    ``qualname`` may be dotted (``Outer.Inner.Leaf``); each segment is
    resolved within the previous segment's body. Returns ``None`` if any
    segment is not found. Allows leading whitespace on the ``message X {``
    declaration so nested messages match.
    """
    text = proto_text
    parts = qualname.split(".")
    for i, part in enumerate(parts):
        # ``\bmessage <name>\b`` followed by optional whitespace and ``{``.
        # Allows leading whitespace so nested messages (indented) match.
        pat = re.compile(rf"^\s*message\s+{re.escape(part)}\s*\{{", re.MULTILINE)
        m = pat.search(text)
        if not m:
            return None
        depth = 1
        j = m.end()
        n = len(text)
        # Strip string literals just within this scan window so braces
        # inside ``"customers/{customer_id}"`` don't confuse the depth
        # counter. (We strip lazily here rather than across the whole
        # body to keep the parent text intact for later lookups.)
        scan = text[j:]
        scan = re.sub(r'"(?:[^"\\]|\\.)*"', '""', scan)
        scan = re.sub(r"/\*.*?\*/", "", scan, flags=re.DOTALL)
        scan = re.sub(r"//[^\n]*", "", scan)
        k = 0
        body_end = -1
        while k < len(scan):
            c = scan[k]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    body_end = k
                    break
            k += 1
        if body_end < 0:
            return None
        # The body in the *original* text spans the same character offset
        # as in the stripped scan (only string contents were replaced;
        # length was preserved by the substitutions, though comments may
        # have changed length). Slice back from the original to keep
        # field declarations intact.
        body = scan[:body_end]
        if i == len(parts) - 1:
            return body
        text = body
    return None


def parse_proto_fields(proto_text: str, message_name: str) -> list[ProtoField]:
    """Extract fields from the named message in the .proto.

    ``message_name`` may be a bare name (``ShoppingSetting``) or a dotted
    qualname (``Campaign.LocalServicesCampaignSettings.CategoryBid``).
    For dotted names, descend through each parent message body in turn
    so nested messages buried under multiple parents resolve correctly.

    Strategy at each level:
      1. Find ``message X {`` anywhere in the searched text (regex
         allows leading whitespace so nested declarations match).
      2. Track brace depth char-by-char to find the matching ``}``.
      3. At the leaf level, strip string literals and comments and
         walk statements; collect ``;``-terminated field declarations
         and ``oneof`` members.
    """
    body = _find_message_body(proto_text, message_name)
    if body is None:
        return []

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
# Submessage helpers (recursive leaf audit)                                   #
# --------------------------------------------------------------------------- #


# proto-plus exposes a few well-known wrapper / utility types from
# google.protobuf. They aren't user-payload fields so we stop recursion
# at them (their leaves like ``Timestamp.seconds`` aren't part of the
# Google Ads API surface).
_WELL_KNOWN_PROTO_MODULES = ("google.protobuf",)

# Submessage types that are effectively output-only — every field
# inside is computed/validated by Google's policy engine, never set
# by a caller. The protos don't always annotate them as
# ``OUTPUT_ONLY`` (because the *parent's* field annotation is
# considered enough), so we have to recognize them by type name.
_EFFECTIVELY_OUTPUT_ONLY_TYPES = {
    # Policy review chain
    "PolicySummary",
    "AdGroupAdPolicySummary",
    "AdAssetPolicySummary",
    "AssetPolicySummary",
    "AssetFieldTypePolicySummary",
    "PolicyTopicEntry",
    "PolicyTopicEvidence",
    "PolicyTopicConstraint",
    "PolicyValidationParameter",
}


def _is_well_known(message_class: type) -> bool:
    return any(
        message_class.__module__.startswith(prefix)
        for prefix in _WELL_KNOWN_PROTO_MODULES
    )


def _is_effectively_output_only(message_class: type) -> bool:
    return message_class.__name__ in _EFFECTIVELY_OUTPUT_ONLY_TYPES


def _qualified_md_name(message_class: type) -> str:
    """Devsite name for a message class.

    Devsite uses dotted qualnames for nested types
    (``Campaign.ShoppingSetting``) and bare names for top-level ones
    (``RealTimeBiddingSetting``). Python's ``__qualname__`` matches that
    exactly for proto-plus classes.
    """
    return message_class.__qualname__


def _proto_file_for_class(message_class: type) -> str | None:
    """Return the relative proto file path on googleapis/googleapis.

    Maps the SDK module path to the v23 proto layout:
      google.ads.googleads.v23.<dir>.types.<snake>
        → google/ads/googleads/v23/<dir>/<snake>.proto

    Returns None if the module doesn't match the v23 layout (e.g. the
    class is from ``google.protobuf``).
    """
    mod = message_class.__module__
    prefix = f"google.ads.googleads.{PROTO_VERSION}."
    if not mod.startswith(prefix):
        return None
    suffix = mod[len(prefix) :]
    parts = suffix.split(".")
    if len(parts) < 3 or parts[-2] != "types":
        return None
    sub_dir = ".".join(parts[:-2])  # e.g. ``common`` or ``resources``
    snake = parts[-1]
    return (
        f"google/ads/googleads/{PROTO_VERSION}/"
        f"{sub_dir.replace('.', '/')}/{snake}.proto"
    )


def fetch_submessage_md(qualified_name: str, *, refresh: bool = False) -> str | None:
    """Fetch a submessage devsite page, cached by qualified name.

    Cache key is the dotted qualified name (``Campaign.ShoppingSetting``).
    Hit on the first call for any given submessage; common types like
    ``TargetingSetting`` are reused across every resource that nests
    them.
    """
    return _http_get(
        f"{DEVSITE_BASE}/{qualified_name}.md.txt",
        cache_key=("devsite", qualified_name),
        refresh=refresh,
    )


def fetch_common_proto_file(file_path: str, *, refresh: bool = False) -> str | None:
    """Fetch a v23 proto file by its googleapis-relative path, cached.

    Cache key is the proto ref + the file path so a single ``common``
    proto referenced from many resources is fetched only once per ref.
    Re-uses ``_verify_proto_version`` to guard against fetching the
    wrong version's body.
    """
    url = f"https://raw.githubusercontent.com/googleapis/googleapis/{PROTO_REF}/{file_path}"
    body = _http_get(
        url,
        cache_key=("proto", f"{PROTO_REF}_{file_path.replace('/', '_')}"),
        refresh=refresh,
    )
    if body is not None:
        _verify_proto_version(body, url)
    return body


def iter_submessage_fields(message_class: type):
    """Yield ``(field_name, field_class)`` for each message-typed field.

    Skips enums, scalars, well-known google.protobuf types, and
    effectively-output-only submessage types (policy summaries etc.).
    Includes repeated message fields — we descend into the entry shape
    once.
    """
    try:
        fields = message_class.meta.fields
    except AttributeError:
        return
    for name, f in fields.items():
        if f.message is None:
            continue
        if _is_well_known(f.message):
            continue
        if _is_effectively_output_only(f.message):
            continue
        yield name, f.message


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
    # Field names on the *parent resource* whose entire submessage payload
    # this wrapper accepts as a dict and forwards via
    # ``set_optional_submessage(parent, "<field>", value, MsgClass)`` —
    # which means every leaf inside that submessage is transitively
    # reachable.
    dict_passthrough: set[str] = field(default_factory=set)
    # Field names whose entire submessage payload this wrapper accepts as
    # a typed proto-plus value (e.g. ``shopping_setting:
    # Optional[Campaign.ShoppingSetting]``). Same reachability semantics
    # as ``dict_passthrough``.
    typed_passthrough: set[str] = field(default_factory=set)


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


def _method_kind(
    node: ast.AsyncFunctionDef | ast.FunctionDef, ancestry: list[ast.AST]
) -> str:
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
    # Both async and sync defs are collected — many service classes
    # expose their proto-write logic through sync helpers like
    # ``create_<resource>_operation`` that the async tool wrapper just
    # delegates to. Skipping sync defs would invisibly drop those
    # writes from the coverage check.
    def walk(node: ast.AST, ancestry: list[ast.AST]) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.AsyncFunctionDef, ast.FunctionDef)):
                if not child.name.startswith(SKIP_PREFIXES):
                    wm = _build_wrapper_method(file_path, child, ancestry)
                    if wm is not None:
                        out.append(wm)
            walk(child, ancestry + [child])

    walk(tree, [])
    return out


def _build_wrapper_method(
    file_path: Path,
    node: ast.AsyncFunctionDef | ast.FunctionDef,
    ancestry: list[ast.AST],
) -> WrapperMethod | None:
    kind = _method_kind(node, ancestry)
    wm = WrapperMethod(name=node.name, file=file_path, kind=kind)
    wm.params = {a.arg for a in node.args.args} | {a.arg for a in node.args.kwonlyargs}
    wm.params.discard("self")
    wm.params.discard("ctx")
    docstring = ast.get_docstring(node) or ""
    wm.docstring_args = _extract_documented_args(docstring)

    # Typed-passthrough detection: any param whose annotation resolves
    # to a proto-plus message class (or ``Optional[<MsgClass>]``,
    # ``<MsgClass> | None``) means the wrapper takes the whole submessage
    # as a typed value. Heuristic: the annotation references an
    # identifier or attribute chain that ends in an uppercase-leading
    # name (proto-plus convention) and isn't ``Dict``/``Mapping``/
    # ``Sequence``/``List`` etc. The param name doubles as the parent
    # resource's field name (every wrapper in this codebase preserves
    # field naming).
    for arg in (*node.args.args, *node.args.kwonlyargs):
        if arg.arg in {"self", "ctx"}:
            continue
        if _annotation_is_message_class(arg.annotation):
            wm.typed_passthrough.add(arg.arg)

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
        elif isinstance(sub, ast.Call):
            if isinstance(sub.func, ast.Attribute) and sub.func.attr in {
                "append",
                "extend",
                "MergeFrom",
                "CopyFrom",
                "add",
            }:
                p = _attr_chain(sub.func.value)
                if p:
                    wm.writes.add(p)
            # Detect proto-message kwargs constructor calls:
            # ``Resource(name=foo, value=customizer_value)`` — every kwarg
            # name corresponds to a proto field assignment. Heuristic: a
            # plain Name() call where the callee starts with an uppercase
            # letter (proto-plus convention) and there are kwargs.
            if (
                isinstance(sub.func, ast.Name)
                and sub.func.id
                and sub.func.id[0].isupper()
                and sub.keywords
            ):
                for kw in sub.keywords:
                    if kw.arg:
                        wm.writes.add(f"{sub.func.id}.{kw.arg}")
            # Dict-passthrough detection — both the single-submessage
            # helper and the repeated-submessage helper.
            if (
                isinstance(sub.func, ast.Name)
                and sub.func.id
                in {"set_optional_submessage", "extend_repeated_submessages"}
                and len(sub.args) >= 2
                and isinstance(sub.args[1], ast.Constant)
                and isinstance(sub.args[1].value, str)
            ):
                wm.dict_passthrough.add(sub.args[1].value)
    return wm


_MESSAGE_LIKE_BUILTINS = {
    "Optional",
    "Union",
    "List",
    "Sequence",
    "Iterable",
    "Mapping",
    "Dict",
    "Tuple",
    "Set",
    "FrozenSet",
    "Any",
    "Annotated",
    "Literal",
    "Type",
    "ClassVar",
    "Final",
    "Callable",
}


def _annotation_is_message_class(annotation: ast.AST | None) -> bool:
    """Return True if the annotation resolves to a proto-plus message class.

    Heuristic: the annotation contains at least one identifier (or
    attribute-chain leaf) that starts with an uppercase letter and isn't
    one of the typing-module builtins. ``Optional[ShoppingSetting]``,
    ``ShoppingSetting | None``, and bare ``ShoppingSetting`` all qualify;
    ``Optional[Dict[str, Any]]`` does not.
    """
    if annotation is None:
        return False
    found_message_like = False
    found_dict_like = False
    for node in ast.walk(annotation):
        if isinstance(node, ast.Name):
            n = node.id
            if n in {"Dict", "Mapping"}:
                found_dict_like = True
                continue
            if n in _MESSAGE_LIKE_BUILTINS:
                continue
            if n and n[0].isupper():
                found_message_like = True
        elif isinstance(node, ast.Attribute):
            if node.attr and node.attr[0].isupper():
                found_message_like = True
    # ``Optional[Dict[str, Any]]`` has Dict — not a message passthrough.
    return found_message_like and not found_dict_like


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
# Recursive submessage coverage (leaf-level audit)                            #
# --------------------------------------------------------------------------- #


@dataclass
class LeafField:
    """A scalar/enum/message-typed field somewhere inside a submessage tree."""

    path: tuple[str, ...]  # ("shopping_setting", "merchant_id")
    annotation: str  # output_only / immutable / required / input_only / settable
    in_md: bool
    in_proto: bool
    in_sdk: bool
    sources_agree: bool
    description: str = ""


@dataclass
class LeafCoverage:
    leaf: LeafField
    reachable: bool
    reach_mode: str  # "explicit" / "dict_passthrough" / "typed_passthrough" / ""


def _leaf_path_str(path: tuple[str, ...]) -> str:
    return ".".join(path)


def _ancestor_in_passthrough(
    path: tuple[str, ...], wrappers: list[WrapperMethod]
) -> str:
    """Return the reach mode if any ancestor in ``path`` is a passthrough.

    The first ancestor (path[0]) is the field name on the parent
    resource. Wrappers can mark *that* name as dict- or typed-
    passthrough, which transitively covers every descendant leaf.
    """
    if not path:
        return ""
    head = path[0]
    for wm in wrappers:
        if head in wm.dict_passthrough:
            return "dict_passthrough"
        if head in wm.typed_passthrough:
            return "typed_passthrough"
    return ""


def _wrapper_covers_leaf(path: tuple[str, ...], wrappers: list[WrapperMethod]) -> bool:
    """Explicit-write check at the leaf level.

    A leaf is reachable when any wrapper:

    1. **Full suffix match** — writes a path ending in the dotted leaf
       path (``<var>.text_ad.description1`` for leaf ``text_ad.description1``).
       This handles plain ``parent.sub.leaf = param`` assignments.

    2. **Entry-class build pattern** — writes the leaf-name on its own
       (``FrequencyCapEntry.cap`` from a ``FrequencyCapEntry(cap=...)``
       constructor, or ``fc.cap`` from a ``fc = parent.frequency_caps.add()``
       pattern) AND has a write referencing the top-level parent field
       (``campaign.frequency_caps``). This catches repeated-field
       building where leaf writes don't include the parent in their
       attribute chain.
    """
    full_suffix = "." + ".".join(path)
    full_path = ".".join(path)
    leaf = path[-1]
    parent = path[0]
    leaf_dot = "." + leaf
    for wm in wrappers:
        if any(w == full_path or w.endswith(full_suffix) for w in wm.writes):
            return True
        leaf_written = any(w == leaf or w.endswith(leaf_dot) for w in wm.writes)
        if leaf_written and any(parent in w.split(".") for w in wm.writes):
            return True
    return False


def merge_leaf_sources(
    sub_path: tuple[str, ...],
    sub_class: type,
    proto_text: str | None,
    proto_message_name: str,
) -> list[LeafField]:
    """Three-source triangulation for the fields inside one submessage.

    Like ``merge_field_sources`` but at the submessage level:
      * **Markdown** is the canonical inventory (devsite page).
      * **Proto** validates field-behavior annotations.
      * **SDK** confirms the field is reachable at runtime.

    Drops oneof / output-only fields when they're flagged that way in
    the markdown — same rules the top-level audit uses.
    """
    md_text = fetch_submessage_md(_qualified_md_name(sub_class))
    md_fields = parse_devsite_fields(md_text) if md_text else []
    proto_fields = (
        parse_proto_fields(proto_text, proto_message_name) if proto_text else []
    )
    proto_by_name = {f.name: f for f in proto_fields}
    try:
        sdk_field_set = set(sub_class.meta.fields.keys())
    except AttributeError:
        sdk_field_set = set()

    # Annotation pairs that the markdown and proto can legitimately
    # disagree on — same equivalences as ``merge_field_sources`` plus
    # one extra: Google often writes "Required." in the devsite prose
    # for submessage leaves but omits ``[(google.api.field_behavior) =
    # REQUIRED]`` from the proto (e.g. ``TargetRoas.target_roas``).
    # Trust the markdown as canonical and treat these as agreement.
    EQUIVALENT_ANNOTATIONS = {
        frozenset({"input_only", "immutable"}),
        frozenset({"required", "settable"}),
    }
    out: list[LeafField] = []
    for md in md_fields:
        pf = proto_by_name.get(md.name)
        in_proto = pf is not None
        in_sdk = md.name in sdk_field_set or f"{md.name}_" in sdk_field_set
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
            LeafField(
                path=sub_path + (md.name,),
                annotation=md.annotation,
                in_md=True,
                in_proto=in_proto,
                in_sdk=in_sdk,
                sources_agree=agree,
                description=md.description,
            )
        )
    # Fields that exist in proto/sdk but aren't on the markdown — rare
    # but worth tracking, since they indicate either a doc lag on
    # Google's side or a misclassified leaf. Mark them as
    # ``in_md=False`` so they aren't double-counted as "missing
    # somewhere" in the rollup.
    md_names = {f.path[-1] for f in out}
    for pf in proto_fields:
        if pf.name in md_names:
            continue
        out.append(
            LeafField(
                path=sub_path + (pf.name,),
                annotation=pf.behavior,
                in_md=False,
                in_proto=True,
                in_sdk=pf.name in sdk_field_set or f"{pf.name}_" in sdk_field_set,
                sources_agree=False,
            )
        )

    # Strip the proto-plus keyword-alias suffix when checking
    # cross-source presence: ``type_`` in the SDK is the same field as
    # ``type`` on the markdown / in the proto.
    def _alias(name: str) -> str:
        return name[:-1] if name.endswith("_") else name

    md_canon = {_alias(n) for n in md_names}
    proto_canon = {_alias(n) for n in proto_by_name}
    for sdk_name in sorted(sdk_field_set):
        canon = _alias(sdk_name)
        if canon in md_canon or canon in proto_canon:
            continue
        out.append(
            LeafField(
                path=sub_path + (sdk_name,),
                annotation="settable",
                in_md=False,
                in_proto=False,
                in_sdk=True,
                sources_agree=False,
            )
        )
    return out


def score_submessage_coverage(
    resource: str,
    resource_class: type,
    parent_proto_text: str | None,
    wrappers: list[WrapperMethod],
    parent_unified_fields: list[UnifiedField] | None = None,
) -> list[LeafCoverage]:
    """Recursively audit every reachable leaf inside resource submessages.

    For each top-level submessage field on the resource, descend through
    its message tree using SDK introspection. At each level, gather
    leaf inventory via three-source triangulation
    (``merge_leaf_sources``) and check reachability against the
    wrapper code (explicit writes or ancestor-level passthrough).

    Cycle protection: track visited ``module.qualname`` pairs per
    descent stack. The Google Ads schema doesn't have message cycles in
    practice, but the guard makes the audit defensive against future
    additions.
    """
    out: list[LeafCoverage] = []
    parent_proto_cache: dict[str, str | None] = {}
    if parent_proto_text is not None:
        parent_proto_cache[
            f"google/ads/googleads/{PROTO_VERSION}/resources/{_snake(resource)}.proto"
        ] = parent_proto_text

    def proto_for(cls: type) -> str | None:
        path = _proto_file_for_class(cls)
        if path is None:
            return None
        if path not in parent_proto_cache:
            parent_proto_cache[path] = fetch_common_proto_file(path)
        return parent_proto_cache[path]

    def descend(
        sub_field_name: str,
        sub_class: type,
        path: tuple[str, ...],
        visited: frozenset[str],
    ) -> None:
        cls_id = f"{sub_class.__module__}.{sub_class.__qualname__}"
        if cls_id in visited:
            return
        next_visited = visited | {cls_id}

        sub_proto = proto_for(sub_class)
        leaves = merge_leaf_sources(path, sub_class, sub_proto, sub_class.__qualname__)

        # Get this submessage's *own* submessage fields (for recursion)
        nested = dict(iter_submessage_fields(sub_class))

        # Submessages annotated output-only at this level should not be
        # descended into — their entire subtree is server-controlled
        # (policy summaries, system-set audit fields, etc.).
        output_only_nested = {
            leaf.path[-1]
            for leaf in leaves
            if leaf.annotation == "output_only" and leaf.path[-1] in nested
        }

        for leaf in leaves:
            leaf_name = leaf.path[-1]
            if leaf.annotation == "output_only":
                continue
            if leaf_name in nested:
                # Don't score the parent submessage itself; its scalars
                # appear when we recurse into it.
                continue
            mode = ""
            reachable = False
            anc_mode = _ancestor_in_passthrough(leaf.path, wrappers)
            if anc_mode:
                reachable = True
                mode = anc_mode
            elif _wrapper_covers_leaf(leaf.path, wrappers):
                reachable = True
                mode = "explicit"
            out.append(LeafCoverage(leaf=leaf, reachable=reachable, reach_mode=mode))

        for nested_name, nested_class in nested.items():
            if nested_name in output_only_nested:
                continue
            descend(nested_name, nested_class, path + (nested_name,), next_visited)

    # Annotation map from the parent resource's already-triangulated
    # fields. Used to skip output-only top-level submessages — descending
    # into a server-controlled subtree generates noise without
    # surfacing real gaps.
    top_level_annotations: dict[str, str] = {}
    if parent_unified_fields:
        for f in parent_unified_fields:
            top_level_annotations[f.name] = f.annotation
    for top_name, top_class in iter_submessage_fields(resource_class):
        if top_level_annotations.get(top_name) == "output_only":
            continue
        descend(top_name, top_class, (top_name,), frozenset())
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
    leaf_coverage: list[LeafCoverage] = field(default_factory=list)
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
    leaves_total = 0
    leaves_reachable = 0
    leaves_disagreement = 0
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
        for lc in r.leaf_coverage:
            leaves_total += 1
            if lc.reachable:
                leaves_reachable += 1
            if not lc.leaf.sources_agree and (
                lc.leaf.in_md or lc.leaf.in_proto or lc.leaf.in_sdk
            ):
                leaves_disagreement += 1

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
    lines.append(
        f"- Submessage leaves reachable: **{leaves_reachable} / {leaves_total}** ({_pct(leaves_reachable, leaves_total)})"
    )
    lines.append(f"- Submessage leaf source disagreements: **{leaves_disagreement}**")
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
    # Submessage-leaf callout
    if r.leaf_coverage:
        total = len(r.leaf_coverage)
        reachable = sum(1 for lc in r.leaf_coverage if lc.reachable)
        out.append("")
        out.append(
            f"**Submessage leaves**: {reachable}/{total} reachable "
            f"({_pct(reachable, total)})"
        )
        unreach = [lc for lc in r.leaf_coverage if not lc.reachable]
        if unreach:
            out.append("")
            out.append("Unreachable leaves:")
            for lc in unreach:
                out.append(
                    f"- `{_leaf_path_str(lc.leaf.path)}` — "
                    f"{_emoji(lc.leaf.annotation)} {lc.leaf.annotation}"
                )
        leaf_disagreements = [
            lc
            for lc in r.leaf_coverage
            if not lc.leaf.sources_agree
            and (lc.leaf.in_md or lc.leaf.in_proto or lc.leaf.in_sdk)
        ]
        if leaf_disagreements:
            out.append("")
            out.append("Leaf source disagreements:")
            for lc in leaf_disagreements:
                sources = []
                if lc.leaf.in_md:
                    sources.append("md")
                if lc.leaf.in_proto:
                    sources.append("proto")
                if lc.leaf.in_sdk:
                    sources.append("sdk")
                out.append(
                    f"- `{_leaf_path_str(lc.leaf.path)}` — only in: "
                    + "/".join(sources)
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
        sdk_class = load_sdk_class(resource)
        leaf_coverage = (
            score_submessage_coverage(
                resource, sdk_class, proto_text, wrappers, unified
            )
            if sdk_class is not None
            else []
        )

        reports.append(
            ServiceReport(
                service=svc,
                resource=resource,
                wrapper_file=wrapper_file,
                fields=coverage,
                mcp_tools=mcp_tools,
                docstring_findings=d_findings,
                leaf_coverage=leaf_coverage,
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
