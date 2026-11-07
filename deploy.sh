#!/usr/bin/env bash
# Deploy a tagged release of this repository's Docker Compose stack.
#
#   ./deploy.sh                 deploy the newest release tag
#   ./deploy.sh v2026.11.07     deploy that tag (this is also how you roll back)
#
# Releases are git tags named vYYYY.MM.DD or vYYYY.MM.DD.N, cut with
# ./release.sh on a dev machine. Production never tracks a branch: the
# checkout is left detached at the deployed tag, so "git describe --tags"
# always says what is running.
#
# Credential files (ENV_FILES below) are NOT tracked in git and exist only on
# this machine. They are copied aside before anything else happens, restored
# on every exit path (including failures), and the deploy refuses to start if
# one is missing.
#
# The script normally lives in the checkout it deploys. To run a copy from
# somewhere else, point it at the checkout: DEPLOY_DIR=~/flask/PHR-Database bash deploy.sh
set -euo pipefail

# ---- per-repository settings -------------------------------------------------
ENV_FILES=(.env .env.db)        # untracked credential files to protect
# ------------------------------------------------------------------------------

cd "${DEPLOY_DIR:-$(dirname "$(readlink -f "$0")")}"

BACKUP_DIR="${HOME}/env-backups/$(basename "$PWD")"
STAMP="$(date +%Y%m%d-%H%M%S)"
REQUESTED_TAG="${1:-}"

die() { echo "ERROR: $*" >&2; exit 1; }

restore_env_files() {
    local f backup
    for f in "${ENV_FILES[@]}"; do
        backup="${BACKUP_DIR}/${f}.${STAMP}"
        [[ -f "$backup" ]] || continue
        if [[ ! -f "$f" ]] || ! cmp -s "$f" "$backup"; then
            cp -p "$backup" "$f"
            echo "Restored $f from $backup"
        fi
    done
}

echo "==> Pre-flight checks"
docker info >/dev/null 2>&1 || die "Docker daemon is not reachable. Try: sudo systemctl enable --now docker"
docker compose version >/dev/null 2>&1 || die "Docker Compose v2 plugin is not installed (docker-compose-plugin)."
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || die "$PWD is not a git checkout."
for f in "${ENV_FILES[@]}"; do
    [[ -f "$f" ]] || die "$f is missing. Create it from ${f}.example before deploying."
done

echo "==> Fetching release tags"
git fetch --quiet --tags --force origin

if [[ -z "$REQUESTED_TAG" ]]; then
    REQUESTED_TAG="$(git tag --list 'v*' --sort=-v:refname | head -n 1)"
    [[ -n "$REQUESTED_TAG" ]] || die "No release tags found. Cut one with ./release.sh first."
fi
git rev-parse -q --verify "refs/tags/${REQUESTED_TAG}^{commit}" >/dev/null \
    || die "Tag ${REQUESTED_TAG} does not exist. Available: $(git tag --list 'v*' --sort=-v:refname | head -n 5 | tr '\n' ' ')"

CURRENT="$(git describe --tags --always 2>/dev/null || echo unknown)"
echo "==> Deploying ${REQUESTED_TAG} (currently ${CURRENT})"

echo "==> Backing up credential files to ${BACKUP_DIR}"
mkdir -p "$BACKUP_DIR"
chmod 700 "$BACKUP_DIR"
for f in "${ENV_FILES[@]}"; do
    cp -p "$f" "${BACKUP_DIR}/${f}.${STAMP}"
done
trap restore_env_files EXIT

# Older checkouts still have the credential files under version control. Any
# local edits to them would make git refuse the checkout, so reset them to the
# committed version first; the trap above puts the real files back afterwards.
for f in "${ENV_FILES[@]}"; do
    if git ls-files --error-unmatch "$f" >/dev/null 2>&1; then
        git checkout -- "$f"
    fi
done

echo "==> Checking out ${REQUESTED_TAG}"
git checkout --quiet --detach "refs/tags/${REQUESTED_TAG}"

restore_env_files

echo "==> Building images"
docker compose build

echo "==> Restarting the stack"
docker compose down
docker compose up -d

echo "==> Status"
docker compose ps

# Keep the last ten backups of each file.
for f in "${ENV_FILES[@]}"; do
    ls -1t "${BACKUP_DIR}/${f}."* 2>/dev/null | tail -n +11 | xargs -r rm -f
done

echo "Deployed ${REQUESTED_TAG} ($(git rev-parse --short HEAD))."
