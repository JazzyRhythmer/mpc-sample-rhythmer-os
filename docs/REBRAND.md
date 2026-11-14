# Rhythmer OS naming and upgrade

Product: Rhythmer OS. Developer: jazzy rhythmer. The virtual multi-sound instrument is Rhythmer Kit and sorts first in the plugin browser.

The product source folder, namespace, application class and binary are src/rhythmer, rhythmer, RhythmerApp and autorun/rhythmer. The local checkout is rhythmer-os. New native port folders use RHYTHMER - FM1 / RHYTHMER - Move and product-owned libraries use rhythmer-*.so. Original engine names, vendor credits, VST UIDs and upstream source trees remain intact.

Legacy GROOVE plugin paths and saved sound-state engine names resolve to their Rhythmer equivalents. Existing Groove/Presets directories, legacy engine subfolder names and .groove.json saved slots are still readable. New saves use Rhythmer/Presets and .rhythmer.json; legacy originals are retained. Existing MELODEE1 project files and original native state-control keys retain compatibility. These strings are compatibility readers rather than visible product names.

Back up the SD card and replace the complete beta package, including Plugins. Keep previous card contents separately; avoid merging old and new native plugin directories, which can duplicate browser entries. Existing projects can keep their old recorded paths: the loader prefers a renamed folder when available, including on a merged card where the old folder still exists. The browser hides that duplicate old folder.

Development storage remains SSD-backed. Existing build/VM storage and old checkout aliases are retained as compatibility links, preventing a large cache copy or loss of previous build evidence. No historical archive is renamed in place. New archives use RHYTHMER-OS and the current version.

Canonical SSD directories and the dedicated Lima instance now use rhythmer-os. Previous directory names are compatibility symlinks to the canonical data; registered historical QA routes remain valid.
