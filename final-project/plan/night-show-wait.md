# Add “Free Time” Gaps Only for Night Shows

## Summary
Insert explicit “Free Time” schedule entries only when a night show is the only feasible remaining item but its window hasn’t opened yet, so the planner can wait until it starts.

## Implementation Changes
1. Add a helper to return the night-show window start/end; keep day-show handling unchanged.
2. In the greedy loop, when `_choose_next` returns `None`, check remaining items for any night shows that:
   - match the park
   - have a window start in the future (>= current time)
   - can finish by `end_time`
3. If found, insert a “Free Time” entry from `time_cursor` to the night-show window start, then schedule the show at that window start.
4. Keep current behavior for day shows and all non-show items.

## Test Plan
1. `time_cursor=17:00`, only night show left, `end_time=22:00`
   - Expect “Free Time” 17:00–19:00, then show at 19:00.
2. `time_cursor=18:50`, night show at 19:00
   - Expect “Free Time” 18:50–19:00, then show at 19:00.
3. `time_cursor=21:40`, night show duration 30, `end_time=22:00`
   - Expect night show dropped, no “Free Time”.
4. Remaining includes a day show later but no night show
   - Expect no waiting; day show remains infeasible until window.

## Assumptions
- Waiting is allowed only for night shows.
- “Free Time” appears explicitly in the schedule output.
