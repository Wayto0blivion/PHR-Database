#!/usr/bin/env bash
# Cut a release: tag the default branch and publish a GitHub Release whose
# notes are generated from the pull requests merged since the previous release.
#
#   ./release.sh                  next tag for today: vYYYY.MM.DD, then .2, .3 ...
#   ./release.sh v2026.11.07.5    an explicit tag
#
# Run this on a dev machine with the GitHub CLI (gh) signed in. The checkout
# must be on the default branch, clean, and identical to origin, so that the
# tag lands on exactly what has been reviewed and merged. Deploy the result on
# the server with: ./deploy.sh <tag>
set -euo pipefail

cd "$(dirname "$(readlink -f "$0")")"

die() { echo "ERROR: $*" >&2; exit 1; }

command -v gh >/dev/null 2>&1 || die "GitHub CLI (gh) is required: https://cli.github.com"
gh auth status >/dev/null 2>&1 || die "gh is not signed in. Run: gh auth login"

BRANCH="$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)"
[[ -n "$BRANCH" ]] || die "Could not determine the repository's default branch."

git fetch --quiet --tags --force origin

[[ "$(git rev-parse --abbrev-ref HEAD)" == "$BRANCH" ]] \
    || die "Releases are cut from ${BRANCH}; you are on $(git rev-parse --abbrev-ref HEAD)."
[[ -z "$(git status --porcelain)" ]] \
    || die "The working tree has uncommitted changes."
[[ "$(git rev-parse HEAD)" == "$(git rev-parse "origin/${BRANCH}")" ]] \
    || die "Local ${BRANCH} differs from origin/${BRANCH}. Pull (or push) first."

TAG="${1:-}"
if [[ -z "$TAG" ]]; then
    BASE="v$(date +%Y.%m.%d)"
    TAG="$BASE"
    N=2
    while git rev-parse -q --verify "refs/tags/${TAG}" >/dev/null; do
        TAG="${BASE}.${N}"
        N=$((N + 1))
    done
fi
[[ "$TAG" =~ ^v[0-9]{4}\.[0-9]{2}\.[0-9]{2}(\.[0-9]+)?$ ]] \
    || die "Tag must look like v2026.11.07 or v2026.11.07.2 (got ${TAG})."
! git rev-parse -q --verify "refs/tags/${TAG}" >/dev/null \
    || die "Tag ${TAG} already exists."

PREVIOUS="$(git tag --list 'v*' --sort=-v:refname | head -n 1)"
echo "Releasing ${TAG} from ${BRANCH} at $(git rev-parse --short HEAD)${PREVIOUS:+ (previous release: ${PREVIOUS})}"

gh release create "$TAG" --target "$BRANCH" --title "$TAG" --generate-notes
git fetch --quiet --tags origin

echo
echo "Released ${TAG}. Deploy it on the server with:"
echo "    ./deploy.sh ${TAG}"
