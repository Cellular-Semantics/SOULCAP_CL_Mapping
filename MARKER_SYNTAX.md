# SOULCAP Marker Expression Syntax

This document specifies the mini-language used to define SOULCAP cell types by
their cell-surface (flow-cytometry) marker phenotype. It applies to the four
marker columns of the **`Marker Combinations`** sheet:

- `Required exclusion`
- `Ideal exclusion`
- `Required phenotypic markers`
- `Ideal phenotypic markers`

It has two parts: a [human-readable guide](#1-human-readable-guide) and a
[formal grammar](#2-formal-grammar-ebnf). They describe the same language.

---

## 1. Human-readable guide

A cell is described by a **space-separated list of conditions**, all of which
must hold. In other words, **a space means AND**.

```
live/ CD45+ CD56+ CD127- CD16+
```

> live cells, AND CD45 positive, AND CD56 positive, AND CD127 negative, AND CD16 positive.

### 1.1 Markers and qualifiers

A condition is a **marker name** followed by a **qualifier** that says how the
marker is expressed:

| Qualifier | Meaning                                   |
|-----------|-------------------------------------------|
| `+`       | positive                                  |
| `-`       | negative                                  |
| `hi`      | high expression                           |
| `lo`      | low expression                            |
| `int`     | intermediate expression                   |
| `+/-`     | variable — low to undetectable            |

Examples: `CD3-`, `CD56hi`, `CD127lo`, `HLA-DR+`.

### 1.2 The `/` operator (alternative qualifiers)

A `/` between qualifiers means **OR on the qualifier** — any of the listed
levels is acceptable:

| Expression | Meaning                          |
|------------|----------------------------------|
| `CD16-/lo` | CD16 is negative **or** low      |
| `CD56+/hi` | CD56 is positive **or** high     |
| `CD127lo/-`| CD127 is low **or** negative     |

(`+/-` is the special "low to undetectable" case of this.)

### 1.3 The `live/` gate

`live/` at the start is **not a marker** — it is a live-cell selection gate
(exclude dead cells). Treat it as a fixed prefix.

### 1.4 The `|` operator (OR between conditions)

`|` means **OR** between whole conditions. It is almost always wrapped in a
group so the scope is explicit:

```
(CD14-|CD33-|CD64-)
```

> CD14 negative OR CD33 negative OR CD64 negative.

### 1.5 Grouping with `[ ]` and `( )`

Both `[ ]` and `( )` are **grouping brackets** — they bundle several conditions
into a single unit. The contents are joined by **space (AND)** or **`|` (OR)**,
and groups may be **nested**:

```
[(TCRVa7.2+|MR1 Tetramer+) CD161+]
```

> ( TCR Vα7.2 positive OR MR1-tetramer positive ) AND CD161 positive.

`[ ]` and `( )` are interchangeable as grouping symbols; by convention `( )`
tends to wrap a simple OR-set and `[ ]` a larger compound, but the parser treats
them identically.

### 1.6 Group-level postfix (the important rule)

**A qualifier placed *after* a closing bracket applies to the whole group.**
This is how negation of a compound condition is written:

| Expression              | Meaning                                          |
|-------------------------|--------------------------------------------------|
| `[HLA-DR+ CD11chi]-`    | NOT ( HLA-DR positive AND CD11c high )           |
| `[CD15hi\|CD66b+]-`     | NOT ( CD15 high OR CD66b positive )              |
| `(...)+`                | the whole OR-group is positive                   |

So a trailing `-` or `+` is **not** part of any single marker — it negates or
affirms everything inside the brackets it follows.

### 1.7 Worked example

```
live/ CD45+ CD56+/hi CD127- (CD14-|CD33-|CD64-) [HLA-DR+ CD11chi]-
```

Reads as: live cells, AND CD45⁺, AND (CD56 positive or high), AND CD127⁻,
AND (CD14⁻ or CD33⁻ or CD64⁻), AND NOT(HLA-DR⁺ and CD11c-high).

---

## 2. Formal grammar (EBNF)

ISO/IEC 14977 EBNF. Whitespace is significant (it is the AND operator), so it is
written explicitly as `WS` rather than skipped.

```ebnf
(* ─── top level ─────────────────────────────────────────────── *)
expression   = [ gate ] , and_list ;

gate         = "live/" , [ WS ] ;          (* live-cell selection, not a marker *)

(* ─── boolean structure ────────────────────────────────────── *)
and_list     = term , { WS , term } ;      (* space = AND *)
or_list      = term , { "|" , term } ;     (* pipe  = OR  *)

term         = ( atom | group ) , [ qualifier ] ;
                                           (* a qualifier after a group applies
                                              to the whole group, e.g. [..]- *)

group        = "[" , inner , "]"
             | "(" , inner , ")" ;
inner        = or_list | and_list ;        (* groups may nest via term -> group *)

(* ─── leaves ───────────────────────────────────────────────── *)
atom         = marker ;
marker       = name_start , { name_char } ;

qualifier    = level , { "/" , level } ;   (* /-joined alternatives: -/lo, +/hi, +/- *)
level        = "+" | "-" | "lo" | "hi" | "int" ;

(* ─── lexical ──────────────────────────────────────────────── *)
name_start   = letter ;
name_char    = letter | digit | "-" | "." ;  (* hyphen/dot allowed *inside* names:
                                                HLA-DR, IL-4, TCRVa7.2, CD1d-a-GalCer *)
letter       = "A" | ... | "Z" | "a" | ... | "z" ;
digit        = "0" | ... | "9" ;
WS           = " " , { " " } ;
```

### 2.1 Lexical disambiguation: hyphen in names vs. negation

The grammar above is ambiguous to a naive tokenizer because `-` appears both
inside marker names (`HLA-DR`) and as the `negative` qualifier (`CD3-`). Resolve
it with this lexer rule:

> A `-` (or `+`) is a **qualifier** only when it is immediately followed by a
> qualifier-terminator: whitespace, `|`, `)`, `]`, `/`, or end-of-string.
> Otherwise it is part of the marker name.

Equivalently: longest-match the marker name first; a trailing `-`/`+` is only
peeled off as a qualifier at a token boundary. This correctly parses
`HLA-DR+` (name `HLA-DR`, qualifier `+`) and `TCRVa24-Ja18+` (name
`TCRVa24-Ja18`, qualifier `+`).

### 2.2 Semantics summary

| Construct      | Operator / meaning                                    |
|----------------|-------------------------------------------------------|
| `A B`          | A AND B                                               |
| `A\|B`         | A OR B                                                 |
| `[ … ]`, `( … )` | grouping (identical); contents AND- or OR-joined    |
| `marker+`      | marker positive (`-` neg, `hi`/`lo`/`int` levels)     |
| `x/y`          | qualifier alternative: level x OR level y             |
| `group-`       | negation of the whole group                           |
| `group+`       | affirmation of the whole group                        |
| `live/`        | live-cell gate (fixed prefix, not a marker)           |

---

## 3. Caveats & known data issues

The grammar describes the *intended* language. The current `Marker Combinations`
sheet contains entries that violate it and should be corrected at source (the
[Google Sheet master](https://docs.google.com/spreadsheets/d/1uWwczLxgbpWMmXycL8Thq5NVExzlib4A/edit)):

- **Unbalanced brackets** —
  `live/ CD45+ CD33+|CD123+) (CD193+|...)` (missing opening `(`) and
  `CD64+/-|CD33+/-)` (stray trailing `)`, appears twice).
- **Free-text leak** — the `ILC` row's *Ideal phenotypic markers* cell contains
  the note `Confirm that ILC don't bind to CD14/CD19/CD56/CD11c/CD123` rather
  than an expression.
- **Inconsistent marker casing** — `TCRVa24` and `TCRva24` are both used for the
  same marker, sometimes within one expression. Pick one canonical spelling.
- **Inconsistent group negation** — `[CD15hi|CD66b+]` appears both with and
  without a trailing `-`; confirm which cell types intend the negation.

A parser built from §2 can be used to lint the sheet for these.
