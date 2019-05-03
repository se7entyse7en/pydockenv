# HISTORY

## Unreleased

### Added

- Added support to python 3.6.
- [internal] Added testing with python 3.6


## v0.2.2 - 2019-05-03

### Fixed

- Fixed bug in `pydockenv` binary that makes it exit from parent when sourced introduced in `v0.2.1`.

## v0.2.1 - 2019-04-29 [YANKED]

### Added

- Exits with status code `1` when called with unsupported shells
- Added printing of environment variables when running `pydockenv` if `PYDOCKENV_DEBUG` is set
- [documentation] Added `Development` section in `README.md`
- [internal] Added some integration tests
- [internal] Added CI on travis

### Fixed

- Fixed exit code of `pydockenv`
- [documentation] Fixed images url in `README.md` by using absolute urls

## v0.2.0 - 2019-04-01

### Added

- Marked with `*` the active environment when listing
- Change `PS1` when activating and deactivating environment
- Added an ad-hoc network for each environment
- [internal] Added `publish-test` Makefile target
- [internal] Added publishing of git tag when publishing

### Changed

- [documentation] Updated `README.md` by adding some documentation and examples
- [internal] Changed bumpversion to include the release date in `HISTORY.md`

### Fixed

- [internal] Fixed `.bumpversion.cfg` by making each version a subsection
- [internal] Fixed description field in `setup.py`
- [internal] Added missing `twine` dev dependency


## v0.1.0 - 2019-04-01

- First version!
