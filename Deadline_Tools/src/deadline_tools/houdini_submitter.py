import os
import hou
from utils import deadline_utils
from utils import file_utils
import tempfile
import subprocess
from typing import Any


class HoudiniSubmitter:
    """
    Custom submitter for Houdini to Deadline.
    """
    def __init__(self, kwargs: dict[str, Any]):
        """
        Initialise values from Houdini submitter node.

        Args:
            kwargs (dict[str]): Keyword arguments from submitter node.
        """
        self.proj = os.getenv("PROJ")
        self.database = os.getenv("DATABASE")

        self.node = kwargs["node"]
        self.shotnum = self.node.parm("shot").rawValue()
        self.version = self.node.parm("version").rawValue()
        self.pypath = deadline_utils.get_pypath()
        self.deadline = deadline_utils.get_deadline()
        self.submit_name = self.node.parm("submit_name").eval()
        self.submit_message = self.node.parm("submit_message").eval()
        self.infile = file_utils.reformat_path(hou.hipFile.path())
        self.renderrop = f"{self.node.path()}/render"
        self.deeprop = f"{self.node.path()}/deep"
        self.outdir = file_utils.reformat_path(os.path.join(os.getenv("PROJ"), "45_render", f"sh{self.shotnum}", self.version))
        self.ocio = os.environ["OCIO"]
        self.machinelimit = self.node.parm("machinelimit").eval()


    def submit_to_deadline(self):
        """
        Creates and submits job to deadline.
        """
        self.get_frames()
        job_info = tempfile.NamedTemporaryFile(delete=False, suffix="_job.info", mode="w", encoding="utf-8")
        plugin_info = tempfile.NamedTemporaryFile(delete=False, suffix="_plugin.info", mode="w", encoding="utf-8")

        job_info.write(
        fr"""Plugin=Houdini
        Name=BushtailBandit_sh{self.shotnum}_{self.version}_{self.submit_name}
        Comment={self.submit_message}
        Pool=main
        Group=none
        Priority=51

        MachineLimit={self.machinelimit}

        Frames={self.framerange}
        ChunkSize=1

        OutputDirectory0={self.outdir}

        EnvironmentKeyValue0=PROJ={self.proj}
        EnvironmentKeyValue1=DATABASE={self.database}

        EnvironmentKeyValue2=PIPELINE_PYTHONPATH={self.pypath}
        EnvironmentKeyValue3=HOUDINI_PYTHONPATH={self.pypath};%HOUDINI_PYTHONPATH%
        EnvironmentKeyValue4=PYTHONPATH={self.pypath};%PYTHONPATH%
        EnvironmentKeyValue5=OCIO={self.ocio}
        """
        )

        job_info.close()

        plugin_info.write(
        fr"""SceneFile={self.infile}

        OutputDriver={self.renderrop}
        Version=20.5
        Renderer=Karma

        IgnoreInputs=True
        UseSceneFrameRange=False
        InitializeSim=False
        """
        )
        plugin_info.close()

        cmd = deadline_utils.get_deadline()

        # Submit job
        subprocess.run([
            cmd,
            job_info.name,
            plugin_info.name
        ])

        hou.ui.displayMessage("Job submitted - Beauty render!")


    def submit_deep_to_deadline(self):
        """
        Creates and submits job to deadline.
        """
        self.get_frames()
        job_info = tempfile.NamedTemporaryFile(delete=False, suffix="_job.info", mode="w", encoding="utf-8")
        plugin_info = tempfile.NamedTemporaryFile(delete=False, suffix="_plugin.info", mode="w", encoding="utf-8")

        job_info.write(
        fr"""Plugin=Houdini
        Name=BushtailBandit_sh{self.shotnum}_{self.version}_deep_{self.submit_name}
        Comment={self.submit_message}
        Pool=main
        Group=none
        Priority=51

        MachineLimit={self.machinelimit}

        Frames={self.framerange}
        ChunkSize=1

        OutputDirectory0={self.outdir}

        EnvironmentKeyValue0=PROJ={self.proj}
        EnvironmentKeyValue1=DATABASE={self.database}

        EnvironmentKeyValue2=PIPELINE_PYTHONPATH={self.pypath}
        EnvironmentKeyValue3=HOUDINI_PYTHONPATH={self.pypath};%HOUDINI_PYTHONPATH%
        EnvironmentKeyValue4=PYTHONPATH={self.pypath};%PYTHONPATH%
        EnvironmentKeyValue5=OCIO={self.ocio}
        """
        )

        job_info.close()

        plugin_info.write(
        fr"""SceneFile={self.infile}

        OutputDriver={self.deeprop}
        Version=20.5
        Renderer=Karma

        IgnoreInputs=True
        UseSceneFrameRange=False
        InitializeSim=False
        """
        )
        plugin_info.close()

        cmd = deadline_utils.get_deadline()

        # Submit job
        subprocess.run([
            cmd,
            job_info.name,
            plugin_info.name
        ])

        hou.ui.displayMessage("Job submitted - Deep camera map!")


    def get_frames(self):
        """
        Gets current frame range to use from submitter node.
        """
        if self.node.parm("trange").eval() == 0:
            self.framerange = f"{int(hou.frame())}"
        else:
            self.framerange = f'{int(self.node.parmTuple("f").eval()[0])}-{int(self.node.parmTuple("f").eval()[1])}'

            