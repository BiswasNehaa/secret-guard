# Changelog

## [0.11.0](https://github.com/BiswasNehaa/secret-guard/compare/v0.10.0...v0.11.0) (2026-09-15)


### Features

* add --max-findings to cap scan output ([#77](https://github.com/BiswasNehaa/secret-guard/issues/77)) ([757e842](https://github.com/BiswasNehaa/secret-guard/commit/757e84216bd2aff265efc1dc56da779964eba16c))
* add detection rules for npm, SendGrid, Twilio, Heroku, DigitalOcean, and HubSpot ([#27](https://github.com/BiswasNehaa/secret-guard/issues/27)) ([07433b9](https://github.com/BiswasNehaa/secret-guard/commit/07433b9499ed41ffc925ad21b0b338e809b7115a))
* add one-line GitHub Action ([#39](https://github.com/BiswasNehaa/secret-guard/issues/39)) ([d3bb8a1](https://github.com/BiswasNehaa/secret-guard/commit/d3bb8a11202afffcb3645534f1360ac6be1b3cc4))
* add per-rule scan controls, release automation, and coverage reporting ([#31](https://github.com/BiswasNehaa/secret-guard/issues/31)) ([6a960b5](https://github.com/BiswasNehaa/secret-guard/commit/6a960b569818aab39e42ae58d0a7975904927bdb))
* **cli:** add --csv output format for scan results ([77c461e](https://github.com/BiswasNehaa/secret-guard/commit/77c461ea8b0a10e994ea9495927c9c1cb020ab50))
* **cli:** add --quiet flag to suppress scan output ([f02637b](https://github.com/BiswasNehaa/secret-guard/commit/f02637b5e522d6808d40300c4f913571a86388a1))
* **cli:** add --reveal-prefix and --reveal-suffix for partial masking ([#91](https://github.com/BiswasNehaa/secret-guard/issues/91)) ([64a22a9](https://github.com/BiswasNehaa/secret-guard/commit/64a22a9b5e91853f2a1f42761fdc71f01336ec00))
* **cli:** add --severity flag to fail scans only past a severity threshold ([0a6d569](https://github.com/BiswasNehaa/secret-guard/commit/0a6d56919526cfa647b8d3de1cde1e6ca835c26a))
* **cli:** add --severity flag to fail scans only past a severity threshold ([#67](https://github.com/BiswasNehaa/secret-guard/issues/67)) ([0a6d569](https://github.com/BiswasNehaa/secret-guard/commit/0a6d56919526cfa647b8d3de1cde1e6ca835c26a))
* **cli:** add --severity threshold support to scan command ([db4fb8a](https://github.com/BiswasNehaa/secret-guard/commit/db4fb8a8a3e33391490eb0205b85a579cab99ff3))
* **cli:** add --stdin and --filename to scan piped input ([#65](https://github.com/BiswasNehaa/secret-guard/issues/65)) ([08c34aa](https://github.com/BiswasNehaa/secret-guard/commit/08c34aa9711f8262a84ea52c7d6e36b6f13a3019))
* **cli:** add --summary output to print only the severity summary ([37fa6bf](https://github.com/BiswasNehaa/secret-guard/commit/37fa6bf3deb1f0c76cdc8ee9c969ce0bc2c2a9dd))
* **cli:** add baseline/allowlist support to suppress known intentional findings ([#36](https://github.com/BiswasNehaa/secret-guard/issues/36)) ([9c660a2](https://github.com/BiswasNehaa/secret-guard/commit/9c660a2f845d5fd8c952ab16a83da074e47842b5))
* **cli:** allow scanning multiple paths with secret-guard scan ([a10c9f7](https://github.com/BiswasNehaa/secret-guard/commit/a10c9f7d26293ab0061af0e61937f68ed8d66814))
* custom rule manifests (closes [#9](https://github.com/BiswasNehaa/secret-guard/issues/9)) ([#70](https://github.com/BiswasNehaa/secret-guard/issues/70)) ([9290242](https://github.com/BiswasNehaa/secret-guard/commit/9290242b58e435fe9f7405aff83c3fe9158229ef))
* **report:** add XML and HTML report output formats ([7604d04](https://github.com/BiswasNehaa/secret-guard/commit/7604d045762890cacb48d714e89a2f155085d079))
* **rules:** add GitLab PAT, Hugging Face token, and Slack webhook detection ([#72](https://github.com/BiswasNehaa/secret-guard/issues/72)) ([20a7f65](https://github.com/BiswasNehaa/secret-guard/commit/20a7f659ede74b844dba0b84855ea3d9e6152797))
* **rules:** add OpenAI, Anthropic, and Discord bot token detection ([9b04cd4](https://github.com/BiswasNehaa/secret-guard/commit/9b04cd478bd90a36dfd71f914bbb8240198059c1))
* **rules:** add OpenAI, Anthropic, and Discord bot token detection ([0f01ed5](https://github.com/BiswasNehaa/secret-guard/commit/0f01ed5c4844ce266693dced18a29d784929cab5))
* **rules:** add OpenAI, Anthropic, and Discord bot token detection ([#62](https://github.com/BiswasNehaa/secret-guard/issues/62)) ([9b04cd4](https://github.com/BiswasNehaa/secret-guard/commit/9b04cd478bd90a36dfd71f914bbb8240198059c1))
* **rules:** add PyPI, Shopify, Mailgun, and database connection URI rules ([#75](https://github.com/BiswasNehaa/secret-guard/issues/75)) ([a9667a6](https://github.com/BiswasNehaa/secret-guard/commit/a9667a67476e50aac1fbf75370b271ff2f6ca90c))
* **rules:** detect Bearer tokens and generic sk- prefixed secret keys ([9eb505c](https://github.com/BiswasNehaa/secret-guard/commit/9eb505cb01fe06060957800181b14d9ae2746746))
* support max_findings in secret-guard.json config ([#90](https://github.com/BiswasNehaa/secret-guard/issues/90)) ([a229c02](https://github.com/BiswasNehaa/secret-guard/commit/a229c02f19b3b3ba24b6108293ab753c2afe7a32))


### Bug Fixes

* don't run PyPI publish for non-semver tags like v1 ([#40](https://github.com/BiswasNehaa/secret-guard/issues/40)) ([a4e9c03](https://github.com/BiswasNehaa/secret-guard/commit/a4e9c03c9ac4515626e35c4a0f136e0923299c9e))
* keep release-please tags in v0.x.x format ([#33](https://github.com/BiswasNehaa/secret-guard/issues/33)) ([d80cc8d](https://github.com/BiswasNehaa/secret-guard/commit/d80cc8d760cb4341f7eb5f38359262dded3e5d6f))
* point smoke CI and audit at relocated action ([#44](https://github.com/BiswasNehaa/secret-guard/issues/44)) ([bdc4c41](https://github.com/BiswasNehaa/secret-guard/commit/bdc4c41ad9ca467b29a0bb46da468f9b44398ddd))


### Documentation

* add contributor onboarding guide ([#29](https://github.com/BiswasNehaa/secret-guard/issues/29)) ([1d3af92](https://github.com/BiswasNehaa/secret-guard/commit/1d3af92a48a519257903ba9064b44e2efce9c341)), closes [#21](https://github.com/BiswasNehaa/secret-guard/issues/21)
* add Docker usage section to README + fix merge conflict marker in tests ([#35](https://github.com/BiswasNehaa/secret-guard/issues/35)) ([a111738](https://github.com/BiswasNehaa/secret-guard/commit/a1117380c7e57b3f222426fa8b0294689c1caccf))
* professionalize README and sync with current features ([#85](https://github.com/BiswasNehaa/secret-guard/issues/85)) ([eff7b29](https://github.com/BiswasNehaa/secret-guard/commit/eff7b299ff0d77e1004a74a9bb8ccb7920393e29))
* rewrite README with clean formatting and LF line endings ([043b867](https://github.com/BiswasNehaa/secret-guard/commit/043b867bfd7aaaa569440d1f3603051e7f473e8b))


### Miscellaneous Chores

* allow manual dispatch of docker-publish ([#41](https://github.com/BiswasNehaa/secret-guard/issues/41)) ([4a4c0c9](https://github.com/BiswasNehaa/secret-guard/commit/4a4c0c9d375ca6a501e8fd22a47e844801ecee4d))
* bump version to 0.1.2 ([#30](https://github.com/BiswasNehaa/secret-guard/issues/30)) ([dcc72e3](https://github.com/BiswasNehaa/secret-guard/commit/dcc72e3c1d90eb7bfd2216f33697b75e37be18b2))
* **main:** release 0.10.0 ([6920540](https://github.com/BiswasNehaa/secret-guard/commit/6920540f6f9d4d7319eb4fd661c063fd5895cbdc))
* **main:** release 0.2.0 ([#32](https://github.com/BiswasNehaa/secret-guard/issues/32)) ([f8786eb](https://github.com/BiswasNehaa/secret-guard/commit/f8786ebeeb53e9dc559e9c47f60bdee4b6c79037))
* **main:** release 0.3.0 ([#38](https://github.com/BiswasNehaa/secret-guard/issues/38)) ([bc9ec5c](https://github.com/BiswasNehaa/secret-guard/commit/bc9ec5c88f7147236561ecc77645b04fd21cc5dd))
* **main:** release 0.3.1 ([#45](https://github.com/BiswasNehaa/secret-guard/issues/45)) ([ae8210f](https://github.com/BiswasNehaa/secret-guard/commit/ae8210fa514dd811c3b4da8d695bd40e34ea6c8d))
* **main:** release 0.4.0 ([83dc09c](https://github.com/BiswasNehaa/secret-guard/commit/83dc09c4aff081983faf17bb1397456f73638397))
* **main:** release 0.4.0 ([e13104a](https://github.com/BiswasNehaa/secret-guard/commit/e13104aab11b40a3f8cf04b7631b07a3fd97476f))
* **main:** release 0.4.0 ([#63](https://github.com/BiswasNehaa/secret-guard/issues/63)) ([83dc09c](https://github.com/BiswasNehaa/secret-guard/commit/83dc09c4aff081983faf17bb1397456f73638397))
* **main:** release 0.5.0 ([1d830f0](https://github.com/BiswasNehaa/secret-guard/commit/1d830f09817cb9508302ab54aab2500dff1fec28))
* **main:** release 0.5.0 ([02c20de](https://github.com/BiswasNehaa/secret-guard/commit/02c20deb5e8dec51592bf6b4080aaa71af848597))
* **main:** release 0.5.0 ([#68](https://github.com/BiswasNehaa/secret-guard/issues/68)) ([1d830f0](https://github.com/BiswasNehaa/secret-guard/commit/1d830f09817cb9508302ab54aab2500dff1fec28))
* **main:** release 0.6.0 ([#71](https://github.com/BiswasNehaa/secret-guard/issues/71)) ([b970a45](https://github.com/BiswasNehaa/secret-guard/commit/b970a459a2b8ed5844f749f6cbdf2b5682008320))
* **main:** release 0.7.0 ([9a98acb](https://github.com/BiswasNehaa/secret-guard/commit/9a98acbac6ecaefbdc5ac5f06ea5ec44599af9c9))
* **main:** release 0.7.1 ([#86](https://github.com/BiswasNehaa/secret-guard/issues/86)) ([ea9ac9a](https://github.com/BiswasNehaa/secret-guard/commit/ea9ac9ab7f642ba2cae572db400fb82a64a50636))
* **main:** release 0.8.0 ([#88](https://github.com/BiswasNehaa/secret-guard/issues/88)) ([4635a4a](https://github.com/BiswasNehaa/secret-guard/commit/4635a4ac069e1e9c745231d0e3a25b2d041af87a))
* **main:** release 0.9.0 ([4a8f2d1](https://github.com/BiswasNehaa/secret-guard/commit/4a8f2d180821a2320ecf5d5592a017e4d964cb40))
* move community docs out of the repo root ([19afa58](https://github.com/BiswasNehaa/secret-guard/commit/19afa58162b7ace7c380d8f9552651a665ee7b2d))
* streak maintenance ([#87](https://github.com/BiswasNehaa/secret-guard/issues/87)) ([b14a5dd](https://github.com/BiswasNehaa/secret-guard/commit/b14a5dd9f226ea2c0ac265f282122421f26b5af4))


### Code Refactoring

* **scanner:** precompute the exclusions set once in __init__ ([126f75f](https://github.com/BiswasNehaa/secret-guard/commit/126f75f455bd6174228278a71e7838b3c1a743a3))

## [0.10.0](https://github.com/taksh1507/secret-guard/compare/v0.9.0...v0.10.0) (2026-09-06)


### Features

* **cli:** add --summary output to print only the severity summary ([37fa6bf](https://github.com/taksh1507/secret-guard/commit/37fa6bf3deb1f0c76cdc8ee9c969ce0bc2c2a9dd))
* **report:** add XML and HTML report output formats ([7604d04](https://github.com/taksh1507/secret-guard/commit/7604d045762890cacb48d714e89a2f155085d079))
* **rules:** detect Bearer tokens and generic sk- prefixed secret keys ([9eb505c](https://github.com/taksh1507/secret-guard/commit/9eb505cb01fe06060957800181b14d9ae2746746))


### Miscellaneous Chores

* move community docs out of the repo root ([19afa58](https://github.com/taksh1507/secret-guard/commit/19afa58162b7ace7c380d8f9552651a665ee7b2d))

## [0.9.0](https://github.com/taksh1507/secret-guard/compare/v0.8.0...v0.9.0) (2026-09-02)


### Features

* **cli:** add --csv output format for scan results ([77c461e](https://github.com/taksh1507/secret-guard/commit/77c461ea8b0a10e994ea9495927c9c1cb020ab50))
* **cli:** add --quiet flag to suppress scan output ([f02637b](https://github.com/taksh1507/secret-guard/commit/f02637b5e522d6808d40300c4f913571a86388a1))
* **cli:** allow scanning multiple paths with secret-guard scan ([a10c9f7](https://github.com/taksh1507/secret-guard/commit/a10c9f7d26293ab0061af0e61937f68ed8d66814))


### Code Refactoring

* **scanner:** precompute the exclusions set once in __init__ ([126f75f](https://github.com/taksh1507/secret-guard/commit/126f75f455bd6174228278a71e7838b3c1a743a3))

## [0.8.0](https://github.com/taksh1507/secret-guard/compare/v0.7.1...v0.8.0) (2026-08-30)


### Features

* **cli:** add --reveal-prefix and --reveal-suffix for partial masking ([#91](https://github.com/taksh1507/secret-guard/issues/91)) ([64a22a9](https://github.com/taksh1507/secret-guard/commit/64a22a9b5e91853f2a1f42761fdc71f01336ec00))
* support max_findings in secret-guard.json config ([#90](https://github.com/taksh1507/secret-guard/issues/90)) ([a229c02](https://github.com/taksh1507/secret-guard/commit/a229c02f19b3b3ba24b6108293ab753c2afe7a32))


### Documentation

* rewrite README with clean formatting and LF line endings ([043b867](https://github.com/taksh1507/secret-guard/commit/043b867bfd7aaaa569440d1f3603051e7f473e8b))


### Miscellaneous Chores

* streak maintenance ([#87](https://github.com/taksh1507/secret-guard/issues/87)) ([b14a5dd](https://github.com/taksh1507/secret-guard/commit/b14a5dd9f226ea2c0ac265f282122421f26b5af4))

## [0.7.1](https://github.com/taksh1507/secret-guard/compare/v0.7.0...v0.7.1) (2026-08-28)


### Documentation

* professionalize README and sync with current features ([#85](https://github.com/taksh1507/secret-guard/issues/85)) ([eff7b29](https://github.com/taksh1507/secret-guard/commit/eff7b299ff0d77e1004a74a9bb8ccb7920393e29))

## [0.7.0](https://github.com/taksh1507/secret-guard/compare/v0.6.0...v0.7.0) (2026-08-27)


### Features

* add --max-findings to cap scan output ([#77](https://github.com/taksh1507/secret-guard/issues/77)) ([757e842](https://github.com/taksh1507/secret-guard/commit/757e84216bd2aff265efc1dc56da779964eba16c))
* **rules:** add PyPI, Shopify, Mailgun, and database connection URI rules ([#75](https://github.com/taksh1507/secret-guard/issues/75)) ([a9667a6](https://github.com/taksh1507/secret-guard/commit/a9667a67476e50aac1fbf75370b271ff2f6ca90c))

## [0.6.0](https://github.com/taksh1507/secret-guard/compare/v0.5.0...v0.6.0) (2026-08-26)


### Features

* custom rule manifests (closes [#9](https://github.com/taksh1507/secret-guard/issues/9)) ([#70](https://github.com/taksh1507/secret-guard/issues/70)) ([9290242](https://github.com/taksh1507/secret-guard/commit/9290242b58e435fe9f7405aff83c3fe9158229ef))
* **rules:** add GitLab PAT, Hugging Face token, and Slack webhook detection ([#72](https://github.com/taksh1507/secret-guard/issues/72)) ([20a7f65](https://github.com/taksh1507/secret-guard/commit/20a7f659ede74b844dba0b84855ea3d9e6152797))

## [0.5.0](https://github.com/taksh1507/secret-guard/compare/v0.4.0...v0.5.0) (2026-08-24)


### Features

* **cli:** add --severity flag to fail scans only past a severity threshold ([0a6d569](https://github.com/taksh1507/secret-guard/commit/0a6d56919526cfa647b8d3de1cde1e6ca835c26a))
* **cli:** add --severity flag to fail scans only past a severity threshold ([#67](https://github.com/taksh1507/secret-guard/issues/67)) ([0a6d569](https://github.com/taksh1507/secret-guard/commit/0a6d56919526cfa647b8d3de1cde1e6ca835c26a))
* **cli:** add --severity threshold support to scan command ([db4fb8a](https://github.com/taksh1507/secret-guard/commit/db4fb8a8a3e33391490eb0205b85a579cab99ff3))
* **cli:** add --stdin and --filename to scan piped input ([#65](https://github.com/taksh1507/secret-guard/issues/65)) ([08c34aa](https://github.com/taksh1507/secret-guard/commit/08c34aa9711f8262a84ea52c7d6e36b6f13a3019))

## [0.4.0](https://github.com/taksh1507/secret-guard/compare/v0.3.1...v0.4.0) (2026-08-20)


### Features

* **rules:** add OpenAI, Anthropic, and Discord bot token detection ([9b04cd4](https://github.com/taksh1507/secret-guard/commit/9b04cd478bd90a36dfd71f914bbb8240198059c1))
* **rules:** add OpenAI, Anthropic, and Discord bot token detection ([0f01ed5](https://github.com/taksh1507/secret-guard/commit/0f01ed5c4844ce266693dced18a29d784929cab5))
* **rules:** add OpenAI, Anthropic, and Discord bot token detection ([#62](https://github.com/taksh1507/secret-guard/issues/62)) ([9b04cd4](https://github.com/taksh1507/secret-guard/commit/9b04cd478bd90a36dfd71f914bbb8240198059c1))

## [0.3.1](https://github.com/taksh1507/secret-guard/compare/v0.3.0...v0.3.1) (2026-08-18)


### Bug Fixes

* point smoke CI and audit at relocated action ([#44](https://github.com/taksh1507/secret-guard/issues/44)) ([bdc4c41](https://github.com/taksh1507/secret-guard/commit/bdc4c41ad9ca467b29a0bb46da468f9b44398ddd))

## [0.3.0](https://github.com/taksh1507/secret-guard/compare/v0.2.0...v0.3.0) (2026-08-18)


### Features

* add one-line GitHub Action ([#39](https://github.com/taksh1507/secret-guard/issues/39)) ([d3bb8a1](https://github.com/taksh1507/secret-guard/commit/d3bb8a11202afffcb3645534f1360ac6be1b3cc4))
* **cli:** add baseline/allowlist support to suppress known intentional findings ([#36](https://github.com/taksh1507/secret-guard/issues/36)) ([9c660a2](https://github.com/taksh1507/secret-guard/commit/9c660a2f845d5fd8c952ab16a83da074e47842b5))


### Bug Fixes

* don't run PyPI publish for non-semver tags like v1 ([#40](https://github.com/taksh1507/secret-guard/issues/40)) ([a4e9c03](https://github.com/taksh1507/secret-guard/commit/a4e9c03c9ac4515626e35c4a0f136e0923299c9e))


### Documentation

* add Docker usage section to README + fix merge conflict marker in tests ([#35](https://github.com/taksh1507/secret-guard/issues/35)) ([a111738](https://github.com/taksh1507/secret-guard/commit/a1117380c7e57b3f222426fa8b0294689c1caccf))

## [0.2.0](https://github.com/taksh1507/secret-guard/compare/v0.1.2...v0.2.0) (2026-08-18)


### Features

* add per-rule scan controls, release automation, and coverage reporting ([#31](https://github.com/taksh1507/secret-guard/issues/31)) ([6a960b5](https://github.com/taksh1507/secret-guard/commit/6a960b569818aab39e42ae58d0a7975904927bdb))


### Bug Fixes

* keep release-please tags in v0.x.x format ([#33](https://github.com/taksh1507/secret-guard/issues/33)) ([d80cc8d](https://github.com/taksh1507/secret-guard/commit/d80cc8d760cb4341f7eb5f38359262dded3e5d6f))
