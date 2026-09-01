from zemi.component import ZemiComponent


component = ZemiComponent(params_file="@comp/params/default_params.toml")
try:
    component.run()
finally:
    component.close()
