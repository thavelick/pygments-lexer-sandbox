import re

tokens = []
with open("test.lua", "r", encoding="utf-8") as file:
    content = file.read()
# content = content.replace("    ", "\t")


_comment_multiline = r"(?:--\[(?P<level>=*)\[[\w\W]*?\](?P=level)\])"
_comment_single = r"(?:--.*$)"
_space = r"(?:\s+)"
_s = rf"(?:{_comment_multiline}|{_comment_single}|{_space})"
_name = r"(?:[^\W\d]\w*)"

func_rexmatch = re.compile(rf"[A-Za-z_]\w*(?={_s}*\()", re.MULTILINE).match
var_rexmatch = re.compile(rf"[A-Za-z_]\w*(?={_s}*[.:])", re.MULTILINE).match

pos = 0

while pos < len(content):
    # once we get to pos = 261, match checking takes a long time
    print("pos", pos)
    print("Function match", func_rexmatch(content, pos))
    print("Variable match", func_rexmatch(content, pos))
    pos += 1
