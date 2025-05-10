#!/usr/bin/env python3
import os
import re
from git import Repo
import sys

def get_commit_messages_since_last_tag():
    repo = Repo(".")
    
    # Find the most recent tag
    tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)
    
    if not tags:
        # If no tags, get all commits
        commits = list(repo.iter_commits())
    else:
        last_tag = tags[-1]
        commits = list(repo.iter_commits(f"{last_tag.name}..HEAD"))
    
    # Extract commit messages
    commit_messages = [commit.message for commit in commits]
    return commit_messages

def determine_bump_type(commit_messages):
    bump_type = "patch"  # Default to patch
    
    # Conventional commits patterns
    breaking_pattern = re.compile(r"BREAKING CHANGE:|!:")
    feat_pattern = re.compile(r"^feat(\([^)]*\))?:")
    fix_pattern = re.compile(r"^fix(\([^)]*\))?:")
    
    for message in commit_messages:
        # Check for breaking changes first (major)
        if breaking_pattern.search(message):
            return "major"
        
        # Check for new features (minor)
        if feat_pattern.match(message) and bump_type == "patch":
            bump_type = "minor"
        
        # Fixes are patch level, which is the default
    
    return bump_type

if __name__ == "__main__":
    commit_messages = get_commit_messages_since_last_tag()
    
    if not commit_messages:
        print("No new commits since last tag, defaulting to patch")
        bump_type = "patch"
    else:
        bump_type = determine_bump_type(commit_messages)
    
    # Output the bump type for GitHub Actions
    print(f"Determined bump type: {bump_type}")
    with open(os.environ["GITHUB_ENV"], "a") as env_file:
        env_file.write(f"BUMP_TYPE={bump_type}\n") 