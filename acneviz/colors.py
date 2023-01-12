from dataclasses import dataclass


@dataclass(frozen=True)
class AcneColors:
    """Names defined by coolors.co"""

    pearly_purple: str = "#B2619E"
    dark_sea_green: str = "#79C188"
    mustard: str = "#FDD54D"
    royal_purple: str = "#6E589C"
    sky_blue: str = "#61CAEB"
    rose_madder: str = "#EA142E"
    spanish_blue: str = "#0271B1"
    orchid_pink: str = "#F6C6D5"

    @classmethod
    @property
    def discrete_palette(cls) -> list[str]:
        return [
            cls.pearly_purple,
            cls.dark_sea_green,
            cls.mustard,
            cls.royal_purple,
            cls.sky_blue,
            cls.rose_madder,
            cls.spanish_blue,
            cls.orchid_pink,
        ]
