# GraphQL examples for testing
## Exact segment type with specific data
```GraphQL
query DarkFiber {
  segment_list(
    filters: {
      segment_type: { exact: "dark_fiber" },
      has_type_specific_data: true
    }
  ) {
    id
    name
    type_specific_data
    has_path_data
    has_type_specific_data
  }
}
```
