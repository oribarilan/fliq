from copy import copy
from pathlib import Path

from pydoc_markdown.interfaces import Context
from pydoc_markdown.contrib.loaders.python import PythonLoader
from pydoc_markdown.contrib.renderers.markdown import MarkdownRenderer

context = Context(directory='.')
# loader = PythonLoader(search_path=['../fliq'])  # for debugging
loader = PythonLoader(search_path=['fliq'])
renderer = MarkdownRenderer(render_module_header=False,
                            descriptive_class_title=False,
                            classdef_code_block=False,
                            # signature_with_def=False, # Lib bug here, can't disable
                            render_toc=True,
                            render_toc_title=False,
                            header_level_by_type={
                                "Module": 3,
                                "Class": 3,
                                "Method": 3,
                                "Function": 3,
                                "Variable": 3
                            }
                            )

loader.init(context)
renderer.init(context)

modules = loader.load()
query_module = [m for m in modules if m.name == 'query'][0]
query_class = [c for c in query_module.members if c.name == 'Query'][0]

query_carrier = copy(query_class)
query_carrier.name = 'Carriers'
query_carrier.members = [m for m in query_class.members
                         if not m.name.startswith('_') and m.return_type == "'Query'"]

query_collector = copy(query_class)
query_collector.name = 'Collectors'
query_collector.members = [m for m in query_class.members
                           if not m.name.startswith('_') and m.return_type != "'Query'"]

current_dir = Path(__file__).parent
root_dir = current_dir.parent
api_md_path = root_dir / "api.md"
readme_base_md_path = root_dir / "readme_base.md"
readme_md_path = root_dir / "README.md"

api_content = renderer.render_to_string([query_carrier, query_collector])
with open(api_md_path, 'w') as f:
    f.writelines(api_content)


# merge api.md and readme_base.md to README.md, by replace {{autoapi}} in readme_base.md with api_content
def replace_autoapi_in_readme(content: str) -> str:
    with open(readme_base_md_path, 'r') as readme_base:
        readme_template = readme_base.read()
        readme_content = readme_template.replace('{{auto_api}}', content)

    with open(readme_md_path, 'w') as readme:
        readme.writelines(readme_content)


replace_autoapi_in_readme(api_content)
