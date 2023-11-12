import ast
import re
from pathlib import Path
from typing import List


class MarkdownPythonEvaluator:
    def __init__(self, markdown_file_path: Path):
        self.markdown_file_path = markdown_file_path
        self.code_block_pattern = re.compile(r'```python(.*?)```', re.DOTALL)

    def extract_python_code_blocks(self) -> List[str]:
        """Extract python code blocks from the markdown file and split them into statements."""
        code_blocks = []
        with open(self.markdown_file_path, 'r', encoding='utf-8') as md_file:
            content = md_file.read()

            # Pattern to match python code blocks
            pattern = re.compile(r'```python(.*?)```', re.DOTALL)

            # Iterate over all matches
            for match in pattern.finditer(content):
                code_block = match.group(1).strip()  # Extract the code block
                code_blocks.append(code_block)

        return code_blocks

    def eval(self, code: str):
        """
        Safely evaluate a single python code block.
        This method does not allow modification of the environment or execution of arbitrary code.
        """
        try:
            # Safely evaluate expressions, preventing code execution
            block = ast.parse(code, mode='exec')
            exec(compile(block, '<string>', mode='exec'))
        except Exception as e:
            # In real use, you might want to handle the exception differently
            print(f"Error evaluating code block at {self.markdown_file_path}: "
                  f"{e} at block:\n{code}")
            exit(1)

    def evaluate_blocks(self):
        """Evaluate all extracted Python code blocks."""
        code_blocks = self.extract_python_code_blocks()
        for block in code_blocks:
            self.eval(block)


# Usage
root_path = Path(__file__).parent.parent
readme_path = root_path / 'README.md'
docs_path = root_path / 'docs'
files = [readme_path] + list(docs_path.glob('**/*.md'))
for f in files:
    print(f"Executing code blocks in {f}")
    evaluator = MarkdownPythonEvaluator(f)
    evaluator.evaluate_blocks()
