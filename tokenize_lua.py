# from pygments.lexers import guess_lexer_for_filename
from scripting import LuaLexer
import re

tokens = []
# Open and read the content of the local file 'test.lua'
with open("test.lua", "r", encoding="utf-8") as file:
    content = file.read()
# content = content.replace("    ", "\t")
# lexer = guess_lexer_for_filename("test.lua", content)
lexer = LuaLexer()

# Get tokens from the lexer
# tokens = lexer.get_tokens(content)

# Print the tokens
# for token in tokens:
#     print(token)


pattern = re.compile(rf"[A-Za-z_]\w*(?={'_s'}*[.:])")
pos = 261
rexmatch = pattern.match
print("text remaining: ", content[pos:])
print("trying to match")
m = rexmatch(content, pos)
print("matched")
