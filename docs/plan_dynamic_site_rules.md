# Plan: Dynamic Site Parsing Configuration

## Context

Currently colusa only supports new websites via Python plugins in the source tree. This change lets users declare CSS-selector-based parsing rules in their book config (or a separate file) so they can handle unsupported sites without touching colusa's code. Dynamic rules take priority over built-in plugins.

---

## Files to Modify

| File | Change |
|------|--------|
| `src/colusa/config.py` | Add `SiteRule` dataclass and `_parse_site_rule()`; add `site_rules` and `site_rules_file` to `BookConfig` |
| `src/colusa/etr.py` | Add `DynamicExtractor` class |
| `src/colusa/colusa.py` | Load rules at startup; match rules before plugin registry in `ebook_generate_content` |

---

## Detailed Changes

### 1. `config.py` — Add `SiteRule`

```python
@dataclass
class SiteRule:
    pattern: str
    content: Optional[str] = None
    title: Optional[str] = None
    author: Optional[str] = None
    published: Optional[str] = None
    cleanup: list[str] = field(default_factory=list)


def _parse_site_rule(d: dict[str, Any]) -> SiteRule:
    return SiteRule(
        pattern=d['pattern'],
        content=d.get('content'),
        title=d.get('title'),
        author=d.get('author'),
        published=d.get('published'),
        cleanup=d.get('cleanup', []),
    )
```

Add to `BookConfig` fields:
```python
site_rules: list[SiteRule] = field(default_factory=list)
site_rules_file: str = ''
```

In `from_dict()`:
```python
site_rules=[_parse_site_rule(r) for r in data.get('site_rules', [])],
site_rules_file=data.get('site_rules_file', ''),
```

---

### 2. `etr.py` — Add `DynamicExtractor`

Add after the base `Extractor` class. Extend the import from `.config` to include `SiteRule`.

```python
class DynamicExtractor(Extractor):
    """Extractor driven by user-supplied CSS selectors from a SiteRule."""
    def __init__(self, bs: BeautifulSoup, rule: 'SiteRule') -> None:
        super().__init__(bs)
        self._rule = rule

    def _find_main_content(self) -> Optional[Tag]:
        if self._rule.content:
            tag = self.bs.select_one(self._rule.content)
            if tag is not None:
                return tag
        return super()._find_main_content()

    def _parse_title(self) -> str:
        if self._rule.title:
            tag = self.bs.select_one(self._rule.title)
            if tag is not None:
                return tag.get_text(strip=True)
        return super()._parse_title()

    def _parse_author(self) -> str:
        if self._rule.author:
            tag = self.bs.select_one(self._rule.author)
            if tag is not None:
                return tag.get_text(strip=True)
        return super()._parse_author()

    def _parse_published(self) -> str:
        if self._rule.published:
            tag = self.bs.select_one(self._rule.published)
            if tag is not None:
                return tag.get_text(strip=True)
        return super()._parse_published()

    def cleanup(self) -> None:
        super().cleanup()
        if self.main_content is None:
            return
        for selector in self._rule.cleanup:
            for el in self.main_content.select(selector):
                el.decompose()
```

---

### 3. `colusa.py` — Load rules and match before plugins

#### 3a. Import `SiteRule`
```python
from colusa.config import BookConfig, MakeConfig, UrlEntry, SiteRule
```

#### 3b. Module-level helper to load an external rules file
```python
def _load_rules_file(path: str) -> list[SiteRule]:
    from colusa.config import _parse_site_rule
    p = pathlib.PurePath(path)
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f) if p.suffix == '.yml' else json.load(f)
    return [_parse_site_rule(r) for r in (data or [])]
```

#### 3c. `Colusa.__init__` — accept optional `config_file_dir`, load rules
```python
def __init__(self, configuration, config_file_dir: str = '') -> None:
    ...
    self.site_rules: list[SiteRule] = self._load_site_rules(config_file_dir)
```

```python
def _load_site_rules(self, config_file_dir: str) -> list[SiteRule]:
    rules = list(self.config.site_rules)
    rules_file = self.config.site_rules_file
    if rules_file:
        if not os.path.isabs(rules_file) and config_file_dir:
            rules_file = os.path.join(config_file_dir, rules_file)
        rules.extend(_load_rules_file(rules_file))
    return rules
```

#### 3d. `generate_book` — pass config directory
```python
config_dir = str(pathlib.Path(config_file_path).parent)
with Colusa(configs, config_file_dir=config_dir) as s:
```

#### 3e. `_match_site_rule()` helper
```python
def _match_site_rule(self, url_path: str) -> Optional[SiteRule]:
    import re
    for rule in self.site_rules:
        if re.search(rule.pattern, url_path):
            return rule
    return None
```

#### 3f. `ebook_generate_content()` — check dynamic rules before plugin registry

Replace the `etr.create_extractor(...)` call with:

```python
rule = self._match_site_rule(url_path)
if rule:
    extractor = etr.DynamicExtractor(bs, rule)
    extractor.url_path = url_path
    extractor.cached_path = os.path.join(self.output_dir, '.cached')
else:
    extractor = etr.create_extractor(bs, url_path, os.path.join(self.output_dir, '.cached'))
```

---

## Verification

1. **Content selector**: Add a `site_rules` entry with `content` pointing to a real CSS selector; confirm the correct element is extracted.
2. **Metadata selectors**: Set `title`/`author`/`published` selectors; confirm rendered chapter header shows the right values.
3. **Cleanup rules**: Set `cleanup` selectors targeting ad/nav divs; confirm those elements are absent from the AsciiDoc output.
4. **Fallback on no match**: Use a `content` selector that matches nothing; confirm colusa falls back to built-in detection without error.
5. **External rules file**: Set `site_rules_file` pointing to a `.yml` file; confirm rules are loaded and applied.
6. **Priority over plugins**: Add a rule for a domain that has a built-in plugin; confirm the dynamic rule is used instead.
7. **Backward compat**: Configs without `site_rules` or `site_rules_file` continue to work unchanged.
8. **Run tests**: `pytest --no-cov` — all existing tests pass.
