# cells_basic

Find every rectangular data table in the worksheet. Include its header and data rows.
Return exactly one JSON object with a "ranges" array of A1 ranges.
Do not include isolated notes or invent cells. When no tables are found, return {"ranges":[]}.

## Input

{{item}}

# cells_examples

Find every rectangular data table in the worksheet. Include its header and data rows.
Return exactly one JSON object with a "ranges" array of A1 ranges.
Do not include isolated notes or invent cells. When no tables are found, return {"ranges":[]}.

## Example

Input:
A1 = Item
B1 = Count
A2 = Pen
B2 = 2
A3 = Book
B3 = 1
D5 = Reminder: call Alex

Output:
{"ranges":["A1:B3"]}

## Input

{{item}}

# cells_compact_basic

Find every rectangular data table in the worksheet. Include its header and data rows.
Return exactly one JSON object with a "ranges" array of A1 ranges.
Do not include isolated notes or invent cells. When no tables are found, return {"ranges":[]}.

## Input

{{item}}

# cells_compact_examples

Find every rectangular data table in the worksheet. Include its header and data rows.
Return exactly one JSON object with a "ranges" array of A1 ranges.
Do not include isolated notes or invent cells. When no tables are found, return {"ranges":[]}.

## Example

Input:
A1=Item|B1=Count|A2=Pen|B2=2|A3=Book|B3=1|D5=Reminder: call Alex

Output:
{"ranges":["A1:B3"]}

## Input

{{item}}
