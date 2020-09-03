from typing import Tuple, List, Dict, TypedDict

from license_sh.project_identifier import ProjectType


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
