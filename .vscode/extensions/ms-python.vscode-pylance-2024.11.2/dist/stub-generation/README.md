## Stub-Generation for native stubs

This folder has a couple of python scripts used for extracting stubs from native python libs.

You run it like so:

-   python -m pip install <lib you want to scrape>
-   python -m scrape_lib <path to site-packages/lib name> <path to site-packages> <output folder>

Stubs will be generated in the output folder. After that's done, you can copy them over the bundled stubs.

See the launch.json for examples.
