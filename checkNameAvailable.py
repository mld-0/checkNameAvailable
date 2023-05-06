import sys
import logging
import argparse
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

def check_pypi(package_name):
    try:
        response = requests.get(f"https://pypi.org/pypi/{package_name}/json")
        return response.status_code != 404
    except Exception as e:
        return f"failed e=({e})"

def check_npm(package_name):
    try:
        response = requests.get(f"https://registry.npmjs.org/{package_name}")
        return response.status_code != 404
    except Exception as e:
        return f"failed e=({e})"

def check_rubygems(package_name):
    try:
        response = requests.get(f"https://rubygems.org/api/v1/gems/{package_name}.json")
        return response.status_code != 404
    except Exception as e:
        return f"failed e=({e})"

def check_maven(package_name):
    try:
        response = requests.get(f"https://search.maven.org/solrsearch/select?q={package_name}&rows=1&wt=json")
        return response.json()["response"]["numFound"] > 0
    except Exception as e:
        return f"failed e=({e})"

def check_nuget(package_name):
    try:
        response = requests.get(f"https://api.nuget.org/v3/registration3/{package_name}/index.json")
        return response.status_code != 404
    except Exception as e:
        return f"failed e=({e})"

def check_brew(package_name):
    try:
        response = requests.get(f"https://formulae.brew.sh/api/formula/{package_name}.json")
        return response.status_code != 404
    except Exception as e:
        return f"failed e=({e})"

def check_apt(package_name):
    try:
        response = requests.get(f"https://tracker.debian.org/pkg/{package_name}")
        return response.status_code != 404
    except Exception as e:
        return f"failed e=({e})"

def check_package_availability(package_name):

    def categorize_result(result):
        if type(result) is bool:
            return "Available" if not result else "Taken"
        else:
            return result

    package_managers = {
        "PyPI": check_pypi,
        "npm": check_npm,
        "RubyGems": check_rubygems,
        "Maven": check_maven,
        "NuGet": check_nuget,
        "Homebrew": check_brew,
        "APT": check_apt
    }

    results = {}
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(func, package_name): name for name, func in package_managers.items()}
        for future in as_completed(futures):
            manager = futures[future]
            try:
                results[manager] = categorize_result(future.result())
            except Exception as e:
                print(f"{manager} check failed: {e}")
                results[manager] = None

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check name availability across major package managers")
    parser.add_argument("package_name", help="The package name to check")
    args = parser.parse_args()

    availability = check_package_availability(args.package_name)

    print("Availability:")
    for manager, available in availability.items():
        print("    %-20s %s" % (manager + ':', available))

