import yaml
import fnmatch
import os
from pathlib import Path
from dotenv import load_dotenv
from github import Github, Auth
from github.GithubException import GithubException

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

def discover_repos():
    with open("config/repos.yaml") as f:
        cfg = yaml.safe_load(f)

    mode = cfg["mode"]

    if mode == "single":
        repo = cfg["single"]
        return [{
            "name": repo["name"],
            "git_url": repo["git_url"]
        }]

    if mode == "org_scan":
        org_config = cfg["org_scan"]
        org_name = org_config["github_org"]
        filters = org_config.get("filters", {})
        limits = org_config.get("limits", {})
        
        # Get GitHub token from environment variable (can be set via .env file or environment)
        github_token = os.environ.get("GITHUB_TOKEN")
        if not github_token:
            raise ValueError("GITHUB_TOKEN is required for org_scan mode. Set it in .env file or as environment variable.")
        
        # Initialize GitHub API client
        auth = Auth.Token(github_token)
        g = Github(auth=auth)
        
        repos = []
        max_repos = limits.get("max_repos_per_run")
        
        # Try to get repos from organization or user
        try:
            org = g.get_organization(org_name)
            repo_source = org.get_repos()
        except GithubException as e:
            # If organization not found, try as a user
            if e.status == 404:
                try:
                    user = g.get_user(org_name)
                    repo_source = user.get_repos()
                except GithubException as user_e:
                    raise ValueError(f"Failed to access organization/user '{org_name}': {user_e.data.get('message', str(user_e))}")
            else:
                raise ValueError(f"Failed to access organization '{org_name}': {e.data.get('message', str(e))}")
        
        # Get all repositories from the organization/user
        for repo in repo_source:
            # Apply filters
            if filters.get("exclude_archived") and repo.archived:
                continue
            
            if filters.get("exclude_forks") and repo.fork:
                continue
            
            # Filter by language
            target_language = filters.get("language", "")
            if target_language:
                repo_languages = repo.get_languages()
                # GitHub API returns languages as a dict like {"Java": bytes, "Python": bytes}
                # Check if target language (case-insensitive) exists in repo languages
                repo_lang_names = [lang.lower() for lang in repo_languages.keys()]
                if target_language.lower() not in repo_lang_names:
                    continue
            
            repos.append({
                "name": repo.name,
                "git_url": repo.clone_url
            })
            
            # Apply max repos limit
            if max_repos and len(repos) >= max_repos:
                break
        
        return repos

    raise ValueError(f"Unknown mode: {mode}")


if __name__ == "__main__":
    repos = discover_repos()
    for r in repos:
        print(f"Discovered repo: {r['name']} → {r['git_url']}")
