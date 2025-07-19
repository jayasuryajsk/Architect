#!/usr/bin/env python3
"""Test the clean_code method"""

from browser_use.architect.core.tool_generator import AdvancedToolGenerator

# Test the _clean_code method
generator = AdvancedToolGenerator()

# Test with markdown wrapped code
code_with_markdown = """```python
async def count_words(text: str):
    word_count = len(text.split())
    return {'result': word_count}
```"""

cleaned = generator._clean_code(code_with_markdown)

print("Original:")
print(repr(code_with_markdown))
print("\nCleaned:")
print(repr(cleaned))
print("\nActual cleaned code:")
print(cleaned)

# Try to parse it
import ast
try:
    ast.parse(cleaned)
    print("\n✅ Cleaned code is valid!")
except SyntaxError as e:
    print(f"\n❌ Syntax error: {e}")