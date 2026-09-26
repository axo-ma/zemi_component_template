# ZEMI Component Template

Initialize the shared component environment from the component root:

```powershell
python 00_init.py
```

`00_init.py` and `00_init.toml` remain in the root. Use the Python interpreter
configured by initialization in VS Code for jobs and notebooks.

## Layout

```text
00_init.py
00_init.toml
example/
    job.py
    playbook.ipynb
    params/params.toml
    params/prompts.md
    params/encoder.py
optimizer_example/
    job.py
    playbook.ipynb
    params/params.toml
    params/prompts.md
    params/encoder.py
data/validation/
    validation.json
    single_table.xlsx
    offset_table.xlsx
    two_tables.xlsx
    no_tables.xlsx
zemi/
```

Both examples use the configured local Qwen 3.5 4B model. Jobs only select
tracked parameters, run the component and close it. Each example has its own
playbook and parameter package and can be changed independently.

## Fixed parameters

```powershell
python example/job.py
```

This performs one model call on `single_table.xlsx`, using the `cells_basic`
prompt and `cells` encoding. No optimizer or score comparison is involved.

## Optimizer

```powershell
python optimizer_example/job.py
```

Grid optimization compares four explicit prompt/encoding bindings:

| Prompt | Encoding | Examples |
|---|---|---|
| cells_basic | cells | None |
| cells_examples | cells | One |
| cells_compact_basic | cells_compact | None |
| cells_compact_examples | cells_compact | One |

Each Sample runs on all four validation items: four Samples and sixteen Runs.
Sample names derive from configured `prompt_name`, e.g. `cells_examples-001`.
Targets are used only by the evaluator and are not sent to the model.

## Validation data

All four synthetic workbooks are tracked in this component, each with one
`Sheet1`. `validation.json` is the authoritative dataset manifest and target
source. These files do not require another repository.

| Workbook | Target |
|---|---|
| single_table.xlsx | A1:C4 |
| offset_table.xlsx | B3:D6 |
| two_tables.xlsx | A1:B4 and D1:E4 |
| no_tables.xlsx | Empty array |

The last workbook contains isolated notes. It is not an empty worksheet.

## Prompts, encoders and reports

One `prompts.md` per example contains all named templates and their examples.
Each `encoding_prompt` parameter value binds `prompt_name`, `prompt_file`,
`encoder` and `encoding_format` in that order. The encoder receives the workbook
path, worksheet name and format and returns text. The playbook inserts that
text at `{{item}}` and requests a JSON object with a `ranges` array.

Outputs include ranges, raw response, LM Time, item tokens and prompt tokens.
LM Time excludes tokenization and notebook execution. Float values in reports
use three decimal places. The optimizer uses `TableDetectionSampleTrial` for
aggregate exact table-boundary F1.

ZEMI generates Review Reports automatically for optimized Modules. The job has
no review setup. ZEMI collects configured prompts, encoders, dataset, SampleTrial,
model configuration, job/playbook/params sources and actual Git provenance.
Dataset Reports show Target separately and exact matches as ✅; long mismatches
link to their full Prediction. Reports and output notebooks are written to
`.tmp/runYYMMDD-HHMMSS/`. Automatic HTML notebook copies are not generated.

Kernel/client reuse is enabled by default in optimizer mode. Set
`reuse_kernel = false` under `[modules.optimizer]` for process isolation.

Canonical library documentation:

- [Params 0.6](zemi/docs/ZEMI_PARAMS_0.6.md)
- [Encoding and prompt packages](zemi/docs/ENCODING_PROMPTS.md)
- [Review Report](zemi/docs/report-specifications/review-report.spec.md)

## Optional external smoke example

The previous OpenRouter Free assets are retained under
`example/optional_openrouter/`. Its configuration is disabled by default and
is separate from the two local jobs. It requires an OpenRouter key and is not
used by validation or optimization.

## Component development

Add dependencies through `00_init.toml` and rerun `00_init.py` when needed.
Follow the component marker, environment, lifecycle and path rules in
`agents.md`. Use `@comp/` and `@inst/` paths in TOML and `env.path` in Python.
