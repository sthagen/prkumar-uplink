# Standard library imports
from pprint import pformat

# Local imports
import github

BASE_URL = "https://api.github.com/"


if __name__ == "__main__":
    # Create a GitHub API client
    gh = github.GitHub(base_url=BASE_URL)

    # Get all public repositories
    repos = gh.get_repos()

    # Shorten to first 10 results to avoid hitting the rate limit.
    repos = repos[:10]

    # Print contributors for those repositories
    for repo in repos:
        contributors = gh.get_contributors(repo.owner, repo.name)
        print(f"Contributors for {repo}:\n{pformat(contributors, indent=4)}\n")
