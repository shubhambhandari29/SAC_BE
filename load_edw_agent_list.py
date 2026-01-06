import argparse
import csv
from typing import Iterable

from db import get_raw_connection


def _iter_rows(csv_path: str) -> Iterable[tuple[str, str]]:
    with open(csv_path, newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        fieldnames = {name.strip() for name in (reader.fieldnames or [])}
        required = {"Agent_Code", "Agent_Name"}
        if not required.issubset(fieldnames):
            missing = ", ".join(sorted(required - fieldnames))
            raise ValueError(f"CSV is missing required columns: {missing}")

        for row in reader:
            agent_code = (row.get("Agent_Code") or "").strip()
            agent_name = (row.get("Agent_Name") or "").strip()
            if not agent_code and not agent_name:
                continue
            yield agent_code, agent_name


def load_agents(csv_path: str, batch_size: int) -> int:
    sql = "INSERT INTO tblEDW_AGENT_LIST (Agent_Code, Agent_Name) VALUES (?, ?)"
    total = 0
    batch: list[tuple[str, str]] = []

    conn = get_raw_connection()
    try:
        cursor = conn.cursor()
        cursor.fast_executemany = True
        for row in _iter_rows(csv_path):
            batch.append(row)
            if len(batch) >= batch_size:
                cursor.executemany(sql, batch)
                conn.commit()
                total += len(batch)
                batch.clear()

        if batch:
            cursor.executemany(sql, batch)
            conn.commit()
            total += len(batch)
    finally:
        conn.close()

    return total


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Load EDW agent list CSV into tblEDW_AGENT_LIST",
    )
    parser.add_argument(
        "--csv",
        default="EDW_AGENT_LIST(Sheet1) (1).csv",
        help="Path to the CSV file",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1000,
        help="Number of rows to insert per batch",
    )
    args = parser.parse_args()

    inserted = load_agents(args.csv, args.batch_size)
    print(f"Inserted {inserted} rows into tblEDW_AGENT_LIST")


if __name__ == "__main__":
    main()
