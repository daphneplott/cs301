# Disneyland Ride Planner Function (Multi-Start Greedy)

**Summary**
Build a class-based planner in `final-project/optimization.py` that reads a bucket list file and static YAML data (attractions + walk times). It returns an ordered schedule with timestamps that maximizes bucket-list completion using a greedy score that accounts for walking time, current wait-time curve, and "savings" vs daily average. The greedy algorithm is run once per possible starting ride.

**Implementation Changes**
1. **Planner class + API**
   - Add `RidePlanner` in `final-project/optimization.py`.
   - Init inputs are file paths: `attractions.yaml`, `walk_matrix.yaml`, `land_matrix.yaml`.
   - Public method: `plan(bucket_list_path, start_hour, end_hour, business_scale, park)` returning a dict with `schedule`, `dropped`, `end_time`.
2. **Data schema (YAML in `final-project/data/`)**
   - `attractions.yaml` entries contain:
     - `name`, `park`, `land`, `type`
     - `avg_total_time` (minutes, scale-3 baseline average for the day)
     - `time_curve` mapping half-hour `HH:MM` to **total_time** (minutes, scale-3 baseline)
   - `walk_matrix.yaml` contains attraction-to-attraction walk minutes.
   - `land_matrix.yaml` contains land-to-land walk minutes for fallback.
   - All character/show items live in the same file; `time_curve` can include `0` where wait or duration is negligible.
3. **Time handling**
   - Inputs `start_hour` and `end_hour` are full hours (military); start time is `start_hour:00`.
   - Planner runs in 5-minute steps; advance time by `(walk + current_total_time)` and round up to next 5 minutes.
   - Wait curve values are sampled by **linear interpolation** between half-hour points.
4. **Business scale adjustment**
   - Business scale is 1-5 with linear percent change per step of **15%**.
   - Multipliers: 1 -> 0.70x, 2 -> 0.85x, 3 -> 1.00x, 4 -> 1.15x, 5 -> 1.30x.
   - Apply to `current_total_time` from the curve.
5. **Show windows**
   - Daytime shows: 10:00-16:00.
   - Nighttime spectaculars: 19:00-22:00.
   - Characters have no time windows.
6. **Greedy selection rule (per start item)**
   - For each possible starting item in the bucket list:
     - Begin the schedule with that item if it fits the time window.
     - Then repeatedly select next item with lowest score that fits.
   - Score formula:
     - `current_total_time` from curve (scaled by business scale)
     - `savings = max(0, avg_total_time - current_total_time)`
     - `score = walk_time + current_total_time - savings`
   - Stop when no remaining item fits in the remaining time.
7. **Choosing the best run**
   - Evaluate all runs and pick the best schedule by:
     1. Most completed items
     2. Earliest `end_time` (tie-breaker)
     3. If still tied, pick the run with fewer dropped items from the end of the original bucket list order.
8. **Dropping behavior**
   - If time runs out, drop items from the **end of the bucket list order**.
   - Return a `dropped` list with a reason for each missing item.
9. **Missing data handling**
   - If an attraction is missing from `attractions.yaml`, skip it and add to `dropped`.
   - If a walk time is missing for a pair, infer from `land_matrix.yaml`.

**Return Schema**
- `schedule`: list of entries with fields `start`, `end`, `name`, `walk`, `item_time`
- `dropped`: list of `{name, reason}`
- `end_time`: final time reached

**Test Plan**
1. Business scale multiplier applies correctly (scale 1-5).
2. Time curve interpolation between half-hour points.
3. Greedy selection respects show/night windows.
4. Walking time + item time + rounding rules.
5. Missing attraction -> dropped with reason.
6. Missing walk time -> land fallback used.
7. End-of-list drop order when time runs out.
8. Multi-start greedy selects best run by completion count, then earliest end time.
9. Output schema correctness.

**Assumptions**
- Bucket list file contains one attraction name per line, matching names in `attractions.yaml`.
- Only one park per plan call; no hopping.
- The curve values in `attractions.yaml` are **total_time** (wait + duration) for scale-3 baseline.
- Land names in `attractions.yaml` match `land_matrix.yaml` keys exactly.
- Start/end inputs are full hours; internal scheduling uses minutes.
