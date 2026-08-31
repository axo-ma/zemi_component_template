from __future__ import annotations

import json
import tomllib
import unittest
from pathlib import Path

from zemi.component import _ParamReferenceResolver


ROOT = Path(__file__).resolve().parents[1]


class TemplateTests(unittest.TestCase):
    def test_bundled_library_resolves_bucket_refs_and_includes(self) -> None:
        document = {
            "param_buckets": {
                "base": {"model": "small", "shared": "base"},
                "extra": {"temperature": 0.2, "shared": "extra"},
            }
        }
        params, origins = _ParamReferenceResolver(document).resolve_table(
            {
                "__include__": [
                    {"ref": "param_buckets.base"},
                    {"ref": "param_buckets.extra"},
                ],
                "shared": "local",
                "copied": {"ref": "param_buckets.base.model"},
            },
            "playbook_params",
        )
        self.assertEqual(params, {"model": "small", "temperature": 0.2, "shared": "local", "copied": "small"})
        self.assertNotIn("__include__", params)
        self.assertEqual(origins["temperature"]["source"], "include")
        self.assertEqual(origins["copied"]["refs"], ["param_buckets.base.model"])
        self.assertNotIn("shared", origins)

    def test_default_toml_is_inert_and_documents_parameter_wrappers(self) -> None:
        path = ROOT / "params" / "default_params.toml"
        text = path.read_text(encoding="utf-8")
        with path.open("rb") as file:
            params = tomllib.load(file)
        expected_arsenal = {
            "arsenal_config_path": "@comp/zemi/llm_curated_set_model_mode.toml",
            "arsenal_stop_before_playbook_begin": False,
            "arsenal_stop_after_playbook_end": False,
        }
        self.assertEqual(params["component_params"]["arsenal"], expected_arsenal)
        self.assertEqual(len(params["playbooks_params"]), 2)
        for index, entry in enumerate(params["playbooks_params"]):
            self.assertEqual(
                entry["playbook_params"]["__include__"],
                {"ref": "component_params.arsenal"},
            )
            resolved, _origins = _ParamReferenceResolver(params).resolve_table(
                entry["playbook_params"],
                f"playbooks_params[{index}].playbook_params",
            )
            self.assertEqual(
                {key: resolved[key] for key in expected_arsenal},
                expected_arsenal,
            )
        self.assertFalse(any(
            isinstance(value, dict) and ({"each", "select"} & set(value))
            for entry in params["playbooks_params"]
            for value in entry.get("playbook_params", {}).values()
        ))
        self.assertIn("#     backend = { select =", text)
        self.assertIn("#     temperature = { each =", text)
        self.assertIn('#     __include__ = { ref = "param_buckets.combined" }', text)
        self.assertIn('#     copied_options = { ref = "param_buckets.model.options" }', text)
        self.assertIn("passed whole to the notebook", text)
        alternate = ROOT / "params" / "default_params 2.toml"
        with alternate.open("rb") as file:
            alternate_params = tomllib.load(file)
        self.assertEqual(
            alternate_params["component_params"]["arsenal"],
            expected_arsenal,
        )
        self.assertEqual(len(alternate_params["playbooks_params"]), 2)
        self.assertTrue(all(
            entry["playbook_params"]["__include__"]
            == {"ref": "component_params.arsenal"}
            for entry in alternate_params["playbooks_params"]
        ))
        self.assertIn('#     __include__ = { ref = "param_buckets.combined" }', alternate.read_text(encoding="utf-8"))

    def test_both_notebooks_have_exactly_one_parameters_tag(self) -> None:
        for name in ("playbook.ipynb", "playbook_excel_ling30_gbnf.ipynb"):
            with self.subTest(name=name):
                notebook = json.loads((ROOT / name).read_text(encoding="utf-8"))
                tagged = [
                    cell for cell in notebook["cells"]
                    if "parameters" in cell.get("metadata", {}).get("tags", [])
                ]
                self.assertEqual(len(tagged), 1)
                self.assertEqual(tagged[0]["metadata"]["tags"], ["parameters"])
                parameter_index = notebook["cells"].index(tagged[0])
                heading = notebook["cells"][parameter_index - 1]
                self.assertEqual(heading.get("id"), "input-parameters-heading")
                self.assertEqual("".join(heading.get("source", [])), "## Input parameters")
                preparation = notebook["cells"][parameter_index + 1]
                self.assertEqual(
                    preparation.get("id"),
                    "playbook-preparation-heading",
                )
                self.assertEqual(
                    "".join(preparation.get("source", [])),
                    "## Playbook preparation",
                )
                defaults = "".join(tagged[0]["source"])
                self.assertIn(
                    'arsenal_config_path = "@comp/zemi/llm_curated_set_model_mode.toml"',
                    defaults,
                )
                self.assertIn("arsenal_stop_before_playbook_begin = True", defaults)
                self.assertIn("arsenal_stop_after_playbook_end = True", defaults)
                working_source = "\n".join(
                    "".join(cell.get("source", []))
                    for cell in notebook["cells"]
                    if cell is not tagged[0]
                )
                self.assertIn("ArsenalSession(arsenal_config_path)", working_source)
                self.assertIn(
                    "stop_before_begin=arsenal_stop_before_playbook_begin",
                    working_source,
                )
                self.assertIn(
                    "stop_after_end=arsenal_stop_after_playbook_end",
                    working_source,
                )
                for cell in notebook["cells"]:
                    if cell is not tagged[0]:
                        self.assertNotIn("parameters", cell.get("metadata", {}).get("tags", []))

    def test_default_job_owns_outer_arsenal_lifecycle(self) -> None:
        source = (ROOT / "job.exp.py").read_text(encoding="utf-8")
        self.assertNotIn("for playbook in component.playbooks", source)
        self.assertNotIn("ExitStack", source)
        self.assertIn("arsenal.begin(arsenal_session, stop_before_begin=True)", source)
        self.assertIn(
            "arsenal.end(arsenal_session, stop_after_end=True)",
            source,
        )
        self.assertLess(source.index("arsenal.begin("), source.index("component.run()"))


if __name__ == "__main__":
    unittest.main()
