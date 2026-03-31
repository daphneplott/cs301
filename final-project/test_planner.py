from pathlib import Path

from optimization import RidePlanner


def main() -> None:
    root = Path(__file__).resolve().parent
    data_dir = root / "data"

    planner = RidePlanner(
        attractions_path=data_dir / "attractions.yaml",
        land_matrix_path=data_dir / "land_matrix.yaml",
    )

    bucket_list_path = root / "disneyland_bucket_list.txt"

    result = planner.plan(
        bucket_list_path=bucket_list_path,
        start_hour=8,
        end_hour=22,
        business_scale=3,
        park="Disneyland Park",
    )

    print("Schedule:")
    for entry in result["schedule"]:
        print(
            f"{entry['start']}-{entry['end']} | {entry['name']} | walk {entry['walk']} min | item {entry['item_time']} min"
        )

    print("\nDropped:")
    for drop in result["dropped"]:
        print(f"{drop['name']} ({drop['reason']})")

    print(f"\nEnd time: {result['end_time']}")


if __name__ == "__main__":
    main()
