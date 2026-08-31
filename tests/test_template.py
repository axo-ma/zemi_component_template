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
        self.assertEqual(len(params["playbooks_params"]), 2)
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
        self.assertEqual(len(alternate_params["playbooks_params"]), 2)
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
                for cell in notebook["cells"]:
                    if cell is not tagged[0]:
                        self.assertNotIn("parameters", cell.get("metadata", {}).get("tags", []))


if __name__ == "__main__":
    unittest.main()
