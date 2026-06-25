Input data sources:

https://docs.google.com/spreadsheets/d/1uWwczLxgbpWMmXycL8Thq5NVExzlib4A/edit?pli=1&gid=1187300939#gid=1187300939

Sheets:

`Marker Combinations` is our master for SOULCAP cell type definition by negative positive cell flow cytometry markers

`Citation Mgr` contains reference papers by major cell type.


Marker syntax (for the `Marker Combinations` sheet) is now specified in full in
MARKER_SYNTAX.md — both a human-readable guide and a formal EBNF grammar.

Quick reference:

`live/` - selection for live cell, not a marker
(x|y) = x OR y
space = AND
[ ] and ( ) = grouping (contents AND- or OR-joined); a postfix after a closing
              bracket applies to the whole group, e.g. [A B]- = NOT(A AND B)
postfixes: -, + , lo, hi, int, `+/-` (=low to undetectable)
`/` = OR delimiter on postfix e.g. -/lo