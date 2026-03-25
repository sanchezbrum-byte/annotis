# Swift Tooling

## SwiftLint Configuration

```yaml
# .swiftlint.yml
opt_in_rules:
  - array_init
  - closure_end_indentation
  - closure_spacing
  - contains_over_first_not_nil
  - discouraged_optional_boolean
  - empty_string
  - explicit_init
  - fallthrough
  - fatal_error_message
  - first_where
  - force_unwrapping          # Treat force unwrap as error
  - implicit_return
  - joined_default_parameter
  - lower_acl_than_parent
  - missing_docs
  - modifier_order
  - number_separator
  - operator_usage_whitespace
  - overridden_super_call
  - prefer_self_type_over_type_of_self
  - prohibited_interface_builder
  - sorted_imports
  - vertical_parameter_alignment_on_call

line_length:
  warning: 100
  error: 120

function_body_length:
  warning: 40
  error: 60

file_length:
  warning: 500
  error: 1000

type_body_length:
  warning: 300
  error: 500

identifier_name:
  min_length:
    warning: 2
  excluded:
    - id
    - ok
    - to

excluded:
  - Pods
  - .build
  - DerivedData
```
