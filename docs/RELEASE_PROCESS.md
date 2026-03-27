# Release Process

This document covers the complete workflow from creating a feature/bug fix branch through publishing to PyPI.

## Overview

The release pipeline uses three main branches:

- `main` - Primary development branch, receives merged PRs
- `test` - Publishes to Test PyPI for validation
- `release` - Publishes to Production PyPI

## Stage 1: Create Feature/Bug Fix Branch

```bash
# Ensure you're on latest main
git checkout main
git pull origin main

# Create your feature/bug branch
git checkout -b fix/your-bug-name
# or
git checkout -b feat/your-feature-name
```

## Stage 2: Develop and Test Locally

```bash
# Make your changes...

# Run linting
uv run ruff check src/ tests/

# Run type checking
uv run mypy src/ tests/

# Run tests
uv run pytest tests/ -v

# Format code if needed
uv run ruff format src/ tests/
```

## Stage 3: Commit and Push

```bash
# Stage your changes
git add <files>

# Commit with descriptive message
git commit -m "fix(component): description of the fix"

# Push to remote
git push origin fix/your-bug-name
```

## Stage 4: Create Pull Request

1. Go to GitHub and create a PR from your branch to `main`
2. Fill in the PR description with:
   - Summary of changes
   - Problem being solved
   - Testing performed
3. Wait for CI checks to pass (lint, test workflows)
4. Get PR reviewed and approved
5. Merge PR to `main`

## Stage 5: Publish to Test PyPI (Optional but Recommended)

After PR is merged to main, publish to Test PyPI for validation:

```bash
# Fetch latest changes
git fetch origin

# Switch to test branch
git checkout test
git pull origin test

# Merge main into test
git merge origin/main -m "Merge main into test for testing"

# Push to trigger Test PyPI workflow
git push origin test
```

The workflow will automatically:

- Build the package with a dev version (e.g., `1.0.6.dev0`)
- Publish to Test PyPI
- Attempt installation verification

### Verify Test PyPI Installation

Using pipx (recommended):

```bash
pipx install --python python3.12 \
    --index-url https://test.pypi.org/simple/ \
    --pip-args="--extra-index-url https://pypi.org/simple/" \
    workato-platform-cli==1.0.6.dev0

workato --version
```

Using pip:

```bash
pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    workato-platform-cli==1.0.6.dev0

workato --version
```

**Note:** Replace `1.0.6.dev0` with the actual dev version published. Check Test PyPI for available versions: https://test.pypi.org/project/workato-platform-cli/

## Stage 6: Publish to Production PyPI

### Step 1: Determine the new version number

Check the latest tag:

```bash
git fetch --tags
git tag --sort=-v:refname | head -5
```

Increment appropriately (e.g., `1.0.5` → `1.0.6`).

### Step 2: Create the version tag on main

The version tag must exist before pushing to release, as `hatch-vcs` uses it to determine the package version.

```bash
git checkout main
git pull origin main

# Create the version tag
git tag 1.0.6

# Push the tag (this does NOT trigger the PyPI workflow)
git push origin 1.0.6
```

### Step 3: Merge main into release and push

```bash
# Switch to release branch
git checkout release
git pull origin release

# Merge main into release
git merge origin/main -m "Merge main into release for v1.0.6"

# Push release branch (this triggers the PyPI workflow)
git push origin release
```

### How Versioning Works

The PyPI workflow only triggers on branch pushes (`test` or `release`), not on tag pushes. However, tags are still essential:

- `hatch-vcs` reads git tags to determine the package version
- When the `release` branch is pushed, the workflow runs `git describe --tags --exact-match` to find the version
- If no exact tag exists on the current commit, the build fails with "Production releases require an exact git tag"

This is why the tag must be created before (or at the same time as) pushing the release branch.

## Workflow Triggers Summary

| Trigger                  | Environment | PyPI Target      |
| ------------------------ | ----------- | ---------------- |
| Push to `test` branch    | test        | Test PyPI        |
| Push to `release` branch | release     | Production PyPI  |
| Manual workflow_dispatch | Selected    | Depends on input |

**Note:** Tag pushes do not trigger the workflow. Tags are only used for version detection by `hatch-vcs`.

## Troubleshooting

### "Production releases require an exact git tag"

The release branch was pushed but no matching tag exists on the current commit. Create and push the tag:

```bash
git checkout main
git pull origin main
git tag 1.0.X
git push origin 1.0.X
```

Then push the release branch again (or wait for the tag to be available and re-run the workflow).

### Version mismatch or wrong version published

The version is derived from git tags using `hatch-vcs`. Ensure:

1. The tag follows semver format: `X.Y.Z` (no `v` prefix)
2. The tag points to the exact commit being released
3. You've fetched all tags: `git fetch --tags`

### Test PyPI shows unexpected dev version

Test PyPI versions are automatically generated as dev versions (e.g., `1.0.6.dev3`). The number increments based on commits since the last tag. This is expected behavior for the test environment.

## Quick Reference: Complete Release Commands

```bash
# After PR is merged to main...

# 1. Update local main
git checkout main
git pull origin main

# 2. (Optional) Test on Test PyPI
git checkout test
git pull origin test
git merge origin/main -m "Merge main into test"
git push origin test

# 3. Create version tag
git checkout main
git tag X.Y.Z
git push origin X.Y.Z

# 4. Release to Production PyPI
git checkout release
git pull origin release
git merge origin/main -m "Merge main into release for vX.Y.Z"
git push origin release
```
