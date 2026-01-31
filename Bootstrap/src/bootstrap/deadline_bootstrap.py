import os
from pathlib import Path


class DeadlineBootstrap:
    def __init__(self):
        self.repo_root = os.path.join(os.getenv("PROJ"), "00_config", "PythonPackages")


    def build_pipeline_pythonpath(self):
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
