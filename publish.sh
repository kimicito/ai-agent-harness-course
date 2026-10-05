#!/bin/bash
# Публикация сайта: main (источник в site/) -> gh-pages (сайт в корне)
set -e
cd "$(dirname "$0")"
git checkout -q main
git branch -f gh-pages-tmp main
git checkout -q --orphan gh-pages-new gh-pages-tmp 2>/dev/null || true
# проще: собрать дерево в temp и force-push
TMP=$(mktemp -d)
git archive main site | tar -x -C "$TMP"
cd "$TMP" && mv site/* . && rmdir site && touch .nojekyll
git init -q . && git add -A && git -c user.name=kimicito -c user.email=kimicito@users.noreply.github.com commit -qm "site: $(date +%F)" && git push -q "https://github.com/kimicito/ai-agent-harness-course.git" HEAD:gh-pages -f
cd / && rm -rf "$TMP"
git checkout -q main
echo "опубликовано: https://kimicito.github.io/ai-agent-harness-course/"
