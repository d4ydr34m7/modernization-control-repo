#!/usr/bin/env python3
"""
Phase 1 Analysis Script - SELF-HOSTED RUNNER EXECUTION ONLY

This script executes AWS Transform analysis on discovered repositories.
EXECUTION CONTEXT: Intended for self-hosted runner (EC2 / long-lived machine):
  - Self-hosted runner (EC2 or equivalent long-lived machine)
  - Always on, persistent execution environment
  - NOT for ephemeral CI/CD runners
  - Local development (IDE) is for testing only

ARCHITECTURE:
  - Control-plane: GitHub Actions (orchestration, artifact upload)
  - Execution-plane: Self-hosted runner - this script (Transform execution)
  
Execution requires a machine that is:
  - Always on (or automatically started before scheduled runs)
  - Long-running (not subject to CI timeout limits)
  - Not subject to CI payload limits (persistent storage for large outputs)

AWS Transform is intentionally NOT executed in ephemeral CI/CD runners due to:
  - Large, stateful output that requires persistent storage
  - ATX early-access instability in ephemeral runners
  - Long execution times (1-2+ hours) requiring stable execution environment

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
import argparse
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


def check_transform_success(clone_path, log_file_path):
    """
    OUTPUT-AWARE success detection: Check both files and logs.
    
    Determines if Transform analysis succeeded based on:
    - Log file contains "successfully completed with all exit criteria met"
    - Multiple output folders exist (at least 2, including Documentation)
    
    Returns: (is_success, confidence, details_dict)
    """
    results = {
        'outputs_found': [],
        'outputs_missing': [],
        'log_success_message': False,
        'log_validation_status': False
    }
    
    # Required output folders for Transform analysis
    required_outputs = [
        ("Documentation", "Documentation"),
        (".aws", ".aws"),
        (".atx", ".atx"),
        ("transform_output", "transform_output"),
        ("analysis_output", "analysis_output")
    ]
    
    # Check for output folders
    if clone_path.exists():
        for name, folder_name in required_outputs:
            full_path = clone_path / folder_name
            if full_path.exists():
                results['outputs_found'].append(name)
            else:
                results['outputs_missing'].append(name)
    
    # Check log file for success indicators
    if log_file_path.exists():
        try:
            with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                log_content = f.read()
            
            # Strong success indicators from Transform logs
            success_phrases = [
                'successfully completed with all exit criteria met',
                'comprehensive codebase analysis transformation has been successfully completed',
                'successfully completed',
                'all exit criteria met'
            ]
            
            # Check if the definitive success message exists
            log_lower = log_content.lower()
            for phrase in success_phrases:
                if phrase in log_lower:
                    results['log_success_message'] = True
                    break
            
            # Also check for validation status
            if 'validation status' in log_lower and 'approved' in log_lower:
                results['log_validation_status'] = True
                
        except Exception:
            pass
    
    # Determine success criteria
    output_count = len(results['outputs_found'])
    has_docs = "Documentation" in results['outputs_found']
    has_log_success = results['log_success_message']
    has_validation = results['log_validation_status']
    
    # Success if:
    # 1. Log explicitly says "successfully completed with all exit criteria met" (PRIMARY)
    # 2. OR at least 2 output folders exist (including Documentation) (SECONDARY)
    is_success = has_log_success or (output_count >= 2 and has_docs)
    
    # Confidence level
    if has_log_success and output_count >= 2:
        confidence = "high"
    elif has_log_success or (output_count >= 2 and has_docs):
        confidence = "medium"
    else:
        confidence = "low"
    
    return is_success, confidence, results


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
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Run Phase 1 analysis on repositories')
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force re-analysis of repositories already marked as analyzed'
    )
    args = parser.parse_args()
    
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
    discovered_repos = discover_repos()
    
    # Filter repos based on registry status (idempotent by default)
    repos_to_analyze = []
    skipped_repos = []
    
    for repo in discovered_repos:
        repo_name = repo["name"]
        
        # Check if repo exists in registry
        existing_entry = None
        for reg_repo in registry_data.get("repos", []):
            if reg_repo.get("repo_name") == repo_name:
                existing_entry = reg_repo
                break
        
        # Skip repos already analyzed (unless --force)
        if existing_entry and existing_entry.get("analysis_status") == "analyzed":
            if args.force:
                # Force re-analysis: allow analyzed → pending
                repos_to_analyze.append(repo)
                print(f"Force re-analysis enabled for {repo_name} (previously analyzed)")
            else:
                skipped_repos.append(repo_name)
                print(f"Skipping {repo_name} (already analyzed). Use --force to re-analyze.")
        else:
            # New repo or repo with other status (pending, running, failed) - include it
            repos_to_analyze.append(repo)
    
    print(f"\nFound {len(discovered_repos)} repository(ies) to check")
    print(f"  - {len(repos_to_analyze)} repository(ies) to analyze")
    if skipped_repos:
        print(f"  - {len(skipped_repos)} repository(ies) skipped (already analyzed)")
    
    if not repos_to_analyze:
        print("\nNo repositories to analyze. All discovered repos are already analyzed.")
        return
    
    # Mark repos to analyze as pending (only new repos or repos with --force)
    for repo in repos_to_analyze:
        registry_data = update_registry_entry(
            registry_data, 
            repo["name"], 
            repo["git_url"], 
            "pending"
        )
    save_registry(registry_path, registry_data)
    
    repos = repos_to_analyze
    
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
            transform_succeeded = True
            
        except subprocess.CalledProcessError:
            # Transform process exited with error - but may have generated output
            # Check for outputs before marking as failed (output-aware, not exit-code-only)
            transform_succeeded = False
            print(f"\nTransform process exited with error. Checking for generated output...", file=sys.stderr)
        except Exception as e:
            # Unexpected error - check for outputs anyway
            transform_succeeded = False
            print(f"\nUnexpected error during Transform execution: {e}. Checking for generated output...", file=sys.stderr)
            
        finally:
            # OUTPUT-AWARE: Check for success using multiple indicators (logs + files)
            # This runs regardless of process exit code - always check for outputs
            is_success, confidence, success_details = check_transform_success(clone_path, log_file_path)
            
            # Copy ALL Transform-generated output before cleanup (always run, even on errors)
            transform_output_folders = [
                ".aws",
                "Documentation",
                ".atx",
                "transform_output",
                "analysis_output"
            ]
            
            copied_count = 0
            if clone_path.exists():
                print(f"\nCopying Transform-generated output...")
                for item in clone_path.iterdir():
                    if item.name == ".git":
                        continue
                    
                    if item.name in transform_output_folders or item.name.startswith(".aws"):
                        dest_item = analysis_output_dir / item.name
                        try:
                            if item.is_dir():
                                shutil.copytree(item, dest_item, dirs_exist_ok=True)
                            else:
                                shutil.copy2(item, dest_item)
                            copied_count += 1
                            print(f"Copied {item.name}/")
                        except Exception as e:
                            print(f"Warning: Could not copy {item.name}: {e}", file=sys.stderr)
                
                if copied_count == 0:
                    print(f"Warning: No Transform output folders found.")
            
            # Determine final status based on outputs + logs, NOT just exit code
            if is_success:
                # Analysis succeeded (determined by outputs/logs, even if process errored)
                output_list = ', '.join(success_details['outputs_found']) if success_details['outputs_found'] else 'none'
                notes_parts = [f"Analysis completed (confidence: {confidence}). Outputs: {output_list}"]
                
                if success_details['log_success_message']:
                    notes_parts.append("Log confirms successful completion")
                if not transform_succeeded:
                    notes_parts.append("Process exit code indicated error, but outputs confirm success")
                
                registry_data = update_registry_entry(
                    registry_data,
                    repo_name,
                    repo_url,
                    "analyzed",
                    language="unknown",
                    notes=" | ".join(notes_parts)
                )
                save_registry(registry_path, registry_data)
                print(f"\n✅ Analysis succeeded: Outputs validated (exit code ignored due to successful completion)")
            elif transform_succeeded:
                # Process succeeded but outputs don't meet success criteria
                registry_data = update_registry_entry(
                    registry_data,
                    repo_name,
                    repo_url,
                    "analyzed",
                    language="unknown",
                    notes=f"Process completed but limited outputs found. Outputs: {', '.join(success_details['outputs_found']) or 'none'}"
                )
                save_registry(registry_path, registry_data)
                print(f"\n⚠️  Analysis completed with limited outputs")
            else:
                # Real failure: no outputs and process failed
                missing_outputs = ', '.join(success_details['outputs_missing']) if success_details['outputs_missing'] else 'all'
                registry_data = update_registry_entry(
                    registry_data,
                    repo_name,
                    repo_url,
                    "failed",
                    language="unknown",
                    notes=f"Transform execution failed. Missing outputs: {missing_outputs}. Check {repos_dir.name}/{repo_name}_transform.log"
                )
                save_registry(registry_path, registry_data)
                print(f"\n❌ Error: Failed to process {repo_name}. Check {repos_dir.name}/{repo_name}_transform.log", file=sys.stderr)
            
            # Delete the cloned repository after copying (always run cleanup)
            if clone_path.exists():
                print(f"\nDeleting cloned repository at {clone_path}")
                try:
                    shutil.rmtree(clone_path)
                    print(f"Cleanup complete")
                except (PermissionError, OSError) as e:
                    print(f"Warning: Could not fully delete {clone_path}: {e}", file=sys.stderr)
                    print(f"Cleanup partial - some files may remain")
            
            # Exit with error only if truly failed (no outputs, no log success)
            if not is_success and not transform_succeeded:
                sys.exit(1)
    
    print(f"\n{'='*60}")
    print(f"Phase 1 analysis complete for {len(repos)} repository(ies)")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
