#!/bin/bash
# Публикация сайта: main (источник в site/) -> gh-pages (сайт в корне).
# Работает из чистого состояния main; не трогает рабочую ветку.
# Требует: push-доступ к репозиторию (токен со scope repo, gh auth или SSH).
set -e
cd "$(dirname "$0")"
git checkout -q main
git pull -q origin main || true

TMP=$(mktemp -d)
git archive main site | tar -x -C "$TMP"
cd "$TMP"
mv site/* .
rmdir site
touch .nojekyll

git init -q .
git add -A
git -c user.name=kimicito -c user.email=kimicito@users.noreply.github.com \
    commit -qm "site: $(date +%F)" || true
git push -q "https://github.com/kimicito/ai-agent-harness-course.git" HEAD:gh-pages -f
cd /
rm -rf "$TMP"
echo "опубликовано: https://kimicito.github.io/ai-agent-harness-course/"
