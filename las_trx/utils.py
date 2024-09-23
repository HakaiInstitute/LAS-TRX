import logging
import sys
from os import path
from typing import TypeVar, List, Mapping, Any, Optional
from las_trx.logger import logger

T = TypeVar("T")


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    base_path = getattr(sys, "_MEIPASS", path.dirname(__file__))
    return path.abspath(path.join(base_path, relative_path))


def _get_available_versions() -> Optional[List[Mapping[str, Any]]]:
    import requests

    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    r = requests.get(
        "https://api.github.com/repos/HakaiInstitute/LAS-TRX/releases", headers=headers
    )
    if r.status_code == requests.codes.ok:
        return list(
            {
                "tag_name": version["tag_name"],
                "html_url": version["html_url"],
                "prerelease": version["prerelease"],
                "draft": version["draft"],
            }
            for version in r.json()
        )
    else:
        return None


def get_upgrade_version(version) -> Optional[Mapping[str, str]]:
    available_versions = _get_available_versions()
    if available_versions is None or len(available_versions) == 0:
        # Error fetching versions, assume no upgrade available
        return None

    # Get all tags that are newer than the current version
    try:
        idx = [v["tag_name"] for v in available_versions].index(version)
    except ValueError:
        # Current version not found in releases, so get latest version of all releases
        idx = len(available_versions)

    # Only recommend stable releases for upgrade
    newer_stable_versions = [
        v for v in available_versions[:idx] if not v["prerelease"] and not v["draft"]
    ]

    if len(newer_stable_versions) == 0:
        return None

    return newer_stable_versions[0]
