# Retired Names

When you rename or drop a widget, background or property, users who already picked the old one still have it stored. An `<overrides>` block tells the script where that name went, so their saved menus follow the change instead of pointing at something the skin no longer defines.

---

## Table of Contents

* [File Structure](#file-structure)
* [Renaming](#renaming)
* [Retiring](#retiring)
* [What Is Refused](#what-is-refused)
* [When It Runs](#when-it-runs)
* [Numbered Slots](#numbered-slots)
* [Leaving the Block In Place](#leaving-the-block-in-place)
* [What It Does Not Reach](#what-it-does-not-reach)

---

## File Structure

Each file declares retired names for the things it defines, in a block at the top:

```xml
<widgets>
  <overrides>
    <widget replace="recentmovies">recentlyaddedmovies</widget>
  </overrides>

  <widget name="recentlyaddedmovies" label="$LOCALIZE[20386]">
    <path>videodb://recentlyaddedmovies/</path>
  </widget>
</widgets>
```

| File | Element | Applies to |
|------|---------|------------|
| `widgets.xml` | `<widget>` | A stored widget name |
| `backgrounds.xml` | `<background>` | A stored background name |
| `properties.xml` | `<property>` | A stored property name |

`menus.xml` has its own `<overrides>` block for [actions](menus.md#action-overrides) and [icons](menus.md#icon-overrides), which work differently: they substitute at build time and never change what is stored.

---

## Renaming

The `replace` attribute is the old name, the element text is the new one:

```xml
<backgrounds>
  <overrides>
    <background replace="kodi-movie-fanart">movie-fanart</background>
  </overrides>
</backgrounds>
```

Any item storing `kodi-movie-fanart` now stores `movie-fanart`. The path and type the picker baked in are dropped so they come back from the new definition. A label the user typed is kept.

Property renames move the stored key:

```xml
<properties>
  <overrides>
    <property replace="widgetStyle">listStyle</property>
  </overrides>
</properties>
```

---

## Retiring

An empty element clears the stored value instead of moving it. Use it when a name is gone with nothing to point it at:

```xml
<overrides>
  <widget replace="recentmovies">recentlyaddedmovies</widget>
  <widget replace="discontinuedwidget"></widget>
</overrides>
```

The item keeps its place in the menu, and the retired value is cleared along with the keys the picker wrote beside it.

---

## What Is Refused

An override is ignored, with an error in the log, when it would put user data somewhere the skin cannot use:

* the name it points at is not defined by the skin
* the name it replaces is still defined by the skin, which reads as a typo rather than a rename
* it names one of the keys the widget and background pickers own, such as `widgetPath` or `background`
* it replaces a name with itself

Rename in one hop. If something was renamed twice, point the older entry at the current name rather than chaining one entry to another, since the intermediate name no longer exists for the script to check against.

---

## When It Runs

Overrides apply during a rebuild, and the rebuild that applies them is the one triggered by the config file you just edited. Adding the block is itself the change that causes the build.

Userdata is rewritten once, after the includes are built. A stored name is only ever read as the old one until then, so nothing is lost if a build fails partway.

---

## Numbered Slots

A skin that offers several widget or background slots stores them as `widget`, `widget.2`, `widget.3`. Overrides cover every slot, so one declaration is enough:

```xml
<overrides>
  <widget replace="recentmovies">recentlyaddedmovies</widget>
</overrides>
```

This moves `widget`, `widget.2` and any other slot holding that name. The same applies to a property rename, which moves `widgetStyle.2` along with `widgetStyle`.

Names are matched whole. A rename of `widgetStyle` leaves `widgetStyleExtra` alone.

---

## Leaving the Block In Place

An override only does something when a stored name still matches. Once every user has rebuilt, it does nothing, and running it again changes nothing.

That means there is no point at which the block must be removed, and no harm in keeping it. Drop it when you are confident nobody is still holding the old name, or leave it as a record of the rename.

Values are matched exactly, including case.

---

## What It Does Not Reach

An override moves a stored name. It does not touch anything the user chose for themselves, which means some things stay as they are:

**A widget the user added.** The picker offers every installed add-on, so a user can build a widget the skin never shipped. Retiring your own definition leaves theirs alone, by design.

**A widget list entry.** In a widget submenu each entry is a menu item named after the widget, not a stored `widget` value, so an override does not reach it. A retired widget already added to such a list keeps working from what the picker baked into it.

**A user-supplied path.** A browsed image, a chosen folder and a picked playlist are stored as the user's own values and are never rewritten.

Retiring a name still clears it and the keys the picker wrote beside it, so a retired widget or background does leave the slot empty.

A rename covers numbered slots the same way. An image or folder the user browsed to is stored as the value itself, so no override can reach it.

---

> **See also:**
> - [Widgets](widgets.md) for widget definitions
> - [Backgrounds](backgrounds.md) for background definitions
> - [Properties](properties.md) for property definitions
> - [Action Overrides](menus.md#action-overrides) for replacing changed actions
