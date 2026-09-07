# Northline

WordPress 6.9 block theme. Install this directory as a theme and activate it. The installation harness inserts the `benchmark-fixture/landing` pattern into the home page. For a manual installation, insert “Northline agency landing page” into a page and select that page as the static homepage under Settings → Reading.

## Editing

Open the Home page in the WordPress page editor. The headline is a Heading block, the artwork an Image block, and the project link a Button block. Edit these blocks and click Save; the templates render the saved page through native Post Content. All remaining page sections are editable blocks as well. Header and footer are reusable template parts, editable in Appearance → Editor.

To use the alternative artwork, select the hero Image block, choose Replace → Insert from URL, and use the installed theme's `assets/replacement.svg` URL. Update its alternative text to describe the new artwork. The SVG is retained locally alongside the three original artworks.

The contact section uses the fixture's `[benchmark_contact]` shortcode. This theme only styles its form; validation and local synthetic submission storage remain with the fixture. No external resources or submission endpoints are added.

Public checks during development reported active block-theme status, 53 valid content blocks, no PHP errors, and no axe violations. Desktop and mobile previews were inspected, and mobile keyboard navigation was exercised.
