import inspect
import textwrap
from pathlib import Path

from fliq import Query


docs_path = Path(__file__).parent.parent / 'docs'


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


def create_api_docs():
    docs_reference_path = docs_path / 'reference' / 'code_api'
    mappers = []
    materializers = []
    skipped_methods = [
        Query.__init__.__name__,
        Query._self.__name__,
        Query.__iter__.__name__,
        Query.__next__.__name__,
        Query.__repr__.__name__,
        Query.snap.__name__,
    ]

    for name, method in inspect.getmembers(Query, predicate=inspect.isfunction):
        if name in skipped_methods:
            # skip constructor
            continue
        ret_type = inspect.signature(method).return_annotation
        is_streamer = ret_type.startswith('Query')
        exact_name_regex = f'"^{name}$"'
        if is_streamer:
            mappers.append(exact_name_regex)
        else:
            materializers.append(exact_name_regex)

    with open(docs_reference_path / 'mapper_methods.md', 'w') as f:
        f.write(get_md_body('Mapper Methods', mappers))

    with open(docs_reference_path / 'materializer_methods.md', 'w') as f:
        f.write(get_md_body('Materializer Methods', materializers))


def create_index_doc():
    # this function copies README.md to docs/index.md
    index_doc_path = docs_path / 'index.md'
    readme_path = Path(__file__).parent.parent / 'README.md'

    with open(index_doc_path, 'w') as f:
        with open(readme_path, 'r') as readme:
            # update relative path for asserts
            content = readme.read().replace(
                "docs/assets/",
                "assets/"
            )
            f.write(content)


create_api_docs()
create_index_doc()