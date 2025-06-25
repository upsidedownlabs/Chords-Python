# Change Log


## [1.5.1] - 2022-12-12

* Prevents the extension from being activated for non-Python languages.

* Fixes type hints being provided for some function definitions ending with typing module hints, i.e. '-> Dict[str, str]:'.

## [1.4.1] - 2020-10-18

* Added a known issue to the readme.

## [1.4.0] - 2020-10-18

* Added type hints for bytes
* Changed the default workspace search limit to 10

## [1.3.0] - 2020-08-22

* Type hints for the typing module are now provided at the bottom of the list by default
* Fixed the first type hint not always being pre-selected
* Fixed incorrectly sorted type hints in some cases

## [1.2.0] - 2020-05-05

### Added:

* Return type hints for the typing module
* Support for non-ASCII class names

### Fixed:

* Default parameter values sometimes being provided within type hint items

## [1.1.2] - 2020-04-22

* Fixed type hints not being provided for async functions.

## [1.1.0] - 2020-04-19

### Improved:

* New setting for disabling workspace searching.
* More default hints are provided for the typing module.
* Overall speed.

### Fixed:

* Setting the workspace search limit to 0 not working.

## [1.0.2] - 2020-04-16

* Fixed type hints being provided for non-parameters.

## [1.0.1] - 2020-04-13

* Fixed type hints sometimes being provided when typing ':' within a string.

## [1.0.0] - 2020-04-09

* Initial release