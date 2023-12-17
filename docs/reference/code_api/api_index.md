# API Index

### Special Functionality

- [x] [snap](snapshots.md) (aka cache, materialize)
- [x] [partition](partitioning.md)
- [x] [peek](peeking.md)

### Mapper Methods

- [x] [where](mapper_methods.md#fliq.query.Query.where) (aka filter)
- [x] [select](mapper_methods.md#fliq.query.Query.select) (aka map)
- [x] [exclude](mapper_methods.md#fliq.query.Query.exclude) (aka where_not, remove_all) 
- [x] [distinct](mapper_methods.md#fliq.query.Query.distinct)
- [x] [group_by](mapper_methods.md#fliq.query.Query.group_by)
- [x] [order_by](mapper_methods.md#fliq.query.Query.order_by)
- [x] [reverse](mapper_methods.md#fliq.query.Query.reverse)
- [x] [slice](mapper_methods.md#fliq.query.Query.slice)
- [x] [skip](mapper_methods.md#fliq.query.Query.skip)
- [ ] skip_last
- [x] [take](mapper_methods.md#fliq.query.Query.take)
- [x] [top](mapper_methods.md#fliq.query.Query.top)
- [x] [bottom](mapper_methods.md#fliq.query.Query.bottom)
- [x] [zip](mapper_methods.md#fliq.query.Query.zip)
- [x] [interleave](mapper_methods.md#fliq.query.Query.interleave)
- [x] [append](mapper_methods.md#fliq.query.Query.append)
- [x] [prepend](mapper_methods.md#fliq.query.Query.prepend)
- [x] [append_many](mapper_methods.md#fliq.query.Query.append_many)
- [x] [prepend_many](mapper_methods.md#fliq.query.Query.prepend_many)
- [ ] for_each
- [x] [shuffle](mapper_methods.md#fliq.query.Query.shuffle)
- [x] [flatten](mapper_methods.md#fliq.query.Query.flatten)

### Materializers

- [x] [contains](materializer_methods.md#fliq.query.Query.contains)
- [x] [equals](materializer_methods.md#fliq.query.Query.equals)
- [x] [to_list](materializer_methods.md#fliq.query.Query.to_list)
- [x] [to_dict](materializer_methods.md#fliq.query.Query.to_dict)
- [ ] conversion (to_set, to_tuple, to_string)

#### Special Materializers

- [x] [in / not in](materializer_methods.md#fliq.query.Query.contains) (aka membership)
- [x] [== / !=](materializer_methods.md#fliq.query.Query.__eq__) (aka equality)
- [ ] arithmetic (+, -, *, , %)

#### Reducers

- [x] [first](materializer_methods.md#fliq.query.Query.first)
- [x] [first_or_default](materializer_methods.md#fliq.query.Query.first_or_default)
- [ ] last
- [ ] last_or_default
- [x] [single](materializer_methods.md#fliq.query.Query.single)
- [x] [single_or_default](materializer_methods.md#fliq.query.Query.single_or_default)
- [x] [sample](materializer_methods.md#fliq.query.Query.sample)
- [x] [count](materializer_methods.md#fliq.query.Query.count)
- [x] [any](materializer_methods.md#fliq.query.Query.any)
- [x] [all](materializer_methods.md#fliq.query.Query.all)
- [x] [aggregate](materializer_methods.md#fliq.query.Query.aggregate)

##### Numeric Reducers
- [x] [sum](materializer_methods.md#fliq.query.Query.sum)
- [x] [min](materializer_methods.md#fliq.query.Query.min)
- [x] [max](materializer_methods.md#fliq.query.Query.max)
- [ ] average