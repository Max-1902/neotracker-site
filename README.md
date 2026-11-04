# NEO Tracker website

Static pages for the NEO Tracker iPhone app, served by GitHub Pages at
https://max-1902.github.io/neotracker-site/

- English at the root (`index.html`, `privacy.html`, `support.html`): the App Store links point here
- Other languages in folders: `de/`, `pl/`, `fr/`, `es/`, `it/`
- First-time visitors to the English pages are sent to their browser's language; a language picked in the menu is remembered

## Editing

All text lives in `src/content.json`. Change it there, then rebuild and commit the generated pages:

    python3 src/build.py

The English and German privacy policy are the app's in-app policy (`PrivacyPolicyView` in AboutViews.swift)
word for word; keep them in step when either changes. The other languages are translations, and say that
the English version applies if they differ.

To add a language, add its block to `src/content.json` (same keys as English) and rebuild.
