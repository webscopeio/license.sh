from typing import Tuple, List, Dict
import sys

from license_sh.project_identifier import ProjectType

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


class PackageOverride(TypedDict):
    license: str
    licenseText: str
    reason: str


LanguageOverrides = Dict[str, PackageOverride]
LicenseOverrides = Dict[ProjectType, LanguageOverrides]
LicenseWhitelist = List[str]
LanguageIgnoredPackages = List[str]

IgnoredPackages = Dict[ProjectType, LanguageIgnoredPackages]
ConfigurationType = Tuple[LicenseWhitelist, IgnoredPackages, LicenseOverrides]
