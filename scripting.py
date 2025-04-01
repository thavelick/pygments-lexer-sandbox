import re

from lexer import RegexLexer, include, bygroups, default, combined, words
from pygments.token import (
    Text,
    Comment,
    Operator,
    Keyword,
    Name,
    String,
    Number,
    Punctuation,
    Error,
    Whitespace,
    Other,
)
from pygments.util import get_bool_opt, get_list_opt

__all__ = [
    "LuaLexer",
]


def all_lua_builtins():
    from pygments.lexers._lua_builtins import MODULES

    return [w for values in MODULES.values() for w in values]


class LuaLexer(RegexLexer):
    """
    For Lua source code.

    Additional options accepted:

    `func_name_highlighting`
        If given and ``True``, highlight builtin function names
        (default: ``True``).
    `disabled_modules`
        If given, must be a list of module names whose function names
        should not be highlighted. By default all modules are highlighted.

        To get a list of allowed modules have a look into the
        `_lua_builtins` module:

        .. sourcecode:: pycon

            >>> from pygments.lexers._lua_builtins import MODULES
            >>> MODULES.keys()
            ['string', 'coroutine', 'modules', 'io', 'basic', ...]
    """

    name = "Lua"
    url = "https://www.lua.org/"
    aliases = ["lua"]
    filenames = ["*.lua", "*.wlua"]
    mimetypes = ["text/x-lua", "application/x-lua"]
    version_added = ""

    _comment_multiline = r"(?:--\[(?P<level>=*)\[[\w\W]*?\](?P=level)\])"
    _comment_single = r"(?:--.*$)"
    _space = r"(?:\s+)"
    _s = rf"(?:{_comment_multiline}|{_comment_single}|{_space})"
    _name = r"(?:[^\W\d]\w*)"

    tokens = {
        "root": [
            # Lua allows a file to start with a shebang.
            (r"#!.*", Comment.Preproc),
            default("base"),
        ],
        "ws": [
            (_comment_multiline, Comment.Multiline),
            (_comment_single, Comment.Single),
            (_space, Whitespace),
        ],
        "base": [
            include("ws"),
            (r"(?i)0x[\da-f]*(\.[\da-f]*)?(p[+-]?\d+)?", Number.Hex),
            (r"(?i)(\d*\.\d+|\d+\.\d*)(e[+-]?\d+)?", Number.Float),
            (r"(?i)\d+e[+-]?\d+", Number.Float),
            (r"\d+", Number.Integer),
            # multiline strings
            (r"(?s)\[(=*)\[.*?\]\1\]", String),
            (r"::", Punctuation, "label"),
            (r"\.{3}", Punctuation),
            (r"[=<>|~&+\-*/%#^]+|\.\.", Operator),
            (r"[\[\]{}().,:;]+", Punctuation),
            (r"(and|or|not)\b", Operator.Word),
            (
                words(
                    [
                        "break",
                        "do",
                        "else",
                        "elseif",
                        "end",
                        "for",
                        "if",
                        "in",
                        "repeat",
                        "return",
                        "then",
                        "until",
                        "while",
                    ],
                    suffix=r"\b",
                ),
                Keyword.Reserved,
            ),
            (r"goto\b", Keyword.Reserved, "goto"),
            (r"(local)\b", Keyword.Declaration),
            (r"(true|false|nil)\b", Keyword.Constant),
            (r"(function)\b", Keyword.Reserved, "funcname"),
            (words(all_lua_builtins(), suffix=r"\b"), Name.Builtin),
            (rf"[A-Za-z_]\w*(?={_s}*[.:])", Name.Variable, "varname"),
            (rf"[A-Za-z_]\w*(?={_s}*\()", Name.Function),
            (r"[A-Za-z_]\w*", Name.Variable),
            ("'", String.Single, combined("stringescape", "sqs")),
            ('"', String.Double, combined("stringescape", "dqs")),
        ],
        "varname": [
            include("ws"),
            (r"\.\.", Operator, "#pop"),
            (r"[.:]", Punctuation),
            (rf"{_name}(?={_s}*[.:])", Name.Property),
            (rf"{_name}(?={_s}*\()", Name.Function, "#pop"),
            (_name, Name.Property, "#pop"),
        ],
        "funcname": [
            include("ws"),
            (r"[.:]", Punctuation),
            (rf"{_name}(?={_s}*[.:])", Name.Class),
            (_name, Name.Function, "#pop"),
            # inline function
            (r"\(", Punctuation, "#pop"),
        ],
        "goto": [
            include("ws"),
            (_name, Name.Label, "#pop"),
        ],
        "label": [
            include("ws"),
            (r"::", Punctuation, "#pop"),
            (_name, Name.Label),
        ],
        "stringescape": [
            (
                r'\\([abfnrtv\\"\']|[\r\n]{1,2}|z\s*|x[0-9a-fA-F]{2}|\d{1,3}|'
                r"u\{[0-9a-fA-F]+\})",
                String.Escape,
            ),
        ],
        "sqs": [
            (r"'", String.Single, "#pop"),
            (r"[^\\']+", String.Single),
        ],
        "dqs": [
            (r'"', String.Double, "#pop"),
            (r'[^\\"]+', String.Double),
        ],
    }

    def __init__(self, **options):
        self.func_name_highlighting = get_bool_opt(
            options, "func_name_highlighting", True
        )
        self.disabled_modules = get_list_opt(options, "disabled_modules", [])

        self._functions = set()
        if self.func_name_highlighting:
            from pygments.lexers._lua_builtins import MODULES

            for mod, func in MODULES.items():
                if mod not in self.disabled_modules:
                    self._functions.update(func)
        RegexLexer.__init__(self, **options)

    def get_tokens_unprocessed(self, text):
        for index, token, value in RegexLexer.get_tokens_unprocessed(self, text):
            if token is Name.Builtin and value not in self._functions:
                if "." in value:
                    a, b = value.split(".")
                    yield index, Name, a
                    yield index + len(a), Punctuation, "."
                    yield index + len(a) + 1, Name, b
                else:
                    yield index, Name, value
                continue
            yield index, token, value


def _luau_make_expression(should_pop, _s):
    temp_list = [
        (r"0[xX][\da-fA-F_]*", Number.Hex, "#pop"),
        (r"0[bB][\d_]*", Number.Bin, "#pop"),
        (r"\.?\d[\d_]*(?:\.[\d_]*)?(?:[eE][+-]?[\d_]+)?", Number.Float, "#pop"),
        (words(("true", "false", "nil"), suffix=r"\b"), Keyword.Constant, "#pop"),
        (r"\[(=*)\[[.\n]*?\]\1\]", String, "#pop"),
        (
            r'(\.)([a-zA-Z_]\w*)(?=%s*[({"\'])',
            bygroups(Punctuation, Name.Function),
            "#pop",
        ),
        (r"(\.)([a-zA-Z_]\w*)", bygroups(Punctuation, Name.Variable), "#pop"),
        (rf'[a-zA-Z_]\w*(?:\.[a-zA-Z_]\w*)*(?={_s}*[({{"\'])', Name.Other, "#pop"),
        (r"[a-zA-Z_]\w*(?:\.[a-zA-Z_]\w*)*", Name, "#pop"),
    ]
    if should_pop:
        return temp_list
    return [entry[:2] for entry in temp_list]


def _luau_make_expression_special(should_pop):
    temp_list = [
        (r"\{", Punctuation, ("#pop", "closing_brace_base", "expression")),
        (r"\(", Punctuation, ("#pop", "closing_parenthesis_base", "expression")),
        (r"::?", Punctuation, ("#pop", "type_end", "type_start")),
        (r"'", String.Single, ("#pop", "string_single")),
        (r'"', String.Double, ("#pop", "string_double")),
        (r"`", String.Backtick, ("#pop", "string_interpolated")),
    ]
    if should_pop:
        return temp_list
    return [(entry[0], entry[1], entry[2][1:]) for entry in temp_list]
