# Contributing

1. Branch from a fresh `main`: `git switch -c <type>/<short-name>`.
2. Change `_src/` (data, templates, styles), then rebuild:

   ```bash
   uv run _src/build.py
   ```

3. Commit the sources and every file the build changed together, open a PR into `main`, squash-merge.
   There are no CI checks, so read the generated diff.
4. Merging is publishing. Within about a minute GitHub Pages serves the new pages, and `publish.yml` copies them to
   `idea-denyshotsalo/team`.

Rules:

- **Real people only with their consent.** A card is public: name, title, phone, email. Examples and screenshots
  use `scripts/demo_people.json` (`*.test` domains). Git history is forever.
- **Never edit generated pages by hand** (`<slug>/`, `guide/`, the root `index.html`): the next build overwrites
  them. The old phone generator's `card-site.zip` has the old design; never upload it.
- **Removing a person:** delete the entry and run `git rm -r <slug>`. The build does not prune folders.
- **Secrets:** only `TEAM_DEPLOY_KEY` in the repo's Actions secrets. Nothing secret goes into files.
- **Template changes:** check them on the demo site, `uv run scripts/demo_site.py --serve`, and re-shoot the README
  screenshots with `uv run scripts/screenshots.py` (needs Google Chrome).
- **Workflow changes:** a merge that touches `.github/workflows/*` with a token lacking the `workflow` scope starts
  no Actions run; the next merge or a re-run publishes.
