# Troubleshooting

[← Skinning docs](index.md)

Skin Shortcuts shows a notification when it hits a problem in your config and writes the specifics to the Kodi log. This page covers how to read those and what each notification means.

## Getting the detail

Every error notification has its specifics (which file, which name) in the log. To surface them:

- **Skin Shortcuts' own Debug setting** promotes its messages into a normal log without turning on full Kodi debug logging. Handy while building a skin.
- **Kodi debug logging** captures everything, including other add-ons. Use it when the Skin Shortcuts messages alone don't explain the problem, for example when another add-on is involved.

Enable either, reproduce the problem, then read the log.

Notifications appear once per problem per run, so a mistake repeated across items shows a single toast; the log lists each occurrence.

## Error notifications

| Notification | Cause | Fix |
|---|---|---|
| Shortcut / Widget / Background Group Error: Group missing 'name' | A group in the picker groupings has no `name` attribute | Add `name="..."` to the group |
| Shortcut / Widget / Background Group Error: '\<name>' missing label | A group has a name but no `label`, required unless the group is `flat` | Add `label="..."`, or mark it `flat="true"` |
| Background Config: '\<name>' has both `path` and `source` | A browse or multi background defines both; the fixed path is ignored | Keep one: a fixed `<path>` or a dynamic `<source>` |
| Submenu Template Error: menu '\<name>' not found | A submenu template references a named menu that isn't defined | Correct the name, or define that menu in `menus.xml` |
| Items Template Error: '\<name>' not defined | A `<skinshortcuts insert="...">` references an items template that doesn't exist | Define the items template, or correct the insert name |
| Expression Error: $MATH failed: \<expr> | A `$MATH[...]` expression has invalid syntax | Fix the expression, checking operators and parentheses |
