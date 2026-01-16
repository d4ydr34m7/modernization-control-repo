#!/usr/bin/env python3
"""
Phase 1 Analysis Script - STABLE-RUNNER EXECUTION ONLY

This script executes AWS Transform analysis on discovered repositories.
EXECUTION CONTEXT: Intended for stable, long-running environments:
  - Local development (IDE)
  - GitHub Codespaces
  - EC2 instances
  - NOT for ephemeral CI/CD runners

ARCHITECTURE:
  - Control-plane: GitHub Actions (orchestration, artifact upload)
  - Execution-plane: This script (Transform execution on stable runners)
  
AWS Transform is intentionally NOT executed in CI due to:
  - Large, stateful output that requires persistent storage
  - ATX early-access instability in ephemeral runners
  - Long execution times (1-2+ hours) requiring human oversight

STATUS TRACKING:
  - pending: Repository discovered, not started
  - running: Transform execution started
  - analyzed: Transform completed successfully
  - failed: Transform execution failed
"""

import subprocess
import shutil
import sys
import yaml
from datetime import datetime
from pathlib import Path

# Add scripts directory to path to import discover_repos
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))
from discover_repos import discover_repos


def load_registry(registry_path):
    """Load the analysis registry from YAML file."""
    if registry_path.exists():
        with open(registry_path, 'r') as f:
            data = yaml.safe_load(f)
            return data if data else {"repos": []}
    return {"repos": []}


def save_registry(registry_path, registry_data):
    """Save the analysis registry to YAML file."""
    with open(registry_path, 'w') as f:
        yaml.dump(registry_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)


def update_registry_entry(registry_data, repo_name, git_url, status, language="unknown", notes=None):
    """
    Update or create an entry in the registry.
    
    Valid statuses: pending, running, analyzed, failed
    """
    repos = registry_data.setdefault("repos", [])
    
    # Find existing entry
    entry = None
    for repo in repos:
        if repo.get("repo_name") == repo_name:
            entry = repo
            break
    
    # Create new entry if not found
    if entry is None:
        entry = {
            "repo_name": repo_name,
            "git_url": git_url,
            "language": language,
            "analysis_status": status,
            "analysis_date": datetime.now().isoformat(),
        }
        if notes:
            entry["notes"] = notes
        repos.append(entry)
    else:
        # Update existing entry
        entry["analysis_status"] = status
        entry["analysis_date"] = datetime.now().isoformat()
        if language != "unknown":
            entry["language"] = language
        if notes:
            entry["notes"] = notes
        elif "notes" in entry and status == "analyzed":
            # Clear notes when successfully analyzed
            entry.pop("notes", None)
    
    return registry_data


def main():
    # Get the project root directory (parent of scripts/)
    project_root = Path(__file__).parent.parent
    
    # Create necessary directories
    tmp_dir = project_root / "tmp"
    repos_dir = project_root / "repos"
    tmp_dir.mkdir(exist_ok=True)
    repos_dir.mkdir(exist_ok=True)
    
    # Registry file path
    registry_path = repos_dir / "analysis_registry.yaml"
    
    # Load existing registry
    registry_data = load_registry(registry_path)
    
    # Discover repositories to analyze
    repos = discover_repos()
    print(f"Found {len(repos)} repository(ies) to analyze")
    
    # Mark all discovered repos as pending initially
    for repo in repos:
        registry_data = update_registry_entry(
            registry_data, 
            repo["name"], 
            repo["git_url"], 
            "pending"
        )
    save_registry(registry_path, registry_data)
    
    # Process each repository
    for repo in repos:
        repo_name = repo["name"]
        repo_url = repo["git_url"]
        
        print(f"\n{'='*60}")
        print(f"Processing repository: {repo_name}")
        print(f"{'='*60}")
        
        # Clone location in tmp directory
        clone_path = tmp_dir / repo_name
        
        # Output location for analysis results
        analysis_output_dir = repos_dir / repo_name / "analysis"
        analysis_output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Clean up any existing clone directory from previous runs
            if clone_path.exists():
                # Use shutil.rmtree which handles permission issues better than rm -rf
                try:
                    shutil.rmtree(clone_path)
                except PermissionError:
                    # If permission denied, try with chmod first
                    import stat
                    import os
                    for root, dirs, files in os.walk(clone_path):
                        for d in dirs:
                            os.chmod(os.path.join(root, d), stat.S_IRWXU)
                        for f in files:
                            os.chmod(os.path.join(root, f), stat.S_IRWXU)
                    shutil.rmtree(clone_path)
            
            # Clone the repository
            print(f"\nCloning {repo_url} to {clone_path}")
            subprocess.run(
                ["git", "clone", repo_url, str(clone_path)],
                check=True,
                capture_output=True,
                text=True
            )
            print(f"Repository cloned successfully")
            
            # Mark repository as running before Transform execution
            registry_data = update_registry_entry(
                registry_data,
                repo_name,
                repo_url,
                "running",
                language="unknown"
            )
            save_registry(registry_path, registry_data)
            
            # Run Transform analysis in non-interactive mode
            # EXECUTION-PLANE: This is the heavy Transform execution (stable-runner only)
            transformation_name = "AWS/early-access-comprehensive-codebase-analysis"
            print(f"\nRunning Transform analysis on {repo_name}")
            print(f"Using transformation: {transformation_name}")
            
            # Define log file path for Transform output
            log_file_path = repos_dir / f"{repo_name}_transform.log"
            print(f"Streaming output to {log_file_path.name}...")
            
            # Stream output directly to disk (bypasses shell pipe buffer)
            with open(log_file_path, "w") as log_file:
                subprocess.run(
                    [
                        "atx", "custom", "def", "exec",
                        "-n", transformation_name,
                        "-p", str(clone_path),
                        "-x",  # Non-interactive mode
                        "-t"   # Trust all tools
                    ],
                    check=True,
                    cwd=str(clone_path),
                    stdout=log_file,          # Direct stream to disk (no RAM buffer)
                    stderr=subprocess.STDOUT  # Merge errors into same file
                )
            
            print(f"Transform analysis completed. Logs saved to {log_file_path.name}")
            
            # Copy analysis output from cloned repo to analysis directory
            print(f"\nCopying Transform-generated output...")
            
            # Transform-generated folders to copy
            transform_output_folders = [
                ".aws",
                "Documentation",
                ".atx",
                "transform_output",
                "analysis_output"
            ]
            
            if clone_path.exists():
                copied_count = 0
                for item in clone_path.iterdir():
                    if item.name == ".git":
                        continue
                    
                    if item.name in transform_output_folders or item.name.startswith(".aws"):
                        dest_item = analysis_output_dir / item.name
                        if item.is_dir():
                            shutil.copytree(item, dest_item, dirs_exist_ok=True)
                        else:
                            shutil.copy2(item, dest_item)
                        copied_count += 1
                        print(f"Copied {item.name}/")
                
                if copied_count == 0:
                    print(f"Warning: No standard output folders found. Check the log file.")
            
            # Update registry: mark as analyzed (successful completion)
            registry_data = update_registry_entry(
                registry_data,
                repo_name,
                repo_url,
                "analyzed",
                language="unknown"
            )
            save_registry(registry_path, registry_data)
            
        except subprocess.CalledProcessError:
            # Transform execution failed - mark as failed and keep logs
            registry_data = update_registry_entry(
                registry_data,
                repo_name,
                repo_url,
                "failed",
                language="unknown",
                notes=f"Transform execution failed. Check {repos_dir.name}/{repo_name}_transform.log"
            )
            save_registry(registry_path, registry_data)
            # Note: Error details are already in the log file (stderr merged with stdout)
            print(f"\nError: Failed to process {repo_name}. Check {repos_dir.name}/{repo_name}_transform.log", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            # Unexpected error - mark as failed
            registry_data = update_registry_entry(
                registry_data,
                repo_name,
                repo_url,
                "failed",
                language="unknown",
                notes=f"Unexpected error: {str(e)}"
            )
            save_registry(registry_path, registry_data)
            print(f"\nError: Unexpected error processing {repo_name}: {e}", file=sys.stderr)
            sys.exit(1)
            
        finally:
            # Delete the cloned repository after copying
            if clone_path.exists():
                print(f"\nDeleting cloned repository at {clone_path}")
                try:
                    # Use shutil.rmtree which handles permission issues better
                    shutil.rmtree(clone_path)
                    print(f"Cleanup complete")
                except (PermissionError, OSError) as e:
                    # If cleanup fails, log warning but don't fail the script
                    print(f"Warning: Could not fully delete {clone_path}: {e}", file=sys.stderr)
                    print(f"Cleanup partial - some files may remain")
    
    print(f"\n{'='*60}")
    print(f"Phase 1 analysis complete for {len(repos)} repository(ies)")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
