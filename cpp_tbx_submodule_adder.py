import os
import requests
import argparse
from subprocess import run, PIPE

# Function to get public repositories from the cpp-toolbox organization
def get_public_repos():
    print("Fetching public repositories from the cpp-toolbox organization...")
    url = "https://api.github.com/orgs/cpp-toolbox/repos"
    headers = {
        "Accept": "application/vnd.github.v3+json",
    }
    repos = []
    page = 1
    while True:
        response = requests.get(url, headers=headers, params={"page": page, "per_page": 100})
        if response.status_code != 200:
            print(f"Failed to retrieve repositories: {response.status_code}")
            break
        data = response.json()
        if not data:
            break
        repos.extend(data)
        page += 1
    return repos


# Function to display the structure of the src directory
def display_src_structure(src_path):
    for root, dirs, files in os.walk(src_path):
        level = root.replace(src_path, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 4 * (level + 1)
        # for f in files:
        #     print(f"{subindent}{f}")


# Function to add a submodule
def add_submodule(repo_url, submodule_path, src_path):
    try:
        # Create the submodule directory if it does not exist
        full_submodule_path = os.path.join(src_path, submodule_path)
        os.makedirs(full_submodule_path, exist_ok=True)

        # Change to the submodule directory
        current_dir = os.getcwd()
        os.chdir(full_submodule_path)

        # Add the submodule to the current directory
        result = run(["git", "submodule", "add", repo_url], stdout=PIPE, stderr=PIPE)
        os.chdir(current_dir)  # Change back to the original directory

        if result.returncode == 0:
            print(f"Submodule added in {full_submodule_path}")
        else:
            print(f"Failed to add submodule. Error: {result.stderr.decode()}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Main interactive function
def main():
    parser = argparse.ArgumentParser(description="Manage Git submodules from the cpp-toolbox organization.")
    parser.add_argument('src', type=str, help='The src directory where submodules will be added.')

    args = parser.parse_args()
    src_path = args.src

    if not os.path.exists(src_path):
        print(f"The specified src directory '{src_path}' does not exist.")
        return

    repos = get_public_repos()

    while True:
        command = input("Enter 'list' to list repositories, 'add' to search and add repositories, or 'exit' to quit: ").strip().lower()
        if command == 'exit':
            break
        elif command == 'list':
            print("Public repositories in the cpp-toolbox organization:")
            for repo in repos:
                print(repo['name'])
        elif command == 'add':
            search_keyword = input("Enter a keyword to search for repositories: ").strip()
            matching_repos = [repo for repo in repos if search_keyword.lower() in repo['name'].lower()]
            if not matching_repos:
                print("No matching repositories found.")
                continue

            print("Matching repositories:")
            for i, repo in enumerate(matching_repos):
                print(f"{i + 1}: {repo['name']} - {repo['ssh_url']}")

            choice = input("Enter the number of the repository to add as a submodule, or 'n' to search again: ").strip()
            if choice.lower() == 'n':
                continue

            try:
                repo_index = int(choice) - 1
                if repo_index < 0 or repo_index >= len(matching_repos):
                    print("Invalid choice.")
                    continue

                repo_to_add = matching_repos[repo_index]
                print("Current src directory structure:")
                display_src_structure(src_path)

                submodule_path = input(f"Enter the path to add the submodule (relative to {src_path}/): ").strip()

                add_submodule(repo_to_add['ssh_url'], submodule_path, src_path)

            except ValueError:
                print("Invalid input. Please enter a valid number.")
        else:
            print("Invalid command. Please enter 'list', 'add', or 'exit'.")

if __name__ == "__main__":
    main()
