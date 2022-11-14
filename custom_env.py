"""Extend Talon Python environment with arbitrary packages from a venv."""
import os
import sys
import platform

class CustomEnv:
    """Context manager for briefly shifting into another virtual environment

    Use this to import packages not shipped with Talon, but are basically irreplaceable e.g. OpenCV

    Shift - import - shift back, to minimise potential weirdness with packages from different environments
    """

    def __init__(
        self,
        env_path=os.path.join(os.path.expanduser("~"), "anaconda3", "envs", "talon"),
    ):
        target_subdirs = [
            "lib",
            "",
            os.path.join("lib", "site-packages"),
        ]

        self.new_paths = [os.path.join(env_path, x) for x in target_subdirs]
        self.path_insert_loc = 2  # So local and python base are still first

        self.org_path = sys.path

        if any(platform.win32_ver()):
            self.using_win = True

            dll_subdirs = ["DLLs", os.path.join("Library", "bin")]
            self.dll_paths = [os.path.join(env_path, x) for x in dll_subdirs]

            win_specific_dirs = [
                os.path.join("lib", "site-packages", "win32"),
                os.path.join("lib", "site-packages", "win32", "lib"),
                os.path.join("lib", "site-packages", "Pythonwin"),
            ]
            self.new_paths = self.new_paths + [
                os.path.join(env_path, x) for x in win_specific_dirs
            ]
        else:
            self.using_win = False

    def __enter__(self):
        """Actually add new paths."""
        sys.path = (
            sys.path[: self.path_insert_loc]
            + self.new_paths
            + sys.path[self.path_insert_loc :]
        )

        # Windows: Fix DLL paths
        if self.using_win:
            self.dll_objs = [os.add_dll_directory(x) for x in self.dll_paths]

        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """Revert path on exit."""
        sys.path = self.org_path

        # Windows: Remove DLL paths
        if self.using_win:
            for dll_obj in self.dll_objs:
                dll_obj.close()
