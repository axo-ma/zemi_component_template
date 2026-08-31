from __future__ import annotations

import json
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TemplateTests(unittest.TestCase):
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
        self.assertIn("passed whole to the notebook", text)

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
