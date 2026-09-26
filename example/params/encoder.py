from pathlib import Path


def encode(workbook_path: str | Path, worksheet_name: str, *, format: str) -> str:
    """Serialize nonempty cells; opening and closing Excel belongs to the encoder."""
    from openpyxl import load_workbook
    if format not in {"cells", "cells_compact"}:
        raise ValueError(f"Unknown encoding format: {format}")
    workbook = load_workbook(workbook_path, data_only=True)
    try:
        sheet = workbook[worksheet_name]
        equals = "=" if format == "cells_compact" else " = "
        separator = "|" if format == "cells_compact" else "\n"
        return separator.join(f"{cell.coordinate}{equals}{cell.value}"
                              for row in sheet for cell in row if cell.value is not None)
    finally:
        workbook.close()
