import os
from pathlib import Path


class DeadlineBootstrap:
    """
    Class to run pre-deadline job submission scripts.
    """
    def __init__(self):
        """
        Initialises root of python packages for final year university group film.
        """
        self.repo_root = os.path.join(os.getenv("PROJ"), "00_config", "PythonPackages")


    def build_pipeline_pythonpath(self) -> list[str]:
        """
        Creates a list of python package paths to add to deadline job python env variables.

        Returns:
            list[str]: List of python package paths.
        """
        repo_root = Path(self.repo_root)

        paths = []
        for src in repo_root.glob("*/src"):
            if src.is_dir():
                # Resolve the path
                resolved = str(src.resolve())

                # Normalize UNC server name
                normalized = resolved.replace(
                    r"\\monster.herts.ac.uk\Projects",
                    r"\\monster\projects"
                )

                # Also normalize slashes
                normalized = normalized.replace("\\", "/")

                paths.append(normalized)

        return os.pathsep.join(paths)



if __name__ == "__main__":
    
    bootstrapper = DeadlineBootstrap()
    print(bootstrapper.build_pipeline_pythonpath())
