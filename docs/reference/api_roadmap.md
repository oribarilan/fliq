# API Roadmap

## Special Functionality

- [x] snap (aka cache, materialize)
- [x] partition

## Mapper Methods

- [x] where (aka filter)
- [x] select (aka map)
- [x] exclude (aka where_not, remove_all) 
- [x] distinct
- [x] group_by
- [x] order_by
- [x] reverse
- [x] slice
- [x] skip
- [ ] skip_last
- [x] take
- [x] zip
- [x] append
- [x] prepend
- [x] append_many
- [x] prepend_many
- [ ] for_each

## Materializers

- [x] contains
- [x] equals
- [x] to_list
- [x] to_dict
- [ ] conversion (to_set, to_tuple, to_string)

### Special Materializers

- [x] in / not in (aka membership)
- [x] == / != (aka equality)
- [ ] arithmetic (+, -, *, /, %)

### Reducers

- [x] first
- [x] first_or_default
- [x] get
- [x] count
- [x] any
- [x] all
- [x] aggregate

#### Numeric Reducers
- [x] sum
- [x] min
- [x] max
- [ ] average