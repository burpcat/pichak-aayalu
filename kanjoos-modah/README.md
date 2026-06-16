# Kanjoos Modah (Splitwise data parser)

Parses a Splitwise group export and prints a clean per-person expense report — every transaction they were part of, what they owe or are owed, and a running balance throughout.

---

## Usage

```bash
python main.py <file> <name> [output_file]
```

`file` — the exported `.csv` or `.xlsx` from Splitwise  
`name` — exact column header for the person (as it appears in the export)  
`output_file` — optional, saves the report to a `.txt` file instead of printing

Example:
```bash
python main.py spl.csv "Snake Ahh MF" report.txt
```

---

## Input format

A standard Splitwise group export. Each person is a column; values are their share of that expense (positive = they paid and are owed, negative = someone else covered them and they owe).

---

## Dependencies

```bash
pip install pandas openpyxl
```

---

## License

View-only. See root [`README.md`](../README.md).
