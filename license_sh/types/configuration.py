from typing import Tuple, List, Dict

from license_sh.project_identifier import ProjectType

LicenseWhitelist = List[str]
LanguageIgnoredPackages = List[str]
LanguageOverridenPackages = Dict[str, Tuple[str, str]]

IgnoredPackages = Dict[ProjectType, LanguageIgnoredPackages]
OverridenPackages = Dict[ProjectType, LanguageOverridenPackages]
ConfigurationType = Tuple[LicenseWhitelist, IgnoredPackages, OverridenPackages]
