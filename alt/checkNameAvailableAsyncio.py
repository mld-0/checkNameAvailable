import argparse
import asyncio
import aiohttp

async def check_pypi(package_name):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://pypi.org/pypi/{package_name}/json") as response:
            return response.status != 404

async def check_npm(package_name):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://registry.npmjs.org/{package_name}") as response:
            return response.status != 404

async def check_rubygems(package_name):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://rubygems.org/api/v1/gems/{package_name}.json") as response:
            return response.status != 404

async def check_maven(package_name):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://search.maven.org/solrsearch/select?q={package_name}&rows=1&wt=json") as response:
            json_response = await response.json()
            return json_response["response"]["numFound"] > 0

async def check_nuget(package_name):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.nuget.org/v3/registration3/{package_name}/index.json") as response:
            return response.status != 404

async def check_packagist(package_name):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://packagist.org/packages/{package_name}.json") as response:
            return response.status != 404

async def check_brew(package_name):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://formulae.brew.sh/api/formula/{package_name}.json") as response:
            return response.status != 404

async def check_apt(package_name):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://tracker.debian.org/pkg/{package_name}") as response:
            return response.status != 404

async def check_package_availability(package_name):
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

    tasks = [manager_func(package_name) for manager_func in package_managers.values()]
    results = await asyncio.gather(*tasks)

    return {manager: not result for manager, result in zip(package_managers.keys(), results)}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check package name availability across major package managers.")
    parser.add_argument("package_name", help="The package name to check.")
    args = parser.parse_args()

    availability = asyncio.run(check_package_availability(args.package_name))

    print("Package name availability:")
    for manager, available in availability.items():
        print(f"{manager}: {'Available' if available else 'Taken'}")
