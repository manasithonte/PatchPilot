import os
import tempfile
import re
import requests
from git import Repo
from api.models import DependencyInfo

def clone_repository(repo_url: str, github_token: str = None) -> str:
    temp_dir = tempfile.mkdtemp()
    
    url_to_clone = repo_url
    if github_token:
        url_to_clone = repo_url.replace("https://github.com/", f"https://x-access-token:{github_token}@github.com/")
        if not url_to_clone.endswith(".git"):
            url_to_clone += ".git"
            
    # Set GIT_TERMINAL_PROMPT=0 so git instantly fails instead of hanging indefinitely asking for password
    Repo.clone_from(url_to_clone, temp_dir, env={"GIT_TERMINAL_PROMPT": "0"})
    return temp_dir

def get_latest_pypi_version(package_name: str) -> str:
    try:
        url = f"https://pypi.org/pypi/{package_name}/json"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json().get("info", {}).get("version", None)
    except Exception:
        pass
    return None

def get_latest_npm_version(package_name: str) -> str:
    try:
        url = f"https://registry.npmjs.org/{package_name}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json().get("dist-tags", {}).get("latest", None)
    except Exception:
        pass
    return None

def parse_requirements_txt(file_path: str) -> list[DependencyInfo]:
    deps = []
    # Using utf-8 or errors='ignore' to handle potential BOM like \ufeff
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            # Remove BOM if present
            if line.startswith('\ufeff'):
                line = line[1:]
                
            if not line or line.startswith("#"):
                continue
                
            clean_line = line.split(";")[0].split("#")[0].strip()
            match = re.match(r"^([a-zA-Z0-9_\-\.]+)(?:[\s]*([=><~]+)[\s]*(.*))?$", clean_line)
            if match:
                name = match.group(1).strip()
                operator = match.group(2)
                version = match.group(3)
                
                if operator and version:
                    current_version = version.strip()
                else:
                    current_version = "unknown"
                    
                deps.append(DependencyInfo(
                    name=name,
                    current_version=current_version,
                    file_path=os.path.basename(file_path)
                ))
    return deps

def parse_package_json(file_path: str) -> list[DependencyInfo]:
    import json
    deps = []
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
            deps_dict = data.get("dependencies", {})
            dev_deps_dict = data.get("devDependencies", {})
            
            all_deps = {**deps_dict, **dev_deps_dict}
            for name, version in all_deps.items():
                deps.append(DependencyInfo(
                    name=name,
                    current_version=version,
                    file_path=os.path.basename(file_path)
                ))
    except Exception:
        pass
    return deps

def analyze_repo(repo_url: str, github_token: str = None) -> list[DependencyInfo]:
    repo_dir = clone_repository(repo_url, github_token)
    all_deps = []
    
    # Check for requirements.txt
    req_file = os.path.join(repo_dir, "requirements.txt")
    if os.path.exists(req_file):
        deps = parse_requirements_txt(req_file)
        for dep in deps:
            latest = get_latest_pypi_version(dep.name)
            if latest:
                dep.latest_version = latest
                # Very simplistic "outdated" check
                if dep.current_version == "unknown" or dep.current_version.replace("^","").replace("~","") != latest:
                    dep.is_outdated = True
            all_deps.append(dep)
            
    # Check for package.json
    pkg_file = os.path.join(repo_dir, "package.json")
    if os.path.exists(pkg_file):
        deps = parse_package_json(pkg_file)
        for dep in deps:
            latest = get_latest_npm_version(dep.name)
            if latest:
                dep.latest_version = latest
                clean_current = dep.current_version.replace("^","").replace("~","").replace(">=","").replace("=","")
                if clean_current != latest:
                    dep.is_outdated = True
            all_deps.append(dep)
            
    return all_deps
