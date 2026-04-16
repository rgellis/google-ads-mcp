# Code Standards Checklist

Standardization tasks to unify all 113 services to a single, consistent architecture.

**Created:** 2026-04-15

---

## 1. Unify service architecture (15 services need migration)

All services should follow Pattern A: async methods with `ctx: Context`, error handling with `GoogleAdsException`, and the `create_*_tools()` + `register_*_tools()` factory pattern.

These 15 services currently use Pattern B (sync methods, no ctx, no error handling):

- [x] `src/services/campaign/experiment_arm_service.py` **DONE**
- [x] `src/services/ad_group/ad_group_customizer_service.py` **DONE**
- [x] `src/services/ad_group/ad_group_criterion_label_service.py` **DONE**
- [x] `src/services/assets/asset_group_signal_service.py` **DONE**
- [x] `src/services/assets/customer_asset_service.py` **DONE**
- [x] `src/services/account/customer_customizer_service.py` **DONE**
- [x] `src/services/campaign/campaign_asset_set_service.py` **DONE**
- [x] `src/services/product_integration/product_link_service.py` **DONE**
- [x] `src/services/planning/brand_suggestion_service.py` **DONE**
- [x] `src/services/planning/keyword_plan_ad_group_service.py` **DONE**
- [x] `src/services/planning/keyword_plan_ad_group_keyword_service.py` **DONE**
- [x] `src/services/planning/keyword_plan_campaign_service.py` **DONE**
- [x] `src/services/planning/keyword_plan_campaign_keyword_service.py` **DONE**
- [x] `src/services/conversions/custom_conversion_goal_service.py` **DONE**
- [x] `src/services/conversions/conversion_goal_campaign_config_service.py` **DONE**

**For each service, migrate to:**
```python
class FooService:
    def __init__(self) -> None:
        self._client: Optional[FooServiceClient] = None

    @property
    def client(self) -> FooServiceClient:
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("FooService")
        assert self._client is not None
        return self._client

    async def do_something(
        self, ctx: Context, customer_id: str, ...
    ) -> Dict[str, Any]:
        try:
            customer_id = format_customer_id(customer_id)
            # ... build request ...
            set_request_options(request, ...)
            response = self.client.mutate_foo(request=request)
            await ctx.log(level="info", message="...")
            return serialize_proto_message(response)
        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to ...: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
```

---

## 2. Eliminate server boilerplate with factory function

Replace 113 identical server files with a single factory in `src/servers/__init__.py`:

```python
def create_server(register_fn: Callable) -> FastMCP[Any]:
    server = FastMCP[Any]()
    register_fn(server)
    return server
```

Then each server file becomes:
```python
from src.servers import create_server
from src.services.campaign.campaign_service import register_campaign_tools
campaign_server = create_server(register_campaign_tools)
```

**Or** eliminate server files entirely and build the mapping in `main.py` directly.

- [ ] Create `create_server()` factory in `src/servers/__init__.py`
- [ ] Update all 113 server files to use the factory
- [ ] OR eliminate server files and create servers inline in main.py

---

## 3. Standardize server initialization

All servers should use `FastMCP[Any]()` consistently (not bare `FastMCP()`).

- [ ] Normalize all server files to `FastMCP[Any]()`

---

## 4. Reduce tool wrapper duplication

The `create_*_tools()` functions duplicate every parameter from the service class method. Consider a decorator or generic wrapper that auto-generates the tool function from the service method signature.

Option A — Thin wrappers that only do enum conversion:
```python
async def create_campaign(ctx, customer_id, name, ..., status="PAUSED"):
    status_enum = getattr(CampaignStatusEnum.CampaignStatus, status)
    return await service.create_campaign(ctx=ctx, ..., status=status_enum)
```

Option B — Auto-generate tool wrappers from service method signatures (more complex, less explicit).

- [ ] Evaluate whether auto-generation is worth the complexity
- [ ] If not, ensure all tool wrappers are consistently thin (enum conversion only)

---

## 5. Standardize `__init__.py` files

Either use them consistently for re-exports or keep them empty. Currently they vary from 7 to 81 lines with no clear pattern.

- [ ] Decide: re-export from `__init__.py` or keep empty
- [ ] Standardize all `__init__.py` files to match

---

## 6. Standardize error handling

All service methods should follow the same error handling pattern:
```python
except GoogleAdsException as e:
    error_msg = f"Google Ads API error: {e.failure}"
    await ctx.log(level="error", message=error_msg)
    raise Exception(error_msg) from e
except Exception as e:
    error_msg = f"Failed to {action}: {str(e)}"
    await ctx.log(level="error", message=error_msg)
    raise Exception(error_msg) from e
```

- [ ] Verify all 98 Pattern A services follow this exactly
- [ ] Migrate all 15 Pattern B services to include this

---

## 7. Standardize logging

All mutate/create/update/remove operations should log on success:
```python
await ctx.log(level="info", message=f"Created campaign '{name}'")
```

- [ ] Audit all services for consistent success logging
- [ ] Add missing log calls where operations succeed silently

---

## Priority Order

1. **Item 1** (unify 15 services) — highest impact, fixes missing error handling and logging
2. **Item 6** (error handling) — comes naturally with item 1
3. **Item 2** (server factory) — reduces 113 files of boilerplate
4. **Item 3** (server init) — trivial, do alongside item 2
5. **Item 5** (__init__.py) — low impact, clean up
6. **Item 4** (tool wrapper dedup) — evaluate ROI before doing
7. **Item 7** (logging) — nice to have
