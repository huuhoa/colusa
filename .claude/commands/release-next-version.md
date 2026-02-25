Release the next version of colusa. Follow these steps exactly:

## Step 1 — Determine the next version

Read `src/colusa/_version.py` to get the current version. Ask the user which version part to bump (major / minor / patch) if they have not already specified it, then compute the new version string `NEW_VERSION`.

## Step 2 — Bump version in files

Edit these files, replacing the current version with `NEW_VERSION`:

- `src/colusa/_version.py` — `__version__ = 'NEW_VERSION'`
- `pyproject.toml` — `version = "NEW_VERSION"` under `[project]`
- `pyproject.toml` — `current_version = "NEW_VERSION"` under `[tool.bumpversion]`

## Step 3 — Generate changelog

Create a temporary local tag so gitchangelog groups commits under the new version,
generate the changelog, then delete the local tag (the squash merge will change the
commit hash, so the tag must be re-created on main after the merge):

```sh
git tag vNEW_VERSION
.venv/bin/gitchangelog > CHANGELOG.md
git tag -d vNEW_VERSION
```

## Step 4 — Commit, open PR, and squash-merge

```sh
git checkout -b release/vNEW_VERSION
git add src/colusa/_version.py pyproject.toml CHANGELOG.md
git commit -m "chg: bump version to NEW_VERSION"
gh pr create --title "release: vNEW_VERSION" --body "Release vNEW_VERSION"
gh pr merge <pr-number> --squash
git checkout main
git pull --rebase
```

## Step 5 — Tag the release on main

After the squash merge has landed, create and push the tag on the actual merge commit:

```sh
git tag vNEW_VERSION
git push origin vNEW_VERSION
```

## Step 6 — Build and upload to PyPI

```sh
rm -rf dist/
.venv/bin/python -m build
.venv/bin/twine upload dist/*
```

## Step 7 — Create GitHub release

```sh
gh release create vNEW_VERSION --title "vNEW_VERSION" --notes "See CHANGELOG.md for details."
```

Confirm with the user after each major step before proceeding to the next.
