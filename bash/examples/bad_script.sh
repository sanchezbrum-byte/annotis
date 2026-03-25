#!/bin/bash
# ❌ BAD: /bin/bash not portable — use #!/usr/bin/env bash
# ❌ BAD: No usage documentation
# ❌ BAD: No set -euo pipefail — errors are silently ignored

# ❌ BAD: hardcoded secret in script
DB_PASSWORD=hunter2
API_KEY=sk_live_hardcoded_key_1234
# ❌ BAD: hardcoded production URL
DEPLOY_URL=https://prod.myapp.internal/deploy

# ❌ BAD: variable not quoted — word splitting and globbing
function deploy {  # ❌ BAD: 'function' keyword is non-POSIX; just use deploy() {}
  env=$1  # ❌ BAD: 'env' shadows the system 'env' command; no local keyword
  version=$2  # ❌ BAD: no local, no quotes
  
  # ❌ BAD: unquoted variable — breaks with spaces in paths
  echo Deploying $version to $env
  
  # ❌ BAD: no validation of arguments — will continue even if $1 is empty
  
  # ❌ BAD: eval with user-supplied argument — arbitrary code execution
  eval "docker tag myapp $version"
  
  # ❌ BAD: rm -rf with unquoted variable — catastrophic if var is empty
  rm -rf /tmp/deploy_cache/$env
  # If $env is empty, this becomes: rm -rf /tmp/deploy_cache/ — deletes everything!
  
  # ❌ BAD: using ls output for file iteration — breaks with spaces in filenames
  for f in `ls /tmp/configs/`; do  # ❌ also: backtick syntax
    cp $f /etc/myapp/  # ❌ BAD: no quotes
  done
  
  # ❌ BAD: curl without error checking, without -f flag
  # If this fails, script continues silently (no set -e)
  curl https://api.example.com/webhook -d "deployed=$version"
  
  # ❌ BAD: no checking if deployment succeeded
  echo "Done"  
}

# ❌ BAD: no argument validation
deploy $1 $2
# If called without arguments: deploy "" "" — undefined behavior

# ❌ BAD: writing to /tmp with predictable name — TOCTOU race condition
TMPFILE=/tmp/myapp_deploy_output
# An attacker can create a symlink at this path before the script does
echo "deploy output" > $TMPFILE

# ❌ BAD: no cleanup — temp files leak
# ❌ BAD: no trap for cleanup on exit

# ❌ BAD: using 'which' instead of 'command -v'
if which docker > /dev/null; then  # 'which' is not POSIX; use: command -v docker
  echo docker found
fi

# ❌ BAD: [ ] instead of [[ ]] in bash — more error-prone
if [ $DB_PASSWORD = hunter2 ]; then
  echo "default password in use!"  # ❌ BAD: this never gets noticed
fi

# ❌ BAD: global variable from function (no local)
get_version() {
  VERSION="$(cat version.txt)"  # ❌ BAD: modifies global — implicit side effect
}
