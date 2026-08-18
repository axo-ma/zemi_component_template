# ZEMI Component

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

## 3. Verify the playbook

Open `playbook.ipynb` in VS Code and run all cells. If VS Code asks you to
select a kernel, choose the Python interpreter configured in the previous
step. The playbook verifies the Python venv and its Z-bundle and C-bundle
stamps from that interpreter. Confirm that the notebook runs without errors.

## 4. Start development

Add your component code, notebooks, data, and settings. When packages or
installation code change, update the RunID in
`REQUIRED_C_BUNDLE_VERSION`.

Importing `zemi` alone does not verify the environment. After the import,
user code must obtain the environment through `PythonVenv.from_config()` and
call `verify()`. Use ZEMI functionality only after verification succeeds.

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
