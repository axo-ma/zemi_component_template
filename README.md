# ZEMI Component

## Optional OpenRouter Free playbook

`playbook_openrouter_free.ipynb` is an opt-in smoke example for OpenRouter's
`openrouter/free` dynamic router. Its complete batch configuration is
`params/openrouter_free.toml`, where it is disabled by default; the standard
`params/default_params.toml` remains entirely local. Enable it explicitly for
a manual external run. A normal local run never calls an external API or
requests a key. On first
interactive use, Arsenal asks for `OPENROUTER_API_KEY` with `getpass` and stores
it only in `@inst/_secrets/arsenal.env`. Delete that single entry to rotate it.

The selected free model can change between calls, so results are not fully
reproducible. Availability and free-tier rate limits are controlled by
OpenRouter. The smoke request intentionally avoids GBNF and strict structured
output.

Perform all steps below in VS Code opened with the workspace of the current
ZEMI Instance.

## 1. Create the component

Open the VS Code integrated terminal and run:

```powershell
zemi component create my_component
```

The command creates a new ZEMI Component from this template and adds it to the
current workspace. If VS Code asks whether you trust the added directory,
confirm it. Then open an integrated terminal for the created component or
change to its directory:

```powershell
cd my_component
```

## 2. Initialize the Python venv

Open `00_init.py` and click **Run Python File** in the upper-right corner of
the editor. You can run the same script in the VS Code integrated terminal:

```powershell
python 00_init.py
```

`00_init.toml` declaratively describes the component C-bundle, while
`00_init.py` creates or updates the Python venv, installs the Z-bundle and
C-bundle, records their state, and configures the VS Code interpreter. The
new interpreter is used after VS Code starts a new terminal or notebook kernel.

To add component-specific Python libraries:

1. Set the C-bundle version in `REQUIRED_C_BUNDLE_VERSION` in `00_init.toml`.
2. Add component packages to `C_BUNDLE_PACKAGES`, for example:

   ```toml
   REQUIRED_C_BUNDLE_VERSION = "mycomp260816"
   C_BUNDLE_PACKAGES = [
       "requests==2.32.4",
       "openpyxl==3.1.5",
   ]
   ```

3. Run `python 00_init.py` from the component root.
4. Confirm that initialization completes successfully with `VS Code configured`.

`00_init.py` is not limited to installing libraries. When necessary, it can
perform other initial component setup: run installation scripts through
`venv.run_script("@comp/install.py")`, generate configuration, prepare
directories and resources, verify the environment, and perform other
component-specific operations. Place additional operations before
`venv.finalize_install()` and the final `venv.set_as_vscode_interpreter()`.

## 3. Configure and run the component

Each TOML file in `params/` is a complete component configuration with three
explicit levels:

- `pipeline_params` contains pipeline metadata and is not injected into notebooks;
- `component_params` configures the component and is not injected into notebooks
  unless a `playbook_params.__include__` explicitly references one of its tables;
- each `playbooks_params` entry selects a notebook, enables or disables it, and
  passes only its nested `playbook_params` to Papermill.

Run the complete component from its root:

```powershell
python job.exp.py
```

The template contains exactly one default `job.exp.py`. It constructs
`ZemiComponent`, runs its enabled playbooks, propagates failures as a nonzero
process exit, and always closes the component so its report is saved. A
component created from the template may contain any number of job files,
including separate jobs for individual playbooks or other execution flows.
The terminal shows a prominent start and completion or failure block for every
executed playbook, including its total duration and run output path. Executed
notebooks and `report.json` are written under the process-local
`.tmp/runYYMMDD-HHMMSS` directory; source notebooks are not modified. In the
executed copy, every completed code cell is followed by a visible note with
that cell's execution time.

When `params/` contains one TOML file, `ZemiComponent()` selects it
automatically. With multiple files, the default `job.exp.py` asks which one to
use. For unattended execution, select a tracked configuration explicitly:

```python
component = ZemiComponent(
    params_file="@comp/params/experiment.toml",
)
```

Each parameterized notebook must contain one code cell tagged exactly
`parameters`. Use `env.path.comp.root` for the component root and
`env.path.comp.runid` for run-specific output.

### Arsenal configuration and lifecycle

An Arsenal TOML declares its execution mode as model-set metadata:

```toml
[arsenal]
mode = "model" # or "router"
```

The notebook does not pass a mode to `zemi.arsenal.begin()`; `ArsenalSession`
loads and validates it from the selected TOML. In Model Mode every configured
llama server must contain exactly one model.

The primary object model also supports first-class managed and external
endpoints:

```python
session.endpoints.host_llama.models.host_model
session.models["host_model"]
session.check("host_llama", "host_model")
```

Use `kind = "managed"` only for llama.cpp resources owned by Arsenal. The
session may prepare and start those resources, but stops only processes it
started itself. It never kills an existing process merely because it listens on
the configured port. Managed `base_url` is derived from `runtime.host` and
`runtime.port`.

Use `kind = "external"` for an already-running local, VM/WSL/Docker, remote, or
provider endpoint. Arsenal lazily checks and connects to it, but never starts or
stops it. Configure VM host routing in the ZEMI Instance environment and pass it
through `base_url = "${ZEMI_HOST_LLM_BASE_URL}"`; Arsenal does not guess host
addresses. Put keys only in environment variables selected by `api_key_env`.

Safe examples are included in:

- `zemi/llm_managed_endpoint_example.toml` — managed llama.cpp;
- `zemi/llm_external_local_example.toml` — external OpenAI-compatible host;
- `zemi/llm_external_providers_example.toml` — OpenRouter and a direct provider.

Healthchecks support `none`, `tcp`, and `models`; `validate_model = false`
supports endpoints that restrict `/v1/models`. OpenAI-compatible endpoints use
the integrations listed below without making LiteLLM an internal gateway.
`protocol = "anthropic"` is a validated extension boundary, but native Anthropic
clients are a documented next stage and currently raise an explicit unsupported
error. See `zemi/ARSENAL_ENDPOINTS.md` for the complete schema, ownership rules,
secret handling, and migration notes. Existing `[[arsenal.llamas]]` configs stay
supported through strict legacy normalization.

Interactive notebook runs use safe defaults in the cell tagged `parameters`:

```python
arsenal_config_path = "@comp/zemi/llm_curated_set_model_mode.toml"
arsenal_start_and_stop_at_job_level = False
```

For a batch job, `component_params.arsenal` is the shared parameter bucket.
Each applicable `playbook_params` table includes it explicitly:

```toml
[component_params.arsenal]
arsenal_config_path = "@comp/zemi/llm_curated_set_model_mode.toml"
arsenal_start_and_stop_at_job_level = true

[[playbooks_params]]
playbook_name = "playbook.ipynb"
enabled = true

    [playbooks_params.playbook_params]
    __include__ = { ref = "component_params.arsenal" }
    model_name = "lfm2_350m"
```

Local values in `playbook_params` override included values. The default batch
flags are `false/false` because `job.exp.py` owns the outer lifecycle: it stops
the shared Arsenal configuration before the first notebook and guarantees
another stop after the complete job. Notebooks execute exactly the policy
passed by Papermill and therefore do not duplicate the job-level stop
operations.

## 4. Start development

Add your component code, notebooks, data, and settings. When packages or
installation code change, update the RunID in
`REQUIRED_C_BUNDLE_VERSION`.

Importing `zemi` alone does not verify the environment. A playbook should
obtain the environment through `PythonVenv.from_config()` and call `verify()`
before using ZEMI functionality.

## Arsenal library integrations

Each assistant provides ten lazy integrations. The final path segment
explicitly identifies the returned entity:

```python
assistant.clients.openai.client
assistant.clients.litellm.router
assistant.clients.dspy.model
assistant.clients.instructor.client
assistant.clients.pydantic_ai.model
assistant.clients.smolagents.model
assistant.clients.llama_index.model
assistant.clients.httpx.client
assistant.clients.outlines.model
assistant.clients.guidance.model
```

Each object is created on first access and then cached. The low-level
`openai.client` and `httpx.client` integrations pass llama.cpp parameters,
including `grammar` and `json_schema`, without Arsenal library filtering.
