import pytest
from physics_engine.dopants import get_dopant, DOPANTS


def test_all_four_dopants_loadable():
    for symbol in ["B", "P", "As", "Sb"]:
        d = get_dopant(symbol)
        assert d.symbol == symbol


def test_D0_positive_for_all():
    for symbol in ["B", "P", "As", "Sb"]:
        assert get_dopant(symbol).D0 > 0


def test_Ea_within_literature_range():
    # Sze & Ng values for Si dopants are 3.0–4.5 eV
    for symbol in ["B", "P", "As", "Sb"]:
        ea = get_dopant(symbol).Ea
        assert 3.0 <= ea <= 4.5, f"{symbol}: Ea={ea} eV outside [3.0, 4.5]"


def test_boron_is_p_type():
    assert get_dopant("B").carrier_type == "p-type"


def test_n_type_dopants():
    for symbol in ["P", "As", "Sb"]:
        assert get_dopant(symbol).carrier_type == "n-type"


def test_unknown_dopant_raises_value_error():
    with pytest.raises(ValueError, match="Unknown dopant"):
        get_dopant("Ge")


def test_dopants_dict_has_four_entries():
    assert len(DOPANTS) == 4
