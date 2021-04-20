# Changelog

## [0.6.1] - 2021-04-20
### Changed
- Correction to the previous changelog entry.

## [0.6.0] - 2021-04-20
### Changed
- Converted the middleware to a class.

### Upgrading
In your `MIDDLEWARE` in `settings.py`,
change `blacklist.middleware.blacklist_middleware` to `blacklist.middleware.BlacklistMiddleware`.

## [0.5.1] - 2021-03-05
### Changed
- Added a blank line for consistency. No other changes in this release.

## [0.5.0] - 2021-03-02
### Added
- Added logging toggle setting. Thanks to [@sweldon](https://github.com/sweldon).
### Fixed
- Allow custom user models. Thanks to [@richardARPANET](https://github.com/richardARPANET).

## [0.4.1] - 2020-05-10
### Changed
- Limited the length of comments in rules.
- Bulk deletion of rules from the database.

## [0.4.0] - 2020-05-10
### Added
- Reload rules periodically.
### Changed
- Major scalability improvements.

## [0.3.0] - 2019-12-14
### Added
- Setting to enable the automatic blacklisting of rate-limited clients (on by default).

## [0.2.2] - 2019-12-01
### Fixed
- Don't try to blacklist ratelimited clients if `BLACKLIST_ENABLE` is off.

## [0.2.1] - 2019-12-01
### Fixed
- Corrected the package version.
- Corrected the release date of version 0.2.0 in the changelog.

## [0.2.0] - 2019-12-01
### Added
- Render a custom error template, if configured.
- Setting to enable the blocking of blacklisted clients (on by default).

## [0.1.2] - 2019-06-22
### Fixed
- Install the `trim_blacklist` command with the package.
- Corrected the link to version 0.1.1 in the changelog.

## [0.1.1] - 2019-06-13
### Added
- Included the version of the package in the code.

### Fixed
- Corrected the link to version 0.1.0 in the changelog.

## [0.1.0] - 2019-06-13
### Added
- Initial version.

[0.6.1]: https://github.com/vsemionov/django-blacklist/compare/0.6.0...0.6.1
[0.6.0]: https://github.com/vsemionov/django-blacklist/compare/0.5.1...0.6.0
[0.5.1]: https://github.com/vsemionov/django-blacklist/compare/0.5.0...0.5.1
[0.5.0]: https://github.com/vsemionov/django-blacklist/compare/0.4.1...0.5.0
[0.4.1]: https://github.com/vsemionov/django-blacklist/compare/0.4.0...0.4.1
[0.4.0]: https://github.com/vsemionov/django-blacklist/compare/0.3.0...0.4.0
[0.3.0]: https://github.com/vsemionov/django-blacklist/compare/0.2.2...0.3.0
[0.2.2]: https://github.com/vsemionov/django-blacklist/compare/0.2.1...0.2.2
[0.2.1]: https://github.com/vsemionov/django-blacklist/compare/0.2.0...0.2.1
[0.2.0]: https://github.com/vsemionov/django-blacklist/compare/0.1.2...0.2.0
[0.1.2]: https://github.com/vsemionov/django-blacklist/compare/0.1.1...0.1.2
[0.1.1]: https://github.com/vsemionov/django-blacklist/compare/0.1.0...0.1.1
[0.1.0]: https://github.com/vsemionov/django-blacklist/releases/tag/0.1.0
