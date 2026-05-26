from dataclasses import dataclass


@dataclass(frozen=True)
class DopantData:
    symbol: str
    name: str
    carrier_type: str
    D0: float   # pre-exponential factor [cm²/s]
    Ea: float   # activation energy [eV]


DOPANTS: dict[str, DopantData] = {
    "B":  DopantData("B",  "Boron",      "p-type", 0.76,  3.46),
    "P":  DopantData("P",  "Phosphorus", "n-type", 3.85,  3.66),
    "As": DopantData("As", "Arsenic",    "n-type", 0.066, 3.44),
    "Sb": DopantData("Sb", "Antimony",   "n-type", 0.214, 3.65),
}


def get_dopant(symbol: str) -> DopantData:
    if symbol not in DOPANTS:
        raise ValueError(
            f"Unknown dopant '{symbol}'. Valid options: {list(DOPANTS.keys())}"
        )
    return DOPANTS[symbol]
