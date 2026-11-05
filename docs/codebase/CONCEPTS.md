# Concepts

Rules that span several modules and that no single file shows. Each section names the code that carries the rule; the docstrings there hold the detail. File layouts are in [FORMATS.md](FORMATS.md).

## Skin defaults, the working copy and the userdata diff

- menus.xml is the source of truth. `SkinConfig.default_menus` keeps the parsed menus untouched; `SkinConfig.menus` holds them merged with the user's changes.
- Userdata stores only differences: per menu, the changed and added items, and the names of default items the user deleted (`MenuDiff`, `MenuItemDiff`).
- `merge_items` applies a diff: it drops deleted defaults (a `required` item always stays), overlays the changed fields, appends user-added items, then puts each item that has a `position` at that index and fills the gaps with the rest in order.
- The management dialog never edits userdata. `MenuManager` copies `config.menus` into `working`, a dict of `Menu` by name; every edit goes to `working`; `save()` diffs `working` against the skin defaults (`_generate_userdata`) and writes the result. An item equal to its default leaves no entry and an unchanged menu leaves no key.
- A menu save carries over the loaded `views` untouched, since view selections are edited outside the dialog.
- The dialog's `items` list is the manager's working list itself, so manager edits show on the next list rebuild without a reload.
- An empty menu shows a placeholder item (`MenuItem.is_placeholder`). Placeholders never reach userdata, and any edit to one clears the flag.

## Derived widget and background properties

- An item stores a chosen widget or background by name, in `widget` or `background` and their slots. The siblings (`widgetLabel`, `widgetPath`, `widgetType`, `widgetTarget`, `widgetSource`, `widgetLimit`, `widgetSortBy`, `widgetSortOrder`, `backgroundLabel`, `backgroundPath`, `backgroundType`) can be derived from that definition in widgets.xml or backgrounds.xml (`SkinConfig.derived_item_properties`).
- `SkinConfig.resolve_item_properties` fills the siblings an item does not set, at build time and when the manager builds its working copy. Values the item sets win; siblings of the menu's default widget or background then fill slots the item leaves empty.
- When the user picks, the dialog writes the full sibling set (`PropertiesMixin._set_widget_properties`). On save, `MenuManager._diff_item` leaves out siblings that equal the derived values, but only in slots still holding the skin default's pick. A skin update to a default widget therefore reaches users, while a widget the user picked keeps the values stored at pick time.

## Items a visible= condition hides

- The `visible` attribute on a menus.xml item (`MenuItem.dialog_visible`) is tested against Kodi when config loads. `merge_menu` leaves out items whose condition fails, so they are absent from the includes and from the dialog. The `<visible>` child element (`MenuItem.visible`) is different: it is written into the includes for Kodi to evaluate.
- `merge_items` keeps hidden items, so stored positions count them.
- `MenuManager` records each menu's hidden items at load (`_hidden_items`) and puts each back after the nearest item it followed before diffing (`_with_hidden`). A save therefore keeps their stored edits, deletions and positions.
- The restore picker skips a deleted default whose condition currently fails (`get_removed_items`).
- The hashes file records the result of every visible= condition, so a result that flips makes the next `buildxml` rebuild.

## Per-item submenus

- Every item of a root menu can have its own submenu, keyed `{menu}/{item}` (`submenu_key` in `models/menu.py`). The key is used as a menu name in `SkinConfig.menus`, in the manager's `working` and in userdata.
- A menus.xml `<submenu>` is a template, not a menu the user edits. An item links one through `MenuItem.submenu`: the `submenu` attribute, or the shortcut picker when the picked shortcut's name matches a `<submenu>` ([auto-link](../skinning/menus.md#auto-link-by-shortcut-name)).
- `SkinConfig.load` builds each instance by merging the template with the userdata diff stored under the item's key, and records the template in `Menu.template_origin`. An item with no template but a stored diff gets an instance built from the diff alone. A `<submenu>` that any item links is left out of `config.menus`; one that no item links stays in as an ordinary flat menu.
- The manager seeds an instance from the template when the dialog opens an item that has none yet (`ensure_item_submenu`), discards it when the item's template changes (`drop_item_submenu`), and diffs it against the template on save.
- Submenus are one level deep: only root menu items get instances, and the dialog refuses to open a submenu from a submenu.
- Output: `skinshortcuts-{menu}-submenu` combines a root menu's instances, and each linked template also gets `skinshortcuts-{template}` unless it sets `standalone="false"` ([FORMATS.md](FORMATS.md#generated-includes)).
- Items templates in templates.xml (`<skinshortcuts insert>`) read flat menus named `{item}.{source}`, such as `movies.widgets`, not the per-item keys.

## Custom widget menus

- A custom widget is a menu of shortcuts the user builds for one widget slot. Its name is `custom-` plus 8 hex characters (`MenuManager.create_custom_widget_menu`), and the owning item points at it through `customWidget` for the base slot or `customWidget.N` for slot N.
- The menu is created the first time the reference `{customWidget}` or `{customWidget.N}` is resolved, from a subdialog's `menu` or an onclose `menu` action (`SubdialogsMixin._resolve_menu_reference`). The forms `{item}.customwidget` and `{item}.customwidget.N` resolve the same way. A bare `{customWidget}` takes its slot from the subdialog's `suffix`.
- Picking an ordinary widget for a slot, or clearing the slot, empties that slot's custom menu and drops the reference (`MenuManager.clear_custom_widget`). `type=clear` does the same from a RunScript call (`entry.clear_custom_widget`).
- `SkinConfig.load` gives a `custom-` menu from userdata `menu_type="widgets"`. A save drops every menu the skin does not define that nothing references through a `customWidget` property, a per-item key or a `{item}` subdialog menu (`_cleanup_orphaned_menus`).
- Output: `skinshortcuts-{item}-customwidget` and `skinshortcuts-{item}-customwidget{N}` for root menu items whose custom menu has items. Skinner view: [Custom Widgets](../skinning/widgets.md#custom-widgets).

## Property slots and suffixes

- A slot is a numbered copy of a property: `widget` is the base slot, `widget.2` slot 2, and every sibling takes the same tail (`widgetPath.2`). Slots let one item hold several widgets or backgrounds.
- In the dialog, a subdialog with `suffix=".2"` opens a child on the same menu with that `property_suffix`. A property button with `suffix="true"` appends it to its property name and its `requires` check. Fallback rules, context menu rows and a suffixed button's options suffix their conditions too (`suffix_condition`).
- In templates, an output with a suffix applies it to every condition (`suffix_condition`) and every `from` source (`suffix_property`) the template reads. Built-in names (`NO_SUFFIX_PROPERTIES` in conditions.py), names that already carry a slot, and `{NOSUFFIX:...}` content from a `noSuffix` expression stay as written.
- `slot_suffixes` lists the slots an item holds; custom widget includes and `<value iterate>` use it.

Skinner view: [Suffix Transforms](../skinning/properties.md#suffix-transforms).

## Property names ignore case

- Conditions, the includes builder and the template builder read properties through `conditions.lookup` (exact name first, then ignoring case) and `with_defaults`.
- The dialog writes a property under the spelling properties.xml declares (`PropertySchema.declared_name`), so stored keys keep the skin's spelling.
- A built-in output property (`id`, `name`, `menu`, `action`, `path`, `submenuVisibility`, `hasSubmenu`) that the item also sets, in any case, takes the item's value.

## Overrides and retired names

Three kinds of `<overrides>`, each applied at a different point.

- **Retired names** (`migrations.py`): properties.xml, widgets.xml and backgrounds.xml can list `<property>`, `<widget>` or `<background>` entries with a `replace` attribute (`loaders.base.parse_name_overrides`). `apply_overrides` runs inside `SkinConfig.load` and rewrites the loaded userdata: a property override renames the stored key and its slots, a widget or background override points stored names at the replacement and drops the siblings the new definition supplies, and an empty value clears. It refuses an override that targets an undefined name, replaces itself, or whose old name the skin still defines, and a property override that names a key the script writes itself (`migrations.RESERVED`). It repeats up to five passes so chained renames settle. `build_includes` saves the rewritten userdata when anything changed. Skinner view: [Retired Names](../skinning/overrides.md).
- **Action overrides** (menus.xml `<overrides><action replace>`): applied at build time to copies of the menus (`config._apply_action_overrides`), one hop per action and matched ignoring case. Userdata and the dialog keep the original action. Skinner view: [Action Overrides](../skinning/menus.md#action-overrides).
- **Icon overrides** (menus.xml `<overrides><icons>`): `IconOverrides` maps Kodi `Default*.png` names to skin files, from explicit entries or from a `<source>` folder when the skin has a file of that name. Loaders apply it to default icons as they parse, and the content and browse providers apply it to the icons they return. Skinner view: [Icon Overrides](../skinning/menus.md#icon-overrides).

## View locking

- views.xml (`ViewConfig`) defines views and content rules: a Kodi condition that detects the content, the views it allows, a library default and an optional plugin default.
- The user's choices live in userdata `views`: per content, one for `library`, one for `plugins` in general, and overrides per plugin id ([FORMATS.md](FORMATS.md#views)).
- `ViewExpressionBuilder` turns the effective choice per content into Kodi `<expression>` elements in the includes file, one combined condition per view, which the skin uses to show its view containers. Expression names are listed in [Generated Expressions](../skinning/views.md#generated-expressions).
- `type=viewselect` edits the choices through `dialog/views.py`, saves the userdata and forces a build; `type=resetviews` clears them. A menu save never touches them.

## Template builder stages

How templates.xml turns into includes is on its own page: [builders/template.md](builders/template.md).
