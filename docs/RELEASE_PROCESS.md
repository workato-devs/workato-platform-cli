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

```bash
pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    workato-platform-cli

workato --version
```

## Stage 6: Publish to Production PyPI

**IMPORTANT:** Follow this exact order to avoid workflow failures.

### Step 1: Determine the new version number

Check the latest tag:

```bash
git fetch --tags
git tag --sort=-v:refname | head -5
```

Increment appropriately (e.g., `1.0.5` → `1.0.6`).

### Step 2: Merge main into release and push

```bash
# Switch to release branch
git checkout release
git pull origin release

# Merge main into release
git merge origin/main -m "Merge main into release for v1.0.6"

# Push release branch
git push origin release
```

### Step 3: Create and push the version tag

**Only after the release branch is pushed:**

```bash
# Switch to main (or stay on release - they should be at same commit)
git checkout main
git pull origin main

# Create the version tag
git tag 1.0.6

# Push the tag
git push origin 1.0.6
```

### Why This Order Matters

The PyPI workflow triggers on:

- Push to `release` branch
- Push of version tags (e.g., `1.0.6`)

The workflow requires an exact git tag for production releases. If you push the tag first:

1. Tag push triggers workflow
2. Workflow tries to deploy to `release` environment
3. **FAILS** - Tag is not allowed by environment protection rules (only `release` branch is)

By pushing the `release` branch first:

1. Branch push triggers workflow
2. Workflow finds the tag (created locally or already pushed)
3. **SUCCEEDS** - `release` branch is allowed to deploy

## Workflow Triggers Summary

| Trigger                  | Environment | PyPI Target                                     |
| ------------------------ | ----------- | ----------------------------------------------- |
| Push to `test` branch    | test        | Test PyPI                                       |
| Push to `release` branch | release     | Production PyPI                                 |
| Push version tag         | release     | Production PyPI (but may fail protection rules) |
| Manual workflow_dispatch | Selected    | Depends on selection                            |

## Troubleshooting

### "Production releases require an exact git tag"

The release branch was pushed but no matching tag exists. Create and push the tag:

```bash
git tag 1.0.X
git push origin 1.0.X
```

### "Tag is not allowed to deploy to release due to environment protection rules"

The tag was pushed before the release branch. This workflow run will fail - ignore it. Push the release branch to trigger a successful run:

```bash
git checkout release
git merge origin/main
git push origin release
```

### Version mismatch or wrong version published

The version is derived from git tags using `hatch-vcs`. Ensure:

1. The tag follows semver format: `X.Y.Z` (no `v` prefix)
2. The tag points to the commit being released
3. You've fetched all tags: `git fetch --tags`

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

# 3. Release to Production PyPI
git checkout release
git pull origin release
git merge origin/main -m "Merge main into release for vX.Y.Z"
git push origin release

# 4. Create version tag (after release branch push)
git checkout main
git tag X.Y.Z
git push origin X.Y.Z
```
