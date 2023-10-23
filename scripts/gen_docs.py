import inspect
import textwrap
from pathlib import Path

from fliq import Query


docs_path = Path(__file__).parent.parent / 'docs' / 'reference'


def get_md_body(title, methods):
    template = """
    # {{title}}
    
    ::: fliq.query.Query
        options:
            filters: [
                {{filters}} 
            ]   
    """
    body = (template
            .replace('{{title}}', title)
            .replace('{{filters}}', ', '.join(methods)))
    return textwrap.dedent(body)


mappers = []
materializers = []
skipped_methods = [
    Query.__init__.__name__,
    Query._self.__name__,
    Query.__iter__.__name__,
    Query.__next__.__name__,
    Query.__repr__.__name__
]

for name, method in inspect.getmembers(Query, predicate=inspect.isfunction):
    if name in skipped_methods:
        # skip constructor
        continue
    ret_type = inspect.signature(method).return_annotation
    is_streamer = ret_type == Query.__name__
    if is_streamer:
        mappers.append(name)
    else:
        materializers.append(name)

with open(docs_path / 'mapper_methods.md', 'w') as f:
    f.write(get_md_body('Mapper Methods', mappers))

with open(docs_path / 'materializer_methods.md', 'w') as f:
    f.write(get_md_body('Materializer Methods', materializers))
