# Dream of the Red Chamber Knowledge Platform Demo

This directory contains a deployable pure static website version built with HTML + JavaScript + JSON, requiring no backend.

The demo supports two opening methods simultaneously:

- Open `index.html` directly
- Open it through a local or production web server

## Entry Points

- `index.html`: platform homepage
- `person_social_graph.html`: character social network / relationship graph

## Directory Structure

- `assets/`: CSS styles for the demo site, including the main site, relationship graph, and co-occurrence graph
- `data/`: JSON data actually read by the frontend
- `data/*.json.js`: wrapped data files used when opening directly with `file://`
- `vendor/`: third-party frontend libraries, currently only the local version of D3
- `csv/`: source and proofreading CSV tables, not directly read by the frontend

## Local Testing

### Download Only the Demo for Local Display

If you only want to browse the demo version, you do not need to download the entire project or rebuild the data. Please preserve and download the complete `demo/` folder. The directory structure should include at least:

```text
demo/
├── index.html
├── person_social_graph.html
├── cooccurrence_graph.html
├── assets/
├── data/
└── vendor/
```

After downloading, you can directly open it in the browser:

```text
demo/index.html
```

`demo/data/*.json.js` files are generated to support direct opening via `file://`, so normal browsing, search, statistics, character relationship graphs, and co-occurrence graphs can all work locally.

Notes:

- Do not copy only a single `index.html`, otherwise CSS, JSON, and chart libraries will fail to load.
- `vendor/` contains the local version of D3, which is required for the character relationship graph and co-occurrence graph.
- If your browser restricts local file access, use the local server method below instead.

Run the following in the project root directory:

```bash
python3 -m http.server 8767 --directory demo
```

Then open:

```text
http://127.0.0.1:8767/
```

## Deployment

Deploy the entire `demo/` directory to any static website hosting service. Please keep the relative paths between `data/`, `vendor/`, and the HTML files unchanged.
