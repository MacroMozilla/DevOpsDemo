import os
import requests


class DockerHubManager:
    """A simple wrapper for the Docker Hub REST API."""

    def __init__(self, username: str | None = None, token: str | None = None):
        self.username = username or os.getenv("DOCKERHUB_USERNAME")
        self.token = token or os.getenv("DOCKERHUB_TOKEN")
        self.jwt = None
        self.base_url = "https://hub.docker.com/v2"
        if not self.username:
            raise ValueError("❌ DockerHub username is required.")

    # ----------------------------------------
    # Repository operations
    # ----------------------------------------
    def get_repos(self, page_size: int = 100):
        """Return a list of all repositories under the user."""
        url = f"{self.base_url}/repositories/{self.username}/?page_size={page_size}"
        headers = self._headers()
        repos = []
        print(f"📦 Fetching repositories for {self.username}...")

        while url:
            res = requests.get(url, headers=headers)
            if res.status_code != 200:
                raise RuntimeError(f"❌ Failed to fetch repositories: {res.text}")
            data = res.json()
            repos.extend([r["name"] for r in data.get("results", [])])
            url = data.get("next")
        print(f"✅ Found {len(repos)} repositories.")
        return repos

    def get_tags_by_repo(self, repo_name: str, page_size: int = 100):
        """Return a list of tags (versions) for the given repository."""
        url = f"{self.base_url}/repositories/{self.username}/{repo_name}/tags?page_size={page_size}"
        headers = self._headers()
        tags = []
        print(f"🏷️ Fetching tags for repository: {repo_name}")

        while url:
            res = requests.get(url, headers=headers)
            if res.status_code != 200:
                raise RuntimeError(f"❌ Failed to fetch tags for {repo_name}: {res.text}")
            data = res.json()
            tags.extend([t["name"] for t in data.get("results", [])])
            url = data.get("next")
        print(f"✅ Found {len(tags)} tags in {repo_name}.")
        return tags

    # ----------------------------------------
    # Helper
    # ----------------------------------------
    def _headers(self):
        headers = {}
        if self.jwt:
            headers["Authorization"] = f"JWT {self.jwt}"
        return headers


if __name__ == "__main__":

    manager = DockerHubManager()
    repos = manager.get_repos()
    for repo in repos:
        tags = manager.get_tags_by_repo(repo)
        print(f"{repo}: {tags}")
