from zemi import arsenal
from zemi.arsenal import ArsenalSession
from zemi.component import ZemiComponent


component = ZemiComponent(
    params_file="@comp/params/default_params.toml",
)
arsenal_session = None
try:
    if component.arsenal_start_and_stop_at_job_level:
        arsenal_session = ArsenalSession(component.arsenal_config_path)
        arsenal.begin(arsenal_session, stop_before_begin=True)
    component.run()
finally:
    try:
        if arsenal_session is not None:
            arsenal.end(arsenal_session, stop_after_end=True)
    finally:
        component.close()
