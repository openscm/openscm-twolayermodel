# find the requirements in setup.py, there must be a better way to do this...
with open("setup.py") as fh:
    for line in fh.readlines():
        line = line.strip()
        if line.startswith("REQUIREMENTS ="):
            if "[" in line and "]" in line:
                exec(line)
            else:
                raise NotImplementedError("multi-line requirements")


# find the requirements in the README
requirements_readme = []
with open("README.rst") as fh:
    in_requirements = False
    for line in fh.readlines():
        line = line.strip()
        if line == ".. begin-dependencies":
            in_requirements = True
        elif line == ".. end-dependencies":
            in_requirements = False
        elif in_requirements and line:
            requirements_readme.append(line.strip("-").strip())

requirements_set = set(REQUIREMENTS)
requirements_readme_set = set(requirements_readme)

assert requirements_set == requirements_readme_set, (
    "Requirements: {}\n"
    "Requirements in README: {}\n"
    "Requirements - Requirements in README: {}\n"
    "Requirements in README - Requirements: {}".format(
        requirements_set,
        requirements_readme_set,
        requirements_set - requirements_readme_set,
        requirements_readme_set - requirements_set,
    )
)
