import lobs

import nlohmann_json
import lib_a


class ExternalPackageExample(
    lobs.Package,
    version=lobs.Version(0, 0, 1),
    description="An example project that uses an external package.",
):
    app = lobs.cpp.project.SimpleManagedApplication(
        linked_libraries=[nlohmann_json.NlohmannJsonPackage, lib_a.LibA],
        source_files=[lobs.Path(__file__).parent / "main.cpp"],
    )
