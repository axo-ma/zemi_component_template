"""Run this example using the component's configured Python environment."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from zemi.component import ZemiComponent

component = ZemiComponent(params_file="@comp/example/params/params.toml")
try:
    component.run()
finally:
    component.close()
