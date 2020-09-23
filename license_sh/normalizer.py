import json
from importlib import resources
from typing import Tuple

import license_sh.data as license_data

valid_license_ids = {}
with resources.path(license_data, "licenses.json") as licenses_path:
    with open(licenses_path) as json_file:
        data = json.load(json_file)
        for license in data["licenses"]:
            license["licenseIdUppercase"] = license["licenseId"].upper()

        # Let's create a mapping where upper case licenses will map
        # to the original SPDX licenses
        valid_license_ids = {
            license["licenseIdUppercase"]: license["licenseId"]
            for license in data["licenses"]
        }

        licenses_by_names = {
            license["name"]: license["licenseId"] for license in data["licenses"]
        }


def is_spdx_compliant(license: str) -> bool:
    return license in valid_license_ids.values()


def normalize(license: str) -> Tuple[str, bool]:
    """
    Normalizes the license
    :param license:
    :return: (normalized license, was_normalised, was_spdx_compliant) where
    normalized_license - normalized license name
    was_normalized - returns whether an actual name was changed
    """

    license_upper = license.upper()

    # we check whether our license is in SPDX list
    if is_spdx_compliant(license):
        return valid_license_ids[license_upper], False

    # if it's there, but the uppercase/lowercase is the problem, we normalize it
    # but return a normalized flag
    if license_upper in valid_license_ids:
        return valid_license_ids[license_upper], True

    # let's see if we match the whole name
    if license in licenses_by_names:
        return licenses_by_names[license], True

    # last but not least, let's check against our manual list
    # https://spdx.org/licenses/
    mapping = {
        # Apache 1
        "Apache-1": "Apache-1.0",
        "Apache1": "Apache-1.0",
        "Apache 1.0": "Apache-1.0",
        "Apache 1": "Apache-1.0",
        "Apache Software License, Version 1.1": "Apache-1.1",
        # Apache 2
        "Apache-2": "Apache-2.0",
        "Apache2": "Apache-2.0",
        "Apache 2.0": "Apache-2.0",
        "Apache 2": "Apache-2.0",
        "Apache 2.0 License": "Apache-2.0",
        "Apache License, Version 2.0": "Apache-2.0",
        "The Apache Software License, Version 2.0": "Apache-2.0",
        "Apache Software License - Version 2.0": "Apache-2.0",
        "Apache License Version 2.0": "Apache-2.0",
        "Apache License Version 2": "Apache-2.0",
        "Apache Public License 2.0": "Apache-2.0",
        "The Apache License, Version 2.0": "Apache-2.0",
        "APACHE LICENSE 2.0": "Apache-2.0",
        "ALv2": "Apache-2.0",
        # BSD
        "BSD License": "BSD",
        # BSD-2-Clause
        "Simplified BSD License": "BSD-2-Clause",
        "FreeBSD License": "BSD-2-Clause",
        # BSD-3-Clause
        "New BSD License": "BSD-3-Clause",
        "The New BSD License": "BSD-3-Clause",
        "Modified BSD License": "BSD-3-Clause",
        "The BSD 3-Clause License": "BSD-3-Clause",
        "BSD Licence 3": "BSD-3-Clause",
        "3-Clause BSD License": "BSD-3-Clause",
        # GPL 2
        "GPL2": "GPL-2.0",
        "GPL-2": "GPL-2.0",
        # GPL 2 with exceptions
        "GPLv2+CE": "GPL-2.0 w/Classpath Exception",
        "GPL2 w/ CPE": "GPL-2.0 w/Classpath Exception",
        "GNU General Public License (GPL), version 2, with the Classpath exception": "GPL-2.0 w/Classpath Exception",
        "GNU General Public License, version 2 (GPL2), with the classpath exception": "GPL-2.0 w/Classpath Exception",
        "GPLv2 WITH classpath exception": "GPL-2.0 w/Classpath Exception",
        # GPL 3
        "GPL 3": "GPL-3.0",
        "GPL3": "GPL-3.0",
        "GPL-3": "GPL-3.0",
        # LGPL
        "GNU Lesser Public License": "LGPL",
        "GNU Lesser General Public License": "LGPL",
        # LGPL 2
        "LGPL 2": "LGPL-2.0",
        "LGPL, version 2": "LGPL-2.0",
        "GNU Library General Public License, version 2": "LGPL-2.0",
        # LGPL 2.1
        "LGPL 2.1": "LGPL-2.1",
        "LGPL, version 2.1": "LGPL-2.1",
        "GNU Lesser General Public License, version 2.1": "LGPL-2.1",
        # LGPL 3
        "LGPL 3": "LGPL-3.0",
        "GNU Lesser General Public License, version 3": "LGPL-3.0",
        # MPL-2.0
        "MPL 2.0": "MPL-2.0",
        # CPL
        "Common Public License Version 1.0": "CPL-1.0",
        "Common Public License, version 1.0 (CPL-1.0)": "CPL-1.0",
        # Python
        "Python": "Python-2.0",
        "Python-2": "Python-2.0",
        "PSF": "Python-2.0",
        "PSFL": "Python-2.0",
        "Python Software Foundation License": "Python-2.0",
        # MIT
        "The MIT License": "MIT",
        "MIT license": "MIT",
        "M AND I AND T": "MIT",
        # EPL-1.0
        "Eclipse Public License 1.0": "EPL-1.0",
        "Eclipse Public License v1.0": "EPL-1.0",
        "Eclipse Public License - v 1.0": "EPL-1.0",
        "Eclipse Public License - Version 1.0": "EPL-1.0",
        "Eclipse Public License, Version 1.0": "EPL-1.0",
        "Eclipse Public License (EPL), Version 1.0": "EPL-1.0",
        # EPL-2.0
        "Eclipse Public License 2.0": "EPL-2.0",
        "Eclipse Public License v2.0": "EPL-2.0",
        "Eclipse Public License - v 2.0": "EPL-2.0",
        "Eclipse Public License - Version 2.0": "EPL-2.0",
        "Eclipse Public License, Version 2.0": "EPL-2.0",
        "Eclipse Public License (EPL), Version 2.0": "EPL-2.0",
        # CDDL
        "COMMON DEVELOPMENT AND DISTRIBUTION LICENSE": "CDDL",
        "COMMON DEVELOPMENT AND DISTRIBUTION LICENSE (CDDL)": "CDDL",
    }

    mapping = {k.upper(): v for k, v in mapping.items()}

    if license.upper() in mapping:
        return mapping[license_upper], True

    return license, False
