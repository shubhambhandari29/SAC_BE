import argparse
import csv
import re
from typing import Iterable, TextIO

from db import get_raw_connection


_CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def _sanitize_value(value: str) -> str:
    cleaned = value.replace("\x00", "")
    cleaned = _CONTROL_CHARS_RE.sub("", cleaned)
    return cleaned.strip()


def _iter_rows(csv_path: str, encoding: str) -> Iterable[tuple[str, str]]:
    with open(csv_path, newline="", encoding=encoding, errors="replace") as handle:
        reader = csv.DictReader(handle)
        fieldnames = {name.strip() for name in (reader.fieldnames or [])}
        required = {"Agent_Code", "Agent_Name"}
        if not required.issubset(fieldnames):
            missing = ", ".join(sorted(required - fieldnames))
            raise ValueError(f"CSV is missing required columns: {missing}")

        for row in reader:
            agent_code = _sanitize_value(row.get("Agent_Code") or "")
            agent_name = _sanitize_value(row.get("Agent_Name") or "")
            if not agent_code and not agent_name:
                continue
            yield agent_code, agent_name


def _write_error(
    handle: TextIO | None, row: tuple[str, str], error: Exception
) -> None:
    if handle is None:
        return
    handle.write(f"{row[0]},{row[1]},{str(error).replace(chr(10), ' ')}\n")


def load_agents(
    csv_path: str,
    batch_size: int,
    encoding: str,
    error_log: str | None,
    continue_on_error: bool,
) -> int:
    sql = "INSERT INTO tblEDW_AGENT_LIST (Agent_Code, Agent_Name) VALUES (?, ?)"
    total = 0
    batch: list[tuple[str, str]] = []

    conn = get_raw_connection()
    error_handle = None
    try:
        cursor = conn.cursor()
        cursor.fast_executemany = True
        error_handle = open(error_log, "w", encoding="utf-8") if error_log else None
        if error_handle is not None:
            error_handle.write("Agent_Code,Agent_Name,Error\n")

        for row in _iter_rows(csv_path, encoding):
            batch.append(row)
            if len(batch) >= batch_size:
                try:
                    cursor.executemany(sql, batch)
                    conn.commit()
                    total += len(batch)
                    batch.clear()
                except Exception:
                    conn.rollback()
                    if not continue_on_error:
                        raise
                    for item in batch:
                        try:
                            cursor.execute(sql, item)
                            conn.commit()
                            total += 1
                        except Exception as row_exc:
                            conn.rollback()
                            _write_error(error_handle, item, row_exc)
                    batch.clear()

        if batch:
            try:
                cursor.executemany(sql, batch)
                conn.commit()
                total += len(batch)
            except Exception:
                conn.rollback()
                if not continue_on_error:
                    raise
                for item in batch:
                    try:
                        cursor.execute(sql, item)
                        conn.commit()
                        total += 1
                    except Exception as row_exc:
                        conn.rollback()
                        _write_error(error_handle, item, row_exc)
            batch.clear()
    finally:
        if error_handle is not None:
            error_handle.close()
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
    parser.add_argument(
        "--encoding",
        default="utf-8-sig",
        help="CSV file encoding (default: utf-8-sig)",
    )
    parser.add_argument(
        "--error-log",
        default="edw_agent_list_errors.csv",
        help="Path for bad-row log (set to empty to disable)",
    )
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue inserting when a row fails",
    )
    args = parser.parse_args()

    error_log = args.error_log or None
    inserted = load_agents(
        args.csv,
        args.batch_size,
        args.encoding,
        error_log,
        args.continue_on_error,
    )
    print(f"Inserted {inserted} rows into tblEDW_AGENT_LIST")


if __name__ == "__main__":
    main()
