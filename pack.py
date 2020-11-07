from pdoc import Doc, Module
from pdoc.cli import recursive_write_files as write


def getPackages(packages: Union[str, List[str]], depth: int = 1, **kwargs) \
        -> Tuple[List[Tuple[str, List[Module]]], List[Module]]:
    """
    Scans directories one level at a time for the presence of packages or modules.

    Args:
        packages (str, list): List of directories to packages or modules.
        depth (int):          Number of levels deep to search.
        kwargs:               Additional keyword arguments for Module()

    Returns:
        Packages: The name of the package and its modules.
        Modules:  The list of modules that do not belong to a package.

    Raises:
        ImportError:         If some of the dependencies of a module or package has not
                             been installed into the current virtual environment.
        ModuleNotFoundError: If no modules or packages exist even after searching through
                             the number of levels in depth.
        FileNotFoundError:   If one of the package directories provided does not exist.
    """

    from os import walk, listdir
    from os.path import abspath, expanduser, join, isdir, split

    def _check_if_module(module: Union[str, Module]) -> bool:
        if isinstance(module, str):
            module = pdoc.import_module(module)
            if '__file__' in dir(module):
                return True
            return False
        else:
            raise ImportError(f"{module} is not a module or package")

    def _check_if_package(directory: str) -> Tuple[List[Module], bool, List[str]]:
        if not isinstance(directory, str):
            raise AssertionError("Directory has to be a string")
        directory = abspath(expanduser(directory))
        SKIP_DIRS = ['venv', 'docs', 'egg-info', 'build', 'dist', 'virtualenv']
        SKIP_PREPEND = ['.', '_']
        if args.ignore:
            SKIP_DIRS += args.ignore
        if args.output_dir:
            SKIP_DIRS.append(args.output_dir)

        packageMods, subDirs = [], []
        if _check_if_module(directory):
            packageMods.append(Module(directory, **kwargs))
        else:
            subDirs = [join(directory, i) for i in next(walk(directory))[1]
                       if not any(j in i for j in SKIP_DIRS) and i[0] not in SKIP_PREPEND]
            for dir_ in subDirs:
                if _check_if_module(dir_):
                    packageMods.append(Module(dir_, **kwargs))
                else:
                    subDirs.append(dir_)
        return packageMods, True if 'setup.py' in listdir(directory) else False, subDirs

    if not isinstance(depth, int):
        print("Search depth is set to 1 level")
        depth = 1

    if not isinstance(packages, list):
        packages = [packages]
    ori_packages = packages
    modules, packs, subdirs, errs = [], [], [], []

    while depth:
        for package in packages:
            if isinstance(package, str) and isdir(abspath(expanduser(package))):
                mods, pack, subd = _check_if_package(package)
                if pack:
                    packs.append((split(package)[1], mods))
                else:
                    modules.extend(mods)
                    subdirs.extend(subd)
            else:
                errs.append(str(package))
        if not (packs or modules or subdirs):
            raise FileNotFoundError(f"The directories {', '.join(errs)} do not exist.")
        depth -= 1
        packages, subdirs, errs = subdirs, [], []
    if not (modules or packs):
        raise ModuleNotFoundError(f"No modules or packages were found in "
                                  f"{' ,'.join(ori_packages)}")
    return packs, modules


def getModules(modules: Union[str, List[str]], depth: int = 1, **kwargs) \
        -> List[Module]:
    """
    Retrieves all the modules from the getPackages() method.
    """
    packages, Modules = getPackages(modules, depth, **kwargs)
    return list((*[module for package in packages for module in package[1]], *Modules))
def _pairwise(iterable):
    """s -> (s0,s1), (s1,s2), (s2, s3), ..."""
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


# class Package(Doc):
#     """
#     Representation of a package's documentation
#     """
#     __pdoc__["Package.name"] = """
#         The name of this package with respect to the context/path in which
#         it was imported from. It is always an absolute import path
#         """
#     __slots__ = {'modules', 'doc'}

#     def __init__(self, package: str, *, docfilter: Callable[[Doc], bool] = None,
#                  context: Context = None, skip_errors: bool = False):
#         """
#         Creates a 'Package' documentation object given the actual
#         packaged Python object.

#         'docfilter' is an optional predicate that controls which
#         sub-objects are documentated (see also: `pdoc.html()`).

#         'context' is an instance of 'pdoc.Context'. If 'None' a
#         global context object will be used.

#         If 'skip_errors' is 'True' and an unimportable, erroneous
#         module or submodule is encountered, a warning will be
#         issued instead of raising an exception.
#         """
#         super().__init__(package, self, )
