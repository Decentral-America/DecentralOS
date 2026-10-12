echo "Hand Hermes Desktop the DecentralOS theme as a skin"

# Only the app DecentralOS installed under Install > AI follows the theme by itself.
# A Hermes the user set up some other way keeps whatever skin they chose.
omarchy-pkg-present hermes-desktop || exit 0

# The same hand-over a fresh install does. A Hermes that is not ready or refuses
# the write is reported and done with there; only DecentralOS's own failures return.
omarchy-theme-set-hermes --activate
