# Deploy and Preview

This project treats `site/` as the local production static website output.

`demo/` is a local file-openable mirror because it includes `data/*.json.js` wrappers. For Firebase Hosting and final local review, use `site/`.

The public GitHub repository should keep the code, templates, methodology documentation, citation files, and license. It should not include production corpus tables, SQLite databases, generated JSON, `site/`, or `demo/`.

## Rebuild

Run the full local rebuild pipeline:

```bash
python3 build_all.py
```

Equivalent Makefile command:

```bash
make rebuild
```

This rebuilds the corpus tables, authority-derived outputs, site JSON, demo mirror, and SQLite database in the local workspace.

## Preview Production Site

Preview the same directory that Firebase Hosting will deploy:

```bash
make preview
```

Open:

```text
http://127.0.0.1:8767/
```

Without Makefile:

```bash
python3 -m http.server 8767 --bind 127.0.0.1 --directory site
```

## Firebase Hosting

`firebase.json` is configured with:

```json
{
  "hosting": {
    "public": "site"
  }
}
```

Deploy:

```bash
firebase deploy
```

If you need to specify a project:

```bash
make deploy-firebase FIREBASE_PROJECT=your-project-id
```

or:

```bash
firebase deploy --project your-project-id
```

## GitHub

Keep only the public research platform materials on GitHub:

- build scripts
- templates
- methodology documentation
- citation files
- license

Do not commit:

- source text
- production CSV tables
- SQLite databases
- generated JSON
- `site/`
- `demo/`

After editing code or documentation:

```bash
git status
git add .
git commit -m "Update Red Chamber Dream knowledge platform"
git push
```

If any generated or production data was previously tracked, remove it from git tracking while keeping local files:

```bash
git rm -r --cached site demo
git rm --cached *.csv *.sqlite *.sqlite-* *.json red-chamber-dream.txt
```

Then commit that cleanup. The files remain on the local machine but will no longer be part of the public repository.

## Demo Mirror

Preview the `demo/` mirror only when you need to check local file-openable behavior:

```bash
make preview-demo
```

or:

```bash
python3 -m http.server 8767 --bind 127.0.0.1 --directory demo
```

Do not use `demo/` as the final production review target for Firebase Hosting, and do not publish `demo/` through GitHub Pages if the public repo should not expose generated data.
