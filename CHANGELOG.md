# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0](https://github.com/atriumn/noxaudit/compare/v1.1.3...v2.0.0) (2026-03-13)


### ⚠ BREAKING CHANGES

* `noxaudit run` (no --focus) now audits all 7 focus areas instead of using a day-of-week schedule. The `noxaudit schedule` command is removed. The `schedule` and `frames` config keys are deprecated (emit DeprecationWarning if present).

### Features

* add benchmark runner script and corpus definition ([#81](https://github.com/atriumn/noxaudit/issues/81)) ([51114f2](https://github.com/atriumn/noxaudit/commit/51114f291c88d73877ff10d693eabf94a4130516))
* add frame-based config and schedule system ([#30](https://github.com/atriumn/noxaudit/issues/30)) ([#40](https://github.com/atriumn/noxaudit/issues/40)) ([f9fe12c](https://github.com/atriumn/noxaudit/commit/f9fe12c4b47af4449b31757600d3be52dd05690e))
* add Gemini 2.5 Pro, 3 Flash pricing and 50% batch discount ([7f99c98](https://github.com/atriumn/noxaudit/commit/7f99c98c776352d4b82d6ab97493e2724a44768c))
* add noxaudit baseline command to suppress existing findings on adoption ([#38](https://github.com/atriumn/noxaudit/issues/38)) ([f33e348](https://github.com/atriumn/noxaudit/commit/f33e3482f50b2f146f0e24333b029aa08d9b56fe))
* add noxaudit estimate command with pricing.py ([#37](https://github.com/atriumn/noxaudit/issues/37)) ([2f47d38](https://github.com/atriumn/noxaudit/commit/2f47d3842c03735352c55a89bf7d6ec3172bd3b1)), closes [#28](https://github.com/atriumn/noxaudit/issues/28)
* add OpenAI provider with GPT-5 family support ([#35](https://github.com/atriumn/noxaudit/issues/35)) ([#44](https://github.com/atriumn/noxaudit/issues/44)) ([50290d6](https://github.com/atriumn/noxaudit/commit/50290d6b6d1ebd783060de4716a5904592bbee7e))
* add patterns focus area ([fd9e68e](https://github.com/atriumn/noxaudit/commit/fd9e68e413c2164b9b830267f6b9f491b7219615))
* add SARIF 2.1.0 output format for GitHub Code Scanning ([#39](https://github.com/atriumn/noxaudit/issues/39)) ([d6dba5f](https://github.com/atriumn/noxaudit/commit/d6dba5f9b66901842f29f395344a8914d8b86230))
* add testing, hygiene, dependencies, performance focus areas ([3bd6c3d](https://github.com/atriumn/noxaudit/commit/3bd6c3d4f7090d079462cb5f9b2a3da9a7e985eb))
* batch API support with submit/retrieve split ([afa12cd](https://github.com/atriumn/noxaudit/commit/afa12cdc6aa3cb9485c77ec9f0e4c57396a2ba20))
* benchmark Phase 1 — 10 models × 2 repos quality baseline ([#90](https://github.com/atriumn/noxaudit/issues/90)) ([9fa878a](https://github.com/atriumn/noxaudit/commit/9fa878ad573f8a5504bdcc170ed66e941a6a5019))
* benchmark Phase 2 — consistency analysis ([#119](https://github.com/atriumn/noxaudit/issues/119)) ([452ed9e](https://github.com/atriumn/noxaudit/commit/452ed9e14a895b125d27dabb63bf21135eb08950))
* **benchmark:** add claude-sonnet-4-6, claude-opus-4-6, and openai models to corpus; replace gemini-2.0-flash with gemini-2.5-flash-lite; add gemini-3.1-pro-preview pricing ([#95](https://github.com/atriumn/noxaudit/issues/95)) ([c550fd2](https://github.com/atriumn/noxaudit/commit/c550fd2844b651482dcfbdc04c4e26dede034624))
* **benchmark:** add scorecard analysis script ([#96](https://github.com/atriumn/noxaudit/issues/96)) ([9b222cf](https://github.com/atriumn/noxaudit/commit/9b222cf7ec9f27440504510e43031fbdbf15db06)), closes [#88](https://github.com/atriumn/noxaudit/issues/88)
* combined focus areas + test suite + CI ([c6116b0](https://github.com/atriumn/noxaudit/commit/c6116b075f025001725e55876005fd6972d8250c))
* confidence scoring based on cross-run finding frequency ([#121](https://github.com/atriumn/noxaudit/issues/121)) ([#124](https://github.com/atriumn/noxaudit/issues/124)) ([99543b1](https://github.com/atriumn/noxaudit/commit/99543b16e30c453ae585d65e53cedd0f1fe3fc68))
* implement Gemini Batch API in GeminiProvider (50% discount) ([#71](https://github.com/atriumn/noxaudit/issues/71)) ([d95e2b3](https://github.com/atriumn/noxaudit/commit/d95e2b354fd08745c5fda4c85c008bad33053ef5))
* implement MCP server for AI coding tool integration ([#18](https://github.com/atriumn/noxaudit/issues/18)) ([89063b8](https://github.com/atriumn/noxaudit/commit/89063b87ed4997bd5d940d442ddb8b80f50d1f35))
* initial nightwatch MVP ([2347be8](https://github.com/atriumn/noxaudit/commit/2347be8a0a2c9079739a1d134849ad2d60123f16))
* migrate docs to subdomain ([95787e0](https://github.com/atriumn/noxaudit/commit/95787e012bcc72832f1eb81cffcc2ea9b9531bcf))
* multi-retrieve idempotency + auto GitHub issues ([3543a1d](https://github.com/atriumn/noxaudit/commit/3543a1d057976a27fbdd8b57876803b4c10716da))
* persist structured findings to latest-findings.json and findings-history.jsonl ([#73](https://github.com/atriumn/noxaudit/issues/73)) ([e7388a4](https://github.com/atriumn/noxaudit/commit/e7388a4aaea4e0c8bd100269c1c020669fe0dcee))
* remove schedule/frames from OSS CLI, default --focus to all ([0d3f313](https://github.com/atriumn/noxaudit/commit/0d3f3131533d4090fb9eeed1ca4198390e160b63))
* switch default provider from Anthropic to Gemini Flash ([f49d22f](https://github.com/atriumn/noxaudit/commit/f49d22f4e8c448247656d828c89bc1b943e93f7c))
* wire SARIF output into CLI and runner (issue [#45](https://github.com/atriumn/noxaudit/issues/45)) ([#50](https://github.com/atriumn/noxaudit/issues/50)) ([efe2218](https://github.com/atriumn/noxaudit/commit/efe2218de3675edebd1b5d0bd8311e15e38cb9ed))


### Bug Fixes

* baseline --undo with filters silently removes nothing ([#53](https://github.com/atriumn/noxaudit/issues/53)) ([2333b53](https://github.com/atriumn/noxaudit/commit/2333b53c696ba0b96d8d033c5715c07e9b734ef8))
* **ci:** break draft-email loop by skipping if draft already exists ([088359d](https://github.com/atriumn/noxaudit/commit/088359d80f1b35e545d75c19722e0af3a98bcdf4))
* **ci:** use PAT in draft-email so push re-triggers CI checks ([38d04b7](https://github.com/atriumn/noxaudit/commit/38d04b79a1f9e13b871133a1a0c8fea94986e47e))
* correct .gitignore formatting for Ralph files ([3a5c928](https://github.com/atriumn/noxaudit/commit/3a5c9286438b557ebd47a7f28f459da809f5b4c2))
* cost tracking projected monthly calculation and cache token handling ([#54](https://github.com/atriumn/noxaudit/issues/54)) ([7eb19e5](https://github.com/atriumn/noxaudit/commit/7eb19e55a69ac49673834f0810f0863112f98573))
* enable pymdownx.emoji extension for Material icon rendering ([edbda29](https://github.com/atriumn/noxaudit/commit/edbda297c31ad4745cb45f313f26347a23fa1aa2))
* handle list responses from dedup LLM provider ([#122](https://github.com/atriumn/noxaudit/issues/122)) ([595cd9a](https://github.com/atriumn/noxaudit/commit/595cd9af474aa542e1f71b6641305bec199d9e1a))
* make GeminiProvider import conditional for optional google-genai dependency ([829b5a6](https://github.com/atriumn/noxaudit/commit/829b5a6e24edceb2027097eba14753359615e4a5))
* pre-push hook installs dev and mcp extras before running tests ([9908739](https://github.com/atriumn/noxaudit/commit/9908739287b0e19ba079656f69675b60862306b0))
* remove "daily" assumptions from pricing.py output ([#109](https://github.com/atriumn/noxaudit/issues/109)) ([b689923](https://github.com/atriumn/noxaudit/commit/b6899239762c1d95609b169b53ee124cafb3d22c))
* remove "nightly" branding from tagline and core messaging ([#106](https://github.com/atriumn/noxaudit/issues/106)) ([94124d5](https://github.com/atriumn/noxaudit/commit/94124d524e5a14e04ada78100fee530db310921d))
* rename remaining Nightwatch references to Noxaudit ([c6b27be](https://github.com/atriumn/noxaudit/commit/c6b27be70205c287c0ad53c912277cd8b7e78897))
* resolve CI failures for ruff formatting and mcp import ([366b001](https://github.com/atriumn/noxaudit/commit/366b00184a1cffddf31ebfef773653febff244ea))
* **test:** remove brittle version prefix assertion in SARIF test ([1d7c94e](https://github.com/atriumn/noxaudit/commit/1d7c94e60b19f1a4e5da3d94b6f888258adc74c3))
* wire pre-pass execution into runner and commit prepass module ([#51](https://github.com/atriumn/noxaudit/issues/51)) ([c82c235](https://github.com/atriumn/noxaudit/commit/c82c235dc2e5efce228427a15b4ca935969daa34))
* wire pre-pass execution into runner and commit prepass module ([#52](https://github.com/atriumn/noxaudit/issues/52)) ([acf8053](https://github.com/atriumn/noxaudit/commit/acf805393e8dea521b0e2d9e2f32eddd7fd94b25))


### Miscellaneous

* add .ralph-fix-prompt.txt to .gitignore ([a623159](https://github.com/atriumn/noxaudit/commit/a623159bce94f955d900930c1aed3d4a1002c573))
* add .ralph/ to .gitignore (Ralph session files) ([fa3f6b0](https://github.com/atriumn/noxaudit/commit/fa3f6b0f1adb84a97042c362f82c1536be0e83c5))
* add cryyer release email pipeline ([4b5a816](https://github.com/atriumn/noxaudit/commit/4b5a8167db9ca4ed64f7deb6898200a4ac3a6a4e))
* add dependabot.yml with grouped minor/patch updates ([6fd6018](https://github.com/atriumn/noxaudit/commit/6fd601843f15f5cd45a4703272cdb05322904f94))
* add pre-commit and pre-push hooks for ruff and pytest ([#20](https://github.com/atriumn/noxaudit/issues/20)) ([3909626](https://github.com/atriumn/noxaudit/commit/39096260bf747b66f6f9802ee380d43894484a92))
* add pre-commit and pre-push hooks for ruff and pytest ([#20](https://github.com/atriumn/noxaudit/issues/20)) ([adaf7b2](https://github.com/atriumn/noxaudit/commit/adaf7b2f7a3c8f8b32c8f2b8bf9c45d8dc786a4c))
* add Ralph monitor/prompt files to .gitignore ([6592324](https://github.com/atriumn/noxaudit/commit/6592324194c56968bedb79866278713284e244d9))
* add release-please for automated versioning and changelogs ([1e89397](https://github.com/atriumn/noxaudit/commit/1e89397eed8d111479f364785ac41b2af020d271))
* auto-commit before merge (loop primary) ([f49f91d](https://github.com/atriumn/noxaudit/commit/f49f91d17227148317ac76a4e0152a1ac5b88970))
* clean up tracked artifacts ([291b164](https://github.com/atriumn/noxaudit/commit/291b164dbc9e1fc95fbafa12f9cde449cbbdd714))
* **deps:** bump actions/checkout from 4 to 6 ([ba4561f](https://github.com/atriumn/noxaudit/commit/ba4561f0a4c474606c085ba1d44a1f94352b093d))
* **deps:** bump actions/checkout from 4 to 6 ([f1257f9](https://github.com/atriumn/noxaudit/commit/f1257f968f97228ad9bc6764bbfba43af1157c8d))
* **deps:** bump actions/checkout from 4 to 6 ([#116](https://github.com/atriumn/noxaudit/issues/116)) ([3e752ff](https://github.com/atriumn/noxaudit/commit/3e752ffa6ad89f0ee587638c4a33dc012f01d0db))
* **deps:** bump actions/checkout from 4 to 6 ([#84](https://github.com/atriumn/noxaudit/issues/84)) ([9e30f37](https://github.com/atriumn/noxaudit/commit/9e30f376a8596246e90fcdd055ab5e9485628fc6))
* **deps:** bump actions/download-artifact from 4 to 8 ([#83](https://github.com/atriumn/noxaudit/issues/83)) ([81305cc](https://github.com/atriumn/noxaudit/commit/81305cccb1316f366150bd99c55c213f76138561))
* **deps:** bump actions/setup-python from 5 to 6 ([0b3d2b1](https://github.com/atriumn/noxaudit/commit/0b3d2b19b05e7e55965319f85a9eebd10837f1da))
* **deps:** bump actions/setup-python from 5 to 6 ([08cce79](https://github.com/atriumn/noxaudit/commit/08cce79b3b028fd65fd7dbf31a6e5f09d6f7300f))
* **deps:** bump actions/setup-python from 5 to 6 ([#117](https://github.com/atriumn/noxaudit/issues/117)) ([4a10892](https://github.com/atriumn/noxaudit/commit/4a10892bdd9cae42168d86d7bb6079d8dced091c))
* **deps:** bump actions/setup-python from 5 to 6 ([#86](https://github.com/atriumn/noxaudit/issues/86)) ([4272783](https://github.com/atriumn/noxaudit/commit/427278366cc733253b6fa67d66068b0b61c179c0))
* **deps:** bump actions/upload-artifact from 4 to 7 ([#82](https://github.com/atriumn/noxaudit/issues/82)) ([57cb187](https://github.com/atriumn/noxaudit/commit/57cb18708d9c39215b04e67f305689e1d5b60b51))
* **deps:** bump astral-sh/setup-uv from 5 to 7 ([fa119d6](https://github.com/atriumn/noxaudit/commit/fa119d6c98715dd7e31814d25a4c89a3955371d5))
* **deps:** bump astral-sh/setup-uv from 5 to 7 ([e67a57a](https://github.com/atriumn/noxaudit/commit/e67a57a8045bda986c25177dd193ba25098a6b77))
* **deps:** bump astral-sh/setup-uv from 5 to 7 ([#85](https://github.com/atriumn/noxaudit/issues/85)) ([b0a7acd](https://github.com/atriumn/noxaudit/commit/b0a7acd189265eb451c8c510a07b799e1e7fdc7f))
* group github-actions minor/patch dependabot updates ([d570247](https://github.com/atriumn/noxaudit/commit/d5702479a01a13bd38b10aa7828ee72fe9907c56))
* **main:** release 1.0.0 ([#98](https://github.com/atriumn/noxaudit/issues/98)) ([c606466](https://github.com/atriumn/noxaudit/commit/c6064661273dcadb8a68e57e9cd49c7e8fbeba04))
* **main:** release 1.0.1 ([#100](https://github.com/atriumn/noxaudit/issues/100)) ([053494e](https://github.com/atriumn/noxaudit/commit/053494e130344757acad4927a83b0ab476be7397))
* **main:** release 1.1.0 ([#101](https://github.com/atriumn/noxaudit/issues/101)) ([55980ff](https://github.com/atriumn/noxaudit/commit/55980fff823fadf8ccc36beea2b8f3959c5aeaf1))
* **main:** release 1.1.1 ([#102](https://github.com/atriumn/noxaudit/issues/102)) ([af2e316](https://github.com/atriumn/noxaudit/commit/af2e316c2531923e88654e6d8bf9c59bb7533261))
* **main:** release 1.1.2 ([#107](https://github.com/atriumn/noxaudit/issues/107)) ([f59f0b6](https://github.com/atriumn/noxaudit/commit/f59f0b621f1dbd32651fefd10c1b5d40d4391942))
* **main:** release 1.1.3 ([#110](https://github.com/atriumn/noxaudit/issues/110)) ([9c19eda](https://github.com/atriumn/noxaudit/commit/9c19edab939a560565421afd214929f74bc13d4d))
* OSS repo cleanup ([9ad3d1a](https://github.com/atriumn/noxaudit/commit/9ad3d1af538fc715f76c4a9ec400a413407c15eb))
* remove ralph dev artifacts and improve gitignore ([35ee053](https://github.com/atriumn/noxaudit/commit/35ee0530a55643329a60201ed96b442be94ea9a9))


### Documentation

* add CHANGELOG.md documenting rename and initial release ([61856d0](https://github.com/atriumn/noxaudit/commit/61856d06b5aa809e1d5d769dddd69d14fd8a2690))
* add CONTRIBUTING.md for open source contributors ([5cdeee9](https://github.com/atriumn/noxaudit/commit/5cdeee99a737516ad1ec8803f0eb4817c63453ff))
* add GitHub Actions workflow example for nightly audits ([#72](https://github.com/atriumn/noxaudit/issues/72)) ([24d038e](https://github.com/atriumn/noxaudit/commit/24d038ee6bcb71f35a71ecc9c6cacf003432a053))
* add logo to README ([c6e8bd7](https://github.com/atriumn/noxaudit/commit/c6e8bd7a1d424f75cbab056a3bf299f609a531a0))
* add MCP server setup instructions to README ([421d56d](https://github.com/atriumn/noxaudit/commit/421d56d7fcea2592a125be7644079a9c5bb67990))
* add MkDocs Material documentation site ([7a73f92](https://github.com/atriumn/noxaudit/commit/7a73f920b0e697ae99205e15aaf61ae6014d00d2))
* add SECURITY.md, CODE_OF_CONDUCT.md, and issue templates ([b35ed6a](https://github.com/atriumn/noxaudit/commit/b35ed6ac97e460ea717bfc3912a9b0cb11f7eb87))
* add validation, confidence scoring, and missing CLI commands ([0bb1406](https://github.com/atriumn/noxaudit/commit/0bb140645231a3fefce84f01bee83c5e14e04f6c))
* consolidate provider configuration in README ([#70](https://github.com/atriumn/noxaudit/issues/70)) ([ed440d4](https://github.com/atriumn/noxaudit/commit/ed440d43895724cb8c5fb62fce93a269c3a1f1b9))
* reframe scheduling as optional, not the default path ([#108](https://github.com/atriumn/noxaudit/issues/108)) ([3b83507](https://github.com/atriumn/noxaudit/commit/3b8350782978848c0524e53a928539eb82fe172d))
* update model references and publish benchmark results ([#99](https://github.com/atriumn/noxaudit/issues/99)) ([56d6924](https://github.com/atriumn/noxaudit/commit/56d69244eaea71fc5b17c20bb39eb81374e574ce))
* update README.md with Noxaudit branding ([a03dca8](https://github.com/atriumn/noxaudit/commit/a03dca82a4594ce955c5864bd593fef8f07b74a9))


### Code Refactoring

* make issues footer configurable and fix remaining nightwatch refs ([ba3f606](https://github.com/atriumn/noxaudit/commit/ba3f60683086eb1223dc4e3635ac87a7d733262f))
* rename config file and update .gitignore ([872c3ef](https://github.com/atriumn/noxaudit/commit/872c3ef12af9f8bad52db2209ead7b10211c8721))
* Rename nightwatch → noxaudit for open source release ([77038b1](https://github.com/atriumn/noxaudit/commit/77038b187e013d186838ec237183ff5a40169718))
* rename nightwatch/ directory to noxaudit/ ([f85f095](https://github.com/atriumn/noxaudit/commit/f85f09584943ac8f3debb8ecada9e02831357d89))
* rework all 7 focus prompts for thoroughness and coverage ([a0d94bf](https://github.com/atriumn/noxaudit/commit/a0d94bf382cf4d7da28c3336c7de4e2bb4e2013c))
* update all Python imports from nightwatch to noxaudit ([d6dab14](https://github.com/atriumn/noxaudit/commit/d6dab14c2e3098c3576d0b663fbbe7f25e9b8f39))
* update GitHub Action and CI workflow for noxaudit rename ([8929216](https://github.com/atriumn/noxaudit/commit/89292164ba1a1825e901a8f0df8f0201ab937875))
* update pyproject.toml for noxaudit rename ([2fe1e0d](https://github.com/atriumn/noxaudit/commit/2fe1e0d94e9e0190f31fa35891c1e1e667d8a5bd))

## [1.1.3](https://github.com/atriumn/noxaudit/compare/v1.1.2...v1.1.3) (2026-03-08)


### Bug Fixes

* remove "daily" assumptions from pricing.py output ([#109](https://github.com/atriumn/noxaudit/issues/109)) ([e246fee](https://github.com/atriumn/noxaudit/commit/e246feefcc0ce70819aa5eeea108660cbe03ed1b))

## [1.1.2](https://github.com/atriumn/noxaudit/compare/v1.1.1...v1.1.2) (2026-03-07)


### Bug Fixes

* remove "nightly" branding from tagline and core messaging ([#106](https://github.com/atriumn/noxaudit/issues/106)) ([44e1aef](https://github.com/atriumn/noxaudit/commit/44e1aefdfbb8e38e225ae5bde8828a86f1ff6038))


### Documentation

* reframe scheduling as optional, not the default path ([#108](https://github.com/atriumn/noxaudit/issues/108)) ([469bfa7](https://github.com/atriumn/noxaudit/commit/469bfa7353df9b69f51a02efe965ccc9e831ed5a))

## [1.1.1](https://github.com/atriumn/noxaudit/compare/v1.1.0...v1.1.1) (2026-03-07)


### Miscellaneous

* remove ralph dev artifacts and improve gitignore ([8efbbd6](https://github.com/atriumn/noxaudit/commit/8efbbd6965879a1c8ebc66aa92fd36acea6e6c93))


### Documentation

* add SECURITY.md, CODE_OF_CONDUCT.md, and issue templates ([c31bf08](https://github.com/atriumn/noxaudit/commit/c31bf08a6fec02ba46be70c5162dc8b719a45e1a))

## [1.1.0](https://github.com/atriumn/noxaudit/compare/v1.0.1...v1.1.0) (2026-03-07)


### Features

* add Next.js marketing site and migrate docs to subdomain ([fcb27bf](https://github.com/atriumn/noxaudit/commit/fcb27bf584411c95e0cc6f62749bed5f8e519788))


### Bug Fixes

* **test:** remove brittle version prefix assertion in SARIF test ([caf8ae3](https://github.com/atriumn/noxaudit/commit/caf8ae34217c812b05073178e6f4f4c318b60a91))

## [1.0.1](https://github.com/atriumn/noxaudit/compare/v1.0.0...v1.0.1) (2026-03-06)


### Documentation

* update model references and publish benchmark results ([#99](https://github.com/atriumn/noxaudit/issues/99)) ([438202b](https://github.com/atriumn/noxaudit/commit/438202bc2195c5f282dab9b0d8ed6b8c5216966f))

## [1.0.0](https://github.com/atriumn/noxaudit/compare/v0.1.0...v1.0.0) (2026-03-06)


### ⚠ BREAKING CHANGES

* `noxaudit run` (no --focus) now audits all 7 focus areas instead of using a day-of-week schedule. The `noxaudit schedule` command is removed. The `schedule` and `frames` config keys are deprecated (emit DeprecationWarning if present).

### Features

* add benchmark runner script and corpus definition ([#81](https://github.com/atriumn/noxaudit/issues/81)) ([3930b99](https://github.com/atriumn/noxaudit/commit/3930b994d8874aa8240e316e7c3e290a212e2e5d))
* add frame-based config and schedule system ([#30](https://github.com/atriumn/noxaudit/issues/30)) ([#40](https://github.com/atriumn/noxaudit/issues/40)) ([92cc7b1](https://github.com/atriumn/noxaudit/commit/92cc7b1451d4a402c76a4deb4c9389f09b8b7392))
* add Gemini 2.5 Pro, 3 Flash pricing and 50% batch discount ([793342d](https://github.com/atriumn/noxaudit/commit/793342dccd6849990d5a8713d14a8177d349d32d))
* add noxaudit baseline command to suppress existing findings on adoption ([#38](https://github.com/atriumn/noxaudit/issues/38)) ([5dcce18](https://github.com/atriumn/noxaudit/commit/5dcce1858a6abfba9ffdd73bd6da2f21259914b6))
* add noxaudit estimate command with pricing.py ([#37](https://github.com/atriumn/noxaudit/issues/37)) ([0a5a008](https://github.com/atriumn/noxaudit/commit/0a5a0086fe8433e4d66f9f7b5a23f1dd8559f7f1)), closes [#28](https://github.com/atriumn/noxaudit/issues/28)
* add OpenAI provider with GPT-5 family support ([#35](https://github.com/atriumn/noxaudit/issues/35)) ([#44](https://github.com/atriumn/noxaudit/issues/44)) ([ae77425](https://github.com/atriumn/noxaudit/commit/ae7742549a2e2887501fa7b239332bc8496c88fd))
* add patterns focus area ([fd9e68e](https://github.com/atriumn/noxaudit/commit/fd9e68e413c2164b9b830267f6b9f491b7219615))
* add SARIF 2.1.0 output format for GitHub Code Scanning ([#39](https://github.com/atriumn/noxaudit/issues/39)) ([c139aed](https://github.com/atriumn/noxaudit/commit/c139aed98ec0e60088bb0391db64ff155dfa32f7))
* add testing, hygiene, dependencies, performance focus areas ([3bd6c3d](https://github.com/atriumn/noxaudit/commit/3bd6c3d4f7090d079462cb5f9b2a3da9a7e985eb))
* batch API support with submit/retrieve split ([afa12cd](https://github.com/atriumn/noxaudit/commit/afa12cdc6aa3cb9485c77ec9f0e4c57396a2ba20))
* benchmark Phase 1 — 10 models × 2 repos quality baseline ([#90](https://github.com/atriumn/noxaudit/issues/90)) ([5937b78](https://github.com/atriumn/noxaudit/commit/5937b78df4a7bd0ef6abf09d16b2fa5cd565ee11))
* **benchmark:** add claude-sonnet-4-6, claude-opus-4-6, and openai models to corpus; replace gemini-2.0-flash with gemini-2.5-flash-lite; add gemini-3.1-pro-preview pricing ([#95](https://github.com/atriumn/noxaudit/issues/95)) ([a9eab32](https://github.com/atriumn/noxaudit/commit/a9eab3229c4b8ef31016040ef93920a2f137b28a))
* **benchmark:** add scorecard analysis script ([#96](https://github.com/atriumn/noxaudit/issues/96)) ([ab9404a](https://github.com/atriumn/noxaudit/commit/ab9404a09c941405ae19442be40fa34d89013432)), closes [#88](https://github.com/atriumn/noxaudit/issues/88)
* combined focus areas + test suite + CI ([c6116b0](https://github.com/atriumn/noxaudit/commit/c6116b075f025001725e55876005fd6972d8250c))
* implement Gemini Batch API in GeminiProvider (50% discount) ([#71](https://github.com/atriumn/noxaudit/issues/71)) ([df7d9be](https://github.com/atriumn/noxaudit/commit/df7d9beb44e1a7b0fc702d522e986d15381ca8ad))
* implement MCP server for AI coding tool integration ([#18](https://github.com/atriumn/noxaudit/issues/18)) ([71f2e46](https://github.com/atriumn/noxaudit/commit/71f2e4673e0e50ef7e82bdd3f6fc40e4b2aac6d3))
* initial nightwatch MVP ([2347be8](https://github.com/atriumn/noxaudit/commit/2347be8a0a2c9079739a1d134849ad2d60123f16))
* multi-retrieve idempotency + auto GitHub issues ([3543a1d](https://github.com/atriumn/noxaudit/commit/3543a1d057976a27fbdd8b57876803b4c10716da))
* persist structured findings to latest-findings.json and findings-history.jsonl ([#73](https://github.com/atriumn/noxaudit/issues/73)) ([fd5bb5f](https://github.com/atriumn/noxaudit/commit/fd5bb5f1252ffe8969bef96b433b83af71a35441))
* remove schedule/frames from OSS CLI, default --focus to all ([b3a8109](https://github.com/atriumn/noxaudit/commit/b3a8109f9764e56e4acd1872152cf2888f14332b))
* switch default provider from Anthropic to Gemini Flash ([016cfd8](https://github.com/atriumn/noxaudit/commit/016cfd82ea66b05db539716115fe88d081ab485a))
* wire SARIF output into CLI and runner (issue [#45](https://github.com/atriumn/noxaudit/issues/45)) ([#50](https://github.com/atriumn/noxaudit/issues/50)) ([2a27517](https://github.com/atriumn/noxaudit/commit/2a275175551b413ec41bd204089d67de9ce0a66d))


### Bug Fixes

* baseline --undo with filters silently removes nothing ([#53](https://github.com/atriumn/noxaudit/issues/53)) ([d82b74c](https://github.com/atriumn/noxaudit/commit/d82b74cff99b95101db2853d52ad5d0204635e7d))
* **ci:** break draft-email loop by skipping if draft already exists ([6e0fb1c](https://github.com/atriumn/noxaudit/commit/6e0fb1c6c3a362bec7311ae4aaf3c0e27f309d41))
* **ci:** use PAT in draft-email so push re-triggers CI checks ([6590a0a](https://github.com/atriumn/noxaudit/commit/6590a0a503c084af0e296f4234eb91f58186c138))
* correct .gitignore formatting for Ralph files ([468f249](https://github.com/atriumn/noxaudit/commit/468f24998a4f93b13993cc0b364a26b3effe5d9d))
* cost tracking projected monthly calculation and cache token handling ([#54](https://github.com/atriumn/noxaudit/issues/54)) ([6aea210](https://github.com/atriumn/noxaudit/commit/6aea21099b04c35900c92e6bcb066f0b745d0d75))
* enable pymdownx.emoji extension for Material icon rendering ([1503cbf](https://github.com/atriumn/noxaudit/commit/1503cbf22b08bbe7e64962221c7075474ed33f57))
* make GeminiProvider import conditional for optional google-genai dependency ([8fa563d](https://github.com/atriumn/noxaudit/commit/8fa563d288be627ee152745b1582d983ee5ef8c0))
* pre-push hook installs dev and mcp extras before running tests ([883cb62](https://github.com/atriumn/noxaudit/commit/883cb62147c1e25464c38ceeb22b072ca30fb34c))
* rename remaining Nightwatch references to Noxaudit ([3564560](https://github.com/atriumn/noxaudit/commit/3564560bfa492d252b5ef4d1a9d9e2c39e9fc299))
* resolve CI failures for ruff formatting and mcp import ([6b0a801](https://github.com/atriumn/noxaudit/commit/6b0a801f99670049ccf762b44f667040c849edb6))
* wire pre-pass execution into runner and commit prepass module ([#51](https://github.com/atriumn/noxaudit/issues/51)) ([d0840fa](https://github.com/atriumn/noxaudit/commit/d0840fac7f1f23dc7197694e29aedf55db5c0b56))
* wire pre-pass execution into runner and commit prepass module ([#52](https://github.com/atriumn/noxaudit/issues/52)) ([aba462b](https://github.com/atriumn/noxaudit/commit/aba462ba5ce41527a59ab8ca3f8f3ed63611b389))


### Miscellaneous

* add .ralph-fix-prompt.txt to .gitignore ([a2f7b6b](https://github.com/atriumn/noxaudit/commit/a2f7b6b69d578b40465b8de9dafd3b19377b437e))
* add .ralph/ to .gitignore (Ralph session files) ([f287cc9](https://github.com/atriumn/noxaudit/commit/f287cc9631031fa7dfad2049fe202faa8e69a751))
* add cryyer release email pipeline ([fb9a817](https://github.com/atriumn/noxaudit/commit/fb9a8179deddde8c10f3fea66ba11ea4e2dd17a0))
* add dependabot.yml with grouped minor/patch updates ([231b0cb](https://github.com/atriumn/noxaudit/commit/231b0cba3cdacce10ca44d79e7992712835ec483))
* add pre-commit and pre-push hooks for ruff and pytest ([#20](https://github.com/atriumn/noxaudit/issues/20)) ([e54291c](https://github.com/atriumn/noxaudit/commit/e54291c6081b90d257553deb6d92eb6588548f9b))
* add pre-commit and pre-push hooks for ruff and pytest ([#20](https://github.com/atriumn/noxaudit/issues/20)) ([5d570d3](https://github.com/atriumn/noxaudit/commit/5d570d3f0718019973034639c2d608abe1e92599))
* add Ralph monitor/prompt files to .gitignore ([e910abc](https://github.com/atriumn/noxaudit/commit/e910abcb7c87b953aa1e8759b307e48430c370e6))
* add release-please for automated versioning and changelogs ([0378986](https://github.com/atriumn/noxaudit/commit/03789863778741a0f5691a535d734ecb610f8921))
* auto-commit before merge (loop primary) ([43f4366](https://github.com/atriumn/noxaudit/commit/43f43662168cfed98859247180ddc27da6ff37b5))
* **deps:** bump actions/checkout from 4 to 6 ([feb0073](https://github.com/atriumn/noxaudit/commit/feb0073fe4779c6309ce18b4663831e1b239db7b))
* **deps:** bump actions/checkout from 4 to 6 ([94026ea](https://github.com/atriumn/noxaudit/commit/94026ea2c1756bc6d409b31dc260b9057ec90e7f))
* **deps:** bump actions/checkout from 4 to 6 ([#84](https://github.com/atriumn/noxaudit/issues/84)) ([7aa6a89](https://github.com/atriumn/noxaudit/commit/7aa6a8913db94ced82930033f214a62a57104c25))
* **deps:** bump actions/download-artifact from 4 to 8 ([#83](https://github.com/atriumn/noxaudit/issues/83)) ([c4988a6](https://github.com/atriumn/noxaudit/commit/c4988a635c54d5649a331e9d7b45d11ba51f5022))
* **deps:** bump actions/setup-python from 5 to 6 ([d6c98ee](https://github.com/atriumn/noxaudit/commit/d6c98ee7a310135b6bb6c879a7600854ad49d962))
* **deps:** bump actions/setup-python from 5 to 6 ([4f46cf5](https://github.com/atriumn/noxaudit/commit/4f46cf508fd805dc1daa7c5e206b42ef38152943))
* **deps:** bump actions/setup-python from 5 to 6 ([#86](https://github.com/atriumn/noxaudit/issues/86)) ([921cde3](https://github.com/atriumn/noxaudit/commit/921cde3ea76d302592369fa95b2e0730bf5666f8))
* **deps:** bump actions/upload-artifact from 4 to 7 ([#82](https://github.com/atriumn/noxaudit/issues/82)) ([c1983ff](https://github.com/atriumn/noxaudit/commit/c1983ff4af4c98bd71521532c61bc248a3780972))
* **deps:** bump astral-sh/setup-uv from 5 to 7 ([d6cb39f](https://github.com/atriumn/noxaudit/commit/d6cb39f950e7462eeb00728e415ac963f665fac6))
* **deps:** bump astral-sh/setup-uv from 5 to 7 ([55a2ba5](https://github.com/atriumn/noxaudit/commit/55a2ba5075ddb44db50957ce517842dd468a4aba))
* **deps:** bump astral-sh/setup-uv from 5 to 7 ([#85](https://github.com/atriumn/noxaudit/issues/85)) ([edc0471](https://github.com/atriumn/noxaudit/commit/edc0471d5ebadb2c9b09ae4b9e38634d52e4cff7))
* group github-actions minor/patch dependabot updates ([8724411](https://github.com/atriumn/noxaudit/commit/8724411d31ea54d476f4ee7dfab9c0b5eb639eec))
* remove Ralph session artifacts from git tracking ([a2c1ffb](https://github.com/atriumn/noxaudit/commit/a2c1ffbf76aae0d889ca3ea2fd1bdd6fe25be99b))


### Documentation

* add CHANGELOG.md documenting rename and initial release ([61856d0](https://github.com/atriumn/noxaudit/commit/61856d06b5aa809e1d5d769dddd69d14fd8a2690))
* add CONTRIBUTING.md for open source contributors ([5cdeee9](https://github.com/atriumn/noxaudit/commit/5cdeee99a737516ad1ec8803f0eb4817c63453ff))
* add GitHub Actions workflow example for nightly audits ([#72](https://github.com/atriumn/noxaudit/issues/72)) ([6274dc2](https://github.com/atriumn/noxaudit/commit/6274dc2d6050ccebc26162fc55bbb930d2f0feb9))
* add logo to README ([e019440](https://github.com/atriumn/noxaudit/commit/e0194403b604cbfa012adbb0c9d541e1a9fa6315))
* add MkDocs Material documentation site ([d371b24](https://github.com/atriumn/noxaudit/commit/d371b24c0356d391b7660a9a3cddb835d0b9b698))
* consolidate provider configuration in README ([#70](https://github.com/atriumn/noxaudit/issues/70)) ([2b7176f](https://github.com/atriumn/noxaudit/commit/2b7176f2e1059918be64b33641b3cf2fbc4f8a31))
* update README.md with Noxaudit branding ([a03dca8](https://github.com/atriumn/noxaudit/commit/a03dca82a4594ce955c5864bd593fef8f07b74a9))


### Code Refactoring

* make issues footer configurable and fix remaining nightwatch refs ([ba3f606](https://github.com/atriumn/noxaudit/commit/ba3f60683086eb1223dc4e3635ac87a7d733262f))
* rename config file and update .gitignore ([872c3ef](https://github.com/atriumn/noxaudit/commit/872c3ef12af9f8bad52db2209ead7b10211c8721))
* Rename nightwatch → noxaudit for open source release ([82fa94d](https://github.com/atriumn/noxaudit/commit/82fa94dcc6c79d6c7c79fe0f11411c16e64ebdc4))
* rename nightwatch/ directory to noxaudit/ ([f85f095](https://github.com/atriumn/noxaudit/commit/f85f09584943ac8f3debb8ecada9e02831357d89))
* rework all 7 focus prompts for thoroughness and coverage ([f670cf2](https://github.com/atriumn/noxaudit/commit/f670cf2cfe586f7ce6f2ffd4754e1d34b262b82c))
* update all Python imports from nightwatch to noxaudit ([d6dab14](https://github.com/atriumn/noxaudit/commit/d6dab14c2e3098c3576d0b663fbbe7f25e9b8f39))
* update GitHub Action and CI workflow for noxaudit rename ([8929216](https://github.com/atriumn/noxaudit/commit/89292164ba1a1825e901a8f0df8f0201ab937875))
* update pyproject.toml for noxaudit rename ([2fe1e0d](https://github.com/atriumn/noxaudit/commit/2fe1e0d94e9e0190f31fa35891c1e1e667d8a5bd))

## [Unreleased]

### Changed
- Renamed project from Nightwatch to Noxaudit for better GitHub uniqueness
- Package name changed from `nightwatch-ai` to `noxaudit`
- CLI command changed from `nightwatch` to `noxaudit`
- Configuration file renamed from `nightwatch.yml` to `noxaudit.yml`
- Working directory changed from `.nightwatch/` to `.noxaudit/`
- Made GitHub issue footer repository URL configurable via `repository_url` config field

## [0.1.0] - 2026-02-15

### Added
- Initial release
- Multi-provider AI support (Anthropic, Google Gemini)
- Rotating focus areas: security, patterns, docs, hygiene, performance, dependencies, testing
- Decision memory system to avoid re-flagging resolved issues
- GitHub Actions integration
- Telegram notifications
- GitHub issue creation
- Two-pass audit for large codebases
