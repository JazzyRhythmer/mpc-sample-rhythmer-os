# Source and release privacy

Release archives contain product files, technical documentation and required third-party attribution. Source exports contain source and build instructions without local Git history, credentials, private development material, caches or compiled development tools.

`tools/privacy.py` checks export and SD-package contents for private files, personal home paths, credential patterns and discussion records. `tools/export_public.py` also validates the completed source ZIP and supplies checksums. These checks reduce accidental disclosure; they are not a proof that arbitrary future content is safe.

Developer branding and explicitly public social links remain in the product. Copyright, license and source notices remain with their components.

RHYTHMER does not configure remote browser/control services or stock-MPC addin hooks. Third-party plugin binaries execute native code; each accepted engine needs its own source, state, asset and runtime review.
