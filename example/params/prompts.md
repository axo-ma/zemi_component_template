# cells_basic

Find every rectangular data table in the worksheet. Include its header and data rows.
Return exactly one JSON object with a "ranges" array of A1 ranges.
Do not include isolated notes or invent cells. When no tables are found, return {"ranges":[]}.

## Input

{{item}}
