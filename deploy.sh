#!/usr/bin/env bash
# Deploy the PHR Database stack on the web server.
#
#   ./deploy.sh
#
# Steps: back up the local credential files, fast-forward the checkout to
# origin, put the credential files back exactly as they were, rebuild the
# images, then restart the stack with Docker Compose v2 ("docker compose").
#
# .env and .env.db are NOT tracked in git. They exist only on this machine, so
# this script treats them as precious: they are copied aside before anything
# else happens, restored on every exit path (including failures), and the
# deploy refuses to start if either is missing.
#
# The script normally lives in the checkout it deploys. To run a copy from
# somewhere else (e.g. the very first deploy, before the checkout has this
# file), point it at the checkout: PHR_DIR=~/flask/PHR-Database bash deploy.sh
set -euo pipefail

cd "${PHR_DIR:-$(dirname "$(readlink -f "$0")")}"

ENV_FILES=(.env .env.db)
BACKUP_DIR="${HOME}/phr-env-backups"
STAMP="$(date +%Y%m%d-%H%M%S)"

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
trap restore_env_files EXIT

echo "==> Backing up credential files to ${BACKUP_DIR}"
mkdir -p "$BACKUP_DIR"
chmod 700 "$BACKUP_DIR"
for f in "${ENV_FILES[@]}"; do
    if [[ ! -f "$f" ]]; then
        echo "ERROR: $f is missing. Create it from ${f}.example before deploying." >&2
        exit 1
    fi
    cp -p "$f" "${BACKUP_DIR}/${f}.${STAMP}"
done

# Older checkouts still have the credential files under version control. Any
# local edits to them would make git refuse the pull, so reset them to the
# committed version first; the trap above puts the real files back afterwards.
for f in "${ENV_FILES[@]}"; do
    if git ls-files --error-unmatch "$f" >/dev/null 2>&1; then
        git checkout -- "$f"
    fi
done

echo "==> Updating git repository"
git pull --ff-only

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

echo "Docker is back online!"
