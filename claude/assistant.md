## Claude Assistant timer

For enabled periodic Assistant checks, use the native `CronList`, `CronCreate`
and `CronDelete` tools.

- Identify this repository's timer with the prompt prefix `Dogwatch periodic check:`
  and its absolute path. Reuse a matching timer; replace only your own timer when
  the interval changes.
- Set `recurring: false` and `durable: false` for a one-shot check at the next due
  local date and time; schedule the next after each completed check, even when there
  are no findings. Compute the due time from `interval_minutes`; do not use cron step
  expressions that reset at hour boundaries for intervals such as 45 or 90 minutes.
- The prompt must name the repository and direct Assistant to reread `dogwatch.toml`
  and follow its periodic-check procedure. Delete your timer when paused or disabled,
  and reconcile restored timers on resume.
- If scheduling tools are unavailable (including when `CLAUDE_CODE_DISABLE_CRON=1`),
  report that checks are unavailable.
