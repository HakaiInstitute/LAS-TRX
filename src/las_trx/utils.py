import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import requests
from loguru import logger

from las_trx.constants import NetworkConstants


def resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and for PyInstaller.

    Args:
        relative_path: Path relative to the application root

    Returns:
        Absolute path to the resource
    """
    base_path = getattr(sys, "_MEIPASS", Path(__file__).parent)
    return str((Path(base_path) / relative_path).resolve())


def _get_available_versions() -> list[Mapping[str, Any]] | None:
    """Fetch available versions from GitHub API.

    Returns:
        List of version information dictionaries, or None if request fails
    """
    try:
        response = requests.get(
            "https://api.github.com/repos/HakaiInstitute/LAS-TRX/releases",
            headers=NetworkConstants.GITHUB_API_HEADERS,
            timeout=NetworkConstants.GITHUB_API_TIMEOUT,
        )

        if response.status_code == requests.codes.ok:
            releases = response.json()
            return [
                {
                    "tag_name": version["tag_name"],
                    "html_url": version["html_url"],
                    "prerelease": version["prerelease"],
                    "draft": version["draft"],
                }
                for version in releases
            ]
        else:
            logger.warning(f"GitHub API request failed with status {response.status_code}")
            return None

    except requests.RequestException as e:
        logger.warning(f"Failed to fetch version information: {e}")
        return None


def get_upgrade_version(current_version: str) -> Mapping[str, str] | None:
    """Check for available software upgrades.

    Args:
        current_version: Current version string to compare against

    Returns:
        Dictionary with upgrade information, or None if no upgrade available
    """
    available_versions = _get_available_versions()
    if not available_versions:
        logger.debug("No version information available")
        return None

    # Find current version index in releases
    try:
        current_idx = [v["tag_name"] for v in available_versions].index(current_version)
    except ValueError:
        # Current version not found in releases, recommend latest stable
        logger.debug(f"Current version {current_version} not found in releases")
        current_idx = len(available_versions)

    # Only recommend stable releases for upgrade (versions before current in list are newer)
    newer_stable_versions = [v for v in available_versions[:current_idx] if not v["prerelease"] and not v["draft"]]

    if not newer_stable_versions:
        logger.debug("No newer stable versions available")
        return None

    latest_upgrade = newer_stable_versions[0]
    logger.info(f"Upgrade available: {latest_upgrade['tag_name']}")
    return latest_upgrade
