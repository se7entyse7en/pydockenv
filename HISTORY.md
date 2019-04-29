# HISTORY

## Unreleased

### Added

- Added `Development` section in `README.md`
- Added printing of environment variables when running `pydockenv` if `PYDOCKENV_DEBUG` is set
- Added some integration tests

### Fixed

- Fixed images url in `README.md` by using absolute urls
- Fixed exit code of `pydockenv`

## v0.2.0 - 2019-04-01

### Added

- Added publishing of git tag when publishing
- Marked with '*' the active environment when listing
- Change `PS1` when activating and deactivating environment
- Added an ad-hoc network for each environment
- Added `publish-test` Makefile target

### Changed

- Updated `README.md` by adding some documentation and examples
- Changed bumpversion to include the release date in `HISTORY.md`

### Fixed

- Fixed `.bumpversion.cfg` by making each version a subsection
- Fixed description field in `setup.py`
- Added missing `twine` dev dependency


## v0.1.0 - 2019-04-01

- First version!
