from typing import Tuple, List, Dict

from license_sh.project_identifier import ProjectType

LicenseWhitelist = List[str]
LanguageIgnoredPackages = List[str]

IgnoredPackages = Dict[ProjectType, LanguageIgnoredPackages]
ConfigurationType = Tuple[LicenseWhitelist, IgnoredPackages]
