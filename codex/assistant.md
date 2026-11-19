## Codex Assistant timer

Periodic Assistant checks use the Dogwatch launcher timer when started with
`--profile dogwatch-assistant` in Herdr and enabled in `dogwatch.toml`. Launches
with `resume`, `fork` or `--worktree` do not start timers because the final checkout
may differ; start a fresh Assistant in the intended checkout.

- The timer sends a periodic-check prompt when Herdr reports this session idle or
  done; do not start another timer or a sleep loop. While paused, skip periodic prompts.
- Before confirming scheduling, verify `DOGWATCH_WATCH_PID` is a live process whose
  parent is `DOGWATCH_WATCH_OWNER_PID`. Missing values or a missing/mismatched process
  mean no active timer; explain the need to update the launcher or restart Assistant.
- Removing `[assistant.watch]` or disabling every source stops the timer; restart
  Assistant after enabling it again. Outside the installed launcher, explain that
  automatic checks are unavailable instead of claiming they are scheduled.
