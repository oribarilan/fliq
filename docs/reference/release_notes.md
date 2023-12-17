# Release Notes (What's New) 🤩

## v1.10.0

* ⬆️ **Zip Upgrade** - added longest and fillvalue to the [zip method](code_api/mapper_methods.md#fliq.query.Query.zip)
* 🧶 **Interleave** - new [interleave method](code_api/mapper_methods.md#fliq.query.Query.interleave), for 
interleaving two or more iterables together, in a round-robin fashion, regardless of their length

## v1.9.0

* 📝 **Release Notes** - starting to log release notes
* 🔍 **Type Support** - added full type support (including generics)

## v1.7.0 (and before)

* 📝 **Readme** - added readme
* 🧪 **Testing** - added unit tests with 100% coverage
* 📦 **Packaging** - added packaging
* 🧪 **Performance Tests** - added performance tests
* 📊 **Benchmarking** - added benchmarking
* 📝 **Documentation** - added basic documentation using MkDocs
* 📝 **API Reference** - added API reference for entire functionality
* 📝 **Examples** - added examples
* 🫣 **Peeking** - added peeking: a way to look at items in a query, without consuming it.
* ✂️ **Partitioning** - added partitioning: a time and space efficient way to split a query into n sub-queries, 
that a mutually exclusive and collectively exhaustive (MECE)
* 📸 **Snapshots** - added snapshots: a way to create a "checkpoint" for a Query, for efficient re-use.
