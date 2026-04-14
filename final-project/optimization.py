from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


try:
    import yaml
except Exception as exc:  # pragma: no cover - import guard for environments without PyYAML
    raise ImportError(
        "PyYAML is required to use RidePlanner. Install it with `pip install pyyaml`."
    ) from exc


@dataclass(frozen=True)
class Attraction:
    name: str
    park: str
    land: str
    type: str
    avg_total_time: float
    time_curve: Dict[int, float]  # minutes since 00:00 -> total_time (scale-3 baseline)


class RidePlanner:
    """
    Greedy, multi-start planner for Disneyland bucket lists.

    Inputs are file paths for data, and a bucket list file containing one attraction per line.
    """

    DAY_SHOW_WINDOW = (10 * 60, 16 * 60)
    NIGHT_SHOW_WINDOW = (19 * 60, 22 * 60)
    BUSINESS_SCALE_MIN = 1
    BUSINESS_SCALE_MAX = 5
    BUSINESS_STEP_PERCENT = 0.15
    ROUND_STEP = 5
    ENTRANCE_NAME = "__ENTRANCE__"
    ENTRANCE_LAND = "Entrance"
    FREE_TIME_NAME = "Free Time"

    def __init__(
        self,
        attractions_path: str | Path,
        land_matrix_path: str | Path,
    ) -> None:
        self.attractions_path = Path(attractions_path)
        self.land_matrix_path = Path(land_matrix_path)

        self.attractions = self._load_attractions(self.attractions_path)
        self.land_matrix = self._load_matrix(self.land_matrix_path)
        self.land_matrix_avg = self._compute_matrix_average(self.land_matrix)

    def plan(
        self,
        bucket_list_path: str | Path,
        start_hour: int,
        end_hour: int,
        business_scale: int,
        park: str,
    ) -> Dict[str, Any]:
        bucket_items = self._load_bucket_list(Path(bucket_list_path))
        start_time = start_hour * 60
        end_time = end_hour * 60
        scale_multiplier = self._business_scale_multiplier(business_scale)

        runs: List[Dict[str, Any]] = []
        for start_item in bucket_items:
            run = self._run_greedy(
                start_item=start_item,
                bucket_items=bucket_items,
                start_time=start_time,
                end_time=end_time,
                scale_multiplier=scale_multiplier,
                park=park,
            )
            if run["schedule"]:
                runs.append(run)

        if not runs:
            dropped = self._build_dropped(bucket_items, scheduled=set(), park=park)
            return {"schedule": [], "dropped": dropped, "end_time": self._fmt_time(start_time)}

        best = self._select_best_run(runs, bucket_items)
        best["dropped"] = self._build_dropped(
            bucket_items, scheduled={e["name"] for e in best["schedule"]}, park=park
        )
        return best

    # ------------------------- Core algorithm -------------------------

    def _run_greedy(
        self,
        start_item: str,
        bucket_items: List[str],
        start_time: int,
        end_time: int,
        scale_multiplier: float,
        park: str,
    ) -> Dict[str, Any]:
        if start_item not in self.attractions:
            return {"schedule": [], "dropped": [], "end_time": self._fmt_time(start_time)}

        start_attraction = self.attractions[start_item]
        if start_attraction.park != park:
            return {"schedule": [], "dropped": [], "end_time": self._fmt_time(start_time)}

        time_cursor = start_time
        schedule: List[Dict[str, Any]] = []
        remaining = [item for item in bucket_items if item != start_item]

        if not self._fits_window(start_attraction, time_cursor, scale_multiplier):
            return {"schedule": [], "dropped": [], "end_time": self._fmt_time(start_time)}

        first_entry = self._schedule_entry(
            from_item=self.ENTRANCE_NAME,
            to_item=start_item,
            start_time=time_cursor,
            scale_multiplier=scale_multiplier,
        )
        if first_entry is None or first_entry["end_minutes"] > end_time:
            return {"schedule": [], "dropped": [], "end_time": self._fmt_time(start_time)}

        schedule.append(self._entry_for_output(first_entry))
        time_cursor = first_entry["end_minutes"]
        current_item = start_item

        while remaining:
            next_choice = self._choose_next(
                current_item=current_item,
                remaining=remaining,
                time_cursor=time_cursor,
                scale_multiplier=scale_multiplier,
                end_time=end_time,
                park=park,
            )
            if next_choice is None:
                wait_plan = self._wait_for_night_show(
                    current_item=current_item,
                    remaining=remaining,
                    time_cursor=time_cursor,
                    scale_multiplier=scale_multiplier,
                    end_time=end_time,
                    park=park,
                )
                if wait_plan is None:
                    break

                if wait_plan["wait_end"] > wait_plan["wait_start"]:
                    schedule.append(
                        self._free_time_output(
                            start_minutes=wait_plan["wait_start"],
                            end_minutes=wait_plan["wait_end"],
                        )
                    )

                next_choice = wait_plan["entry"]
                schedule.append(self._entry_for_output(next_choice))
                time_cursor = next_choice["end_minutes"]
                current_item = next_choice["name"]
                remaining.remove(current_item)
                continue

            schedule.append(self._entry_for_output(next_choice))
            time_cursor = next_choice["end_minutes"]
            current_item = next_choice["name"]
            remaining.remove(current_item)

        return {"schedule": schedule, "dropped": [], "end_time": self._fmt_time(time_cursor)}

    def _choose_next(
        self,
        current_item: str,
        remaining: List[str],
        time_cursor: int,
        scale_multiplier: float,
        end_time: int,
        park: str,
    ) -> Optional[Dict[str, Any]]:
        best: Optional[Dict[str, Any]] = None
        best_score: Optional[float] = None
        current_land = self._item_land(current_item)

        for candidate in list(remaining):
            attraction = self.attractions.get(candidate)
            if attraction is None or attraction.park != park:
                continue
            if not self._fits_window(attraction, time_cursor, scale_multiplier):
                continue

            entry = self._schedule_entry(
                from_item=current_item,
                to_item=candidate,
                start_time=time_cursor,
                scale_multiplier=scale_multiplier,
            )
            if entry is None or entry["end_minutes"] > end_time:
                continue

            avg_time = attraction.avg_total_time
            current_time = entry["item_time_raw"]
            savings = max(0.0, avg_time - current_time)
            # land_bonus = 15 if attraction.land == current_land else 0
            score = entry["walk"]*2 + current_time - savings

            if best_score is None or score < best_score:
                best = entry
                best_score = score

        return best

    def _wait_for_night_show(
        self,
        current_item: str,
        remaining: List[str],
        time_cursor: int,
        scale_multiplier: float,
        end_time: int,
        park: str,
    ) -> Optional[Dict[str, Any]]:
        if time_cursor >= self.NIGHT_SHOW_WINDOW[0]:
            return None

        window_start = self.NIGHT_SHOW_WINDOW[0]
        best_entry: Optional[Dict[str, Any]] = None

        for candidate in list(remaining):
            attraction = self.attractions.get(candidate)
            if attraction is None or attraction.park != park:
                continue
            if not self._is_night_show(attraction):
                continue

            entry = self._schedule_entry(
                from_item=current_item,
                to_item=candidate,
                start_time=window_start,
                scale_multiplier=scale_multiplier,
            )
            if entry is None or entry["end_minutes"] > end_time:
                continue
            if not self._fits_window(attraction, window_start, scale_multiplier):
                continue

            if best_entry is None or entry["end_minutes"] < best_entry["end_minutes"]:
                best_entry = entry

        if best_entry is None:
            return None

        return {
            "wait_start": time_cursor,
            "wait_end": window_start,
            "entry": best_entry,
        }

    # ------------------------- Data helpers -------------------------

    def _load_bucket_list(self, path: Path) -> List[str]:
        lines = path.read_text(encoding="utf-8").splitlines()
        return [line.strip() for line in lines if line.strip()]

    def _load_attractions(self, path: Path) -> Dict[str, Attraction]:
        data = self._load_yaml(path)
        if isinstance(data, dict) and "attractions" in data:
            items = data["attractions"]
        else:
            items = data

        if not isinstance(items, list):
            raise ValueError("attractions.yaml must be a list of attraction entries.")

        attractions: Dict[str, Attraction] = {}
        for raw in items:
            name = raw["name"]
            curve_raw = raw["time_curve"]
            curve = {self._parse_time_key(k): float(v) for k, v in curve_raw.items()}
            attractions[name] = Attraction(
                name=name,
                park=raw["park"],
                land=raw["land"],
                type=raw["type"],
                avg_total_time=float(raw["avg_total_time"]),
                time_curve=curve,
            )
        return attractions

    def _load_matrix(self, path: Path) -> Dict[str, Dict[str, float]]:
        data = self._load_yaml(path)
        if not isinstance(data, dict):
            raise ValueError(f"{path} must be a mapping of mappings.")
        matrix: Dict[str, Dict[str, float]] = {}
        for row_key, row_val in data.items():
            if not isinstance(row_val, dict):
                raise ValueError(f"{path} row {row_key} must be a mapping.")
            matrix[row_key] = {col_key: float(val) for col_key, val in row_val.items()}
        return matrix

    def _load_yaml(self, path: Path) -> Any:
        return yaml.safe_load(path.read_text(encoding="utf-8"))

    # ------------------------- Time helpers -------------------------

    def _parse_time_key(self, key: str) -> int:
        parts = key.split(":")
        if len(parts) != 2:
            raise ValueError(f"Invalid time key: {key}")
        hour = int(parts[0])
        minute = int(parts[1])
        return hour * 60 + minute

    def _fmt_time(self, minutes_since_midnight: int) -> str:
        minutes_since_midnight = max(0, minutes_since_midnight)
        hour = minutes_since_midnight // 60
        minute = minutes_since_midnight % 60
        return f"{hour:02d}:{minute:02d}"

    def _ceil_to_step(self, minutes: float, step: int = ROUND_STEP) -> int:
        if minutes <= 0:
            return 0
        return int(math.ceil(minutes / step) * step)

    # ------------------------- Scheduling helpers -------------------------

    def _schedule_entry(
        self,
        from_item: str,
        to_item: str,
        start_time: int,
        scale_multiplier: float,
    ) -> Optional[Dict[str, Any]]:
        attraction = self.attractions.get(to_item)
        if attraction is None:
            return None

        walk_time = self._walk_time(from_item, to_item)
        item_time = self._curve_time(attraction, start_time, scale_multiplier)

        total_raw = walk_time + item_time
        total_rounded = self._ceil_to_step(total_raw)
        item_time_output = max(0, total_rounded - walk_time)
        end_minutes = start_time + total_rounded

        return {
            "name": to_item,
            "start_minutes": start_time,
            "end_minutes": end_minutes,
            "walk": int(walk_time),
            "item_time": int(item_time_output),
            "item_time_raw": float(item_time),
        }

    def _curve_time(self, attraction: Attraction, time_minutes: int, scale_multiplier: float) -> float:
        curve = attraction.time_curve
        if not curve:
            return attraction.avg_total_time * scale_multiplier

        keys = sorted(curve.keys())
        if time_minutes <= keys[0]:
            base = curve[keys[0]]
        elif time_minutes >= keys[-1]:
            base = curve[keys[-1]]
        else:
            lower_idx = max(i for i, k in enumerate(keys) if k <= time_minutes)
            lower_key = keys[lower_idx]
            upper_key = keys[lower_idx + 1]
            lower_val = curve[lower_key]
            upper_val = curve[upper_key]
            if upper_key == lower_key:
                base = lower_val
            else:
                ratio = (time_minutes - lower_key) / (upper_key - lower_key)
                base = lower_val + ratio * (upper_val - lower_val)

        return base * scale_multiplier

    def _walk_time(self, from_item: str, to_item: str) -> float:
        if from_item == to_item:
            return 0.0

        from_land = self._item_land(from_item)
        to_land = self._item_land(to_item)
        land_walk = self._matrix_lookup(self.land_matrix, from_land, to_land)
        if land_walk is not None:
            return land_walk

        return self.land_matrix_avg or 5.0

    def _item_land(self, item_name: str) -> str:
        if item_name == self.ENTRANCE_NAME:
            return self.ENTRANCE_LAND
        attraction = self.attractions.get(item_name)
        if attraction is None:
            return self.ENTRANCE_LAND
        return attraction.land


    def _matrix_lookup(
        self, matrix: Dict[str, Dict[str, float]], a: str, b: str
    ) -> Optional[float]:
        if a in matrix and b in matrix[a]:
            return matrix[a][b]
        if b in matrix and a in matrix[b]:
            return matrix[b][a]
        return None

    def _compute_matrix_average(self, matrix: Dict[str, Dict[str, float]]) -> float:
        values: List[float] = []
        for row in matrix.values():
            values.extend(row.values())
        if not values:
            return 0.0
        return sum(values) / len(values)

    def _fits_window(
        self, attraction: Attraction, start_minutes: int, scale_multiplier: float
    ) -> bool:
        item_time = self._curve_time(attraction, start_minutes, scale_multiplier)
        end_minutes = start_minutes + item_time

        if self._is_night_show(attraction):
            return self.NIGHT_SHOW_WINDOW[0] <= start_minutes <= self.NIGHT_SHOW_WINDOW[1] and end_minutes <= self.NIGHT_SHOW_WINDOW[1]
        if self._is_day_show(attraction):
            return self.DAY_SHOW_WINDOW[0] <= start_minutes <= self.DAY_SHOW_WINDOW[1] and end_minutes <= self.DAY_SHOW_WINDOW[1]
        return True

    def _is_day_show(self, attraction: Attraction) -> bool:
        return attraction.type.lower() == "show"

    def _is_night_show(self, attraction: Attraction) -> bool:
        return attraction.type.lower() in {"night_show", "nighttime_show", "night_spectacular"}

    # ------------------------- Output helpers -------------------------

    def _entry_for_output(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "start": self._fmt_time(entry["start_minutes"]),
            "end": self._fmt_time(entry["end_minutes"]),
            "name": entry["name"],
            "walk": entry["walk"],
            "item_time": entry["item_time"],
        }

    def _free_time_output(self, start_minutes: int, end_minutes: int) -> Dict[str, Any]:
        duration = max(0, end_minutes - start_minutes)
        return {
            "start": self._fmt_time(start_minutes),
            "end": self._fmt_time(end_minutes),
            "name": self.FREE_TIME_NAME,
            "walk": 0,
            "item_time": duration,
        }

    def _build_dropped(
        self, bucket_items: List[str], scheduled: set[str], park: str
    ) -> List[Dict[str, str]]:
        dropped: List[Dict[str, str]] = []
        for item in reversed(bucket_items):
            if item in scheduled:
                continue
            attraction = self.attractions.get(item)
            if attraction is None:
                reason = "missing_data"
            elif attraction.park != park:
                reason = "wrong_park"
            else:
                reason = "insufficient_time"
            dropped.append({"name": item, "reason": reason})
        return dropped

    def _business_scale_multiplier(self, business_scale: int) -> float:
        if not (self.BUSINESS_SCALE_MIN <= business_scale <= self.BUSINESS_SCALE_MAX):
            raise ValueError("business_scale must be between 1 and 5.")
        return 1.0 + (business_scale - 3) * self.BUSINESS_STEP_PERCENT

    def _select_best_run(
        self, runs: List[Dict[str, Any]], bucket_items: List[str]
    ) -> Dict[str, Any]:
        def run_key(run: Dict[str, Any]) -> Tuple[int, int, int]:
            scheduled_names = {entry["name"] for entry in run["schedule"]}
            dropped_count = len(bucket_items) - len(scheduled_names)
            end_minutes = self._parse_time_key(run["end_time"])
            return (len(scheduled_names), -end_minutes, -dropped_count)

        return max(runs, key=run_key)
