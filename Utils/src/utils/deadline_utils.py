import os
from bootstrap import deadline_bootstrap


def get_deadline() -> str:
    """
    Gets deadline command path.

    Returns:
        str: Deadline command path.
    """
    deadlineBin = ""
    try:
        deadlineBin = os.environ["DEADLINE_PATH"]
    except KeyError:
        pass
    if deadlineBin == "" and os.path.exists("/Users/Shared/Thinkbox/DEADLINE_PATH"):
        with open("/Users/Shared/Thinkbox/DEADLINE_PATH") as f:
            deadlineBin = f.read().strip()
    deadlineCommand = os.path.join(deadlineBin, "deadlinecommand")
    return deadlineCommand
    

def get_pypath() -> str:
    """
    Gets custom python paths from bootstrap.
    Returns:
        str: Custom python paths.
    """
    bootstrapper = deadline_bootstrap.DeadlineBootstrap()
    pipeline_pythonpath = bootstrapper.build_pipeline_pythonpath()
    return pipeline_pythonpath

    