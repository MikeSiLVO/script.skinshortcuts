# Troubleshooting

[← Skinning docs](index.md)

Skin Shortcuts shows a notification when it hits a problem in your config and writes the specifics to the Kodi log. This page covers how to read those and what each notification means.

## Getting the detail

Every error notification ends in "(see log)". Its log line is in the normal Kodi log, with or without debug logging, and gives the file, what was written, what Skin Shortcuts did and how to fix it.

A notification and its log line appear once per problem in each run, so a mistake repeated across items shows one toast and one log line.

For problems that show no notification:

- **Skin Shortcuts' own Debug setting** promotes its messages into a normal log without turning on full Kodi debug logging. Handy while building a skin.
- **Kodi debug logging** captures everything, including other add-ons. Use it when the Skin Shortcuts messages alone don't explain the problem, for example when another add-on is involved.

Enable either, reproduce the problem, then read the log.

## Error notifications

| Notification | Cause | Fix |
|---|---|---|
| \<Feature> Error: '\<name>' missing \<field>, or \<element> missing '\<field>' | A menu, item, widget, background, property, button, fallback, view, content rule, template, preset or group has no attribute or element it needs; it is skipped | Add what the log line names |
| Property Button Error: '\<id>' is not a control id | A `<button>` in `properties.xml` has an id that is not a number; it is skipped | Use the id of the dialog control |
| View Error: '\<name>' lists no defined view | No id in a content rule's `<views>` is a defined view; the rule is skipped | List the ids of defined views |
| View Error: '\<name>' library view / plugin view not defined | A content rule's `library` or `plugin` default is not a defined view; a bad `library` skips the rule, a bad `plugin` is ignored | Use a defined view id |
| Shortcut / Widget / Background Group Error: '\<name>' missing label | A group has a name but no `label`, required unless the group is `flat` | Add `label="..."`, or mark it `flat="true"` |
| Background Error: '\<name>' has path and source | A browse or multi background defines both; the fixed path is ignored | Keep one: a fixed `<path>` or a dynamic `<source>` |
| Background Error: '\<group>' uses \<content> | backgrounds.xml has a `<content>` element, in a group or at the root (named `backgrounds`); it is skipped | Use a playlist or browse background with `<source>` instead |
| Property Button Error: '\<name>' not defined | A `<button>` in `properties.xml` points at a property that has no `<property>` definition | Define the property, or correct the button's `property` attribute |
| Submenu Template Error: menu '\<name>' not found | A submenu template references a named menu that isn't defined | Correct the name, or define that menu in `menus.xml` |
| Template Error: raw template '\<name>' has \<variables> / \<variableGroup> / \<skinshortcuts include> | A `build="true"` template declares `<variables>`, a `<variableGroup>` reference or a `<skinshortcuts include>` marker, which raw templates do not build | Move variables to a menu template; use a Kodi `<include>` in place of the marker |
| Include Error: '\<name>' not defined | A `<skinshortcuts include="...">` names an include that isn't in `<includes>` | Define the include, or correct the name (the log suggests a close match) |
| Template Error: menu '\<name>' has no container | A visibility marker, or a `build="true"` template with `menu=`, reads a menu without `container` | Add `container="<list id>"` to that `<menu>` in `menus.xml` |
| Submenu Template Error: '\<name>' uses \<feature> | A submenu template contains an element, a `$IF`/`$PARENT` reference or a `<skinshortcuts include>` it does not build | Use what [Supported Content](templates.md#supported-content) lists, or move it to a menu template |
| Submenu Template Error: '\<name>' variableGroups are not built | An items template with `<variableGroup>` references is inserted by a submenu template, which builds no variables | Insert it from a menu template |
| Submenu Template Error: '\<name>' condition has no item to test | An items template with a `<condition>` is inserted by a named `<submenu>`, which has no parent item; the condition is ignored | Insert it from a level-based submenu template or a menu template |
| Items Template Error: '\<name>' not defined | A `<skinshortcuts insert="...">` references an items template that doesn't exist | Define the items template, or correct the insert name |
| Items Template Error: '\<name>' uses suffix= | A `<preset>`, `<propertyGroup>` or `<variableGroup>` inside `<template items="...">` has `suffix=`, which is ignored there since submenu items have no slots | Remove `suffix=` |
| Expression / Include / Variable Group Error: '\<name>' is circular | A `$EXP`, `<skinshortcuts include>` or `<variableGroup>` reaches itself through other references; the log lists the loop | Remove one reference in the loop |
| Expression Error: $MATH failed | A `$MATH[...]` expression has invalid syntax or divides by zero | Fix the expression shown in the log line, checking operators and parentheses |
| Expression Error: $IF clause has no THEN | A `$IF[...]` clause has no uppercase `THEN`, often a lowercase or misspelled keyword | Write `THEN`, `ELIF` and `ELSE` in uppercase |
| Menu / Widget / Background / View Error: '\<name>' defined twice | Two menus, widgets, backgrounds or views share a name or id; only one can be reached | Give each a unique name |
| Menu Error: item '\<name>' defined twice in menu '\<menu>' | Two items in one menu share a name | Give each item a unique name |
| View Error: content '\<name>' defined twice | Two content rules in `views.xml` share a name | Give each rule a unique name |
| Template / Items Template / Submenu Template Error: '\<name>' defined twice | A `<var>` shares its name with another `<var>`, or with `<property>` elements, in the same template, property group, items or submenu template; the first definition is used | Keep one `<var>`, or only `<property>` elements |
| Override Error: '\<name>' replaces itself / points at undefined '\<name>' / names a picker-owned key / is still defined | An entry in an `<overrides>` block would put user data somewhere the skin cannot use; it is ignored | See [What Is Refused](overrides.md#what-is-refused) |
