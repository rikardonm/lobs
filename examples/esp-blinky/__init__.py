import lobs

import esp_blinky


class App(lobs.Package):
    app = lobs.cpp.project.EmbeddedApplication(
        linked_libraries=[esp_blinky.EspBlinky]
    )
