import argparse
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

def check_pypi(package_name):
    response = requests.get(f"https://pypi.org/pypi/{package_name}/json")
    return response.status_code != 404

def check_npm(package_name):
    response = requests.get(f"https://registry.npmjs.org/{package_name}")
    return response.status_code != 404

def check_rubygems(package_name):
    response = requests.get(f"https://rubygems.org/api/v1/gems/{package_name}.json")
    return response.status_code != 404

def check_maven(package_name):
    response = requests.get(f"https://search.maven.org/solrsearch/select?q={package_name}&rows=1&wt=json")
    return response.json()["response"]["numFound"] > 0

def check_nuget(package_name):
    response = requests.get(f"https://api.nuget.org/v3/registration3/{package_name}/index.json")
    return response.status_code != 404

def check_packagist(package_name):
    response = requests.get(f"https://packagist.org/packages/{package_name}.json")
    return response.status_code != 404

def check_brew(package_name):
    response = requests.get(f"https://formulae.brew.sh/api/formula/{package_name}.json")
    return response.status_code != 404

def check_apt(package_name):
    response = requests.get(f"https://tracker.debian.org/pkg/{package_name}")
    return response.status_code != 404

def check_package_availability(package_name):
    package_managers = {
        "PyPI": check_pypi,
        "npm": check_npm,
        "RubyGems": check_rubygems,
        "Maven": check_maven,
        "NuGet": check_nuget,
        "Packagist": check_packagist,
        "Homebrew": check_brew,
        "APT": check_apt
    }

    results = {}
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(func, package_name): name for name, func in package_managers.items()}
        for future in as_completed(futures):
            manager = futures[future]
            try:
                results[manager] = not future.result()
            except Exception as e:
                print(f"{manager} check failed: {e}")
                results[manager] = None

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check package name availability across major package managers.")
    parser.add_argument("package_name", help="The package name to check.")
    args = parser.parse_args()

    availability = check_package_availability(args.package_name)

    print("Package name availability:")
    for manager, available in availability.items():
        print(f"{manager}: {'Available' if available else 'Taken'}")

