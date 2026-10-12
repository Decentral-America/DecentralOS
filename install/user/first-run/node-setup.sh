# Walk the owner through DecentralChain node setup on first login. Skips quietly
# when the node package is absent or the node is already configured.
command -v decentralos-node >/dev/null || exit 0
[[ -f /etc/decentralchain/dcc.conf ]] && exit 0

setsid omarchy-launch-floating-terminal-with-presentation decentralos-node setup >/dev/null 2>&1 &
