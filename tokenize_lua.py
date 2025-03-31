from pygments.lexers import guess_lexer_for_filename

# Open and read the content of the local file 'test.lua'
with open("test.lua", "r", encoding="utf-8") as file:
    content = file.read()
# content = content.replace("    ", "\t")
# Guess the lexer for the Lua file
lexer = guess_lexer_for_filename("test.lua", content)

# Get tokens from the lexer
tokens = lexer.get_tokens(content)

# Print the tokens
for token in tokens:
    print(token)
