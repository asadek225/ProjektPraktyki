import pytest

from LogicGate import LogicGate
from NumOfGatesOptimized import hamming_distance, algorithm
from TruthTable import TruthTable


# === Testy hamming_distance ===


def test_hamming_distance_identical():
    tt1 = [[0, 0], [0, 1], [1, 0], [1, 1]]
    tt2 = [[0, 0], [0, 1], [1, 0], [1, 1]]
    assert hamming_distance(tt1, tt2) == 0


def test_hamming_distance_simple():
    tt1 = [[0, 0], [0, 1], [1, 0], [1, 1]]
    tt2 = [[0, 0], [0, 1], [1, 1], [1, 0]]
    assert hamming_distance(tt1, tt2) == 2


def test_hamming_distance_all_different():
    tt1 = [[0, 0], [0, 0], [0, 0], [0, 0]]
    tt2 = [[1, 1], [1, 1], [1, 1], [1, 1]]
    assert hamming_distance(tt1, tt2) == 8


def test_hamming_distance_invalid_size():
    tt1 = [[0, 0], [0, 1]]
    tt2 = [[0, 0]]
    with pytest.raises(ValueError):
        hamming_distance(tt1, tt2)


def test_hamming_distance_invalid_vector_length():
    tt1 = [[0, 0], [0, 1]]
    tt2 = [[0], [1]]
    with pytest.raises(ValueError):
        hamming_distance(tt1, tt2)


# === Testy algorytmu end-to-end ===
# Idea: bierzemy idealną tablicę, psujemy ją znanymi bramkami (NOT/CNOT/Toffoli),
# a potem sprawdzamy, że algorithm(f) przywraca idealną.


def _apply_gates(tt: TruthTable, gates: list[tuple[int, ...]]) -> TruthTable:
    """
    Pomocniczo: zwraca KOPIĘ tt po zastosowaniu listy bramek.
    Każda bramka to krotka: (target, [opcjonalne sterowania...])
    """
    tmp = tt.__copy__()
    for g in gates:
        gate = LogicGate(*g)
        gate.apply_gate_to_truth_table(tmp)
    return tmp


def test_algorithm_restores_ideal_1_qubit():
    ideal = TruthTable(1)
    # "psujemy" idealną tablicę pojedynczym NOTem na bicie 0
    f = _apply_gates(ideal, [(0,)])
    # uruchamiamy algorytm – modyfikuje f in-place
    algorithm(f, verbose=False)
    assert f.get_vectors() == ideal.get_vectors()


def test_algorithm_restores_ideal_2_qubits_with_cnot_and_nots():
    ideal = TruthTable(2)
    # Kolejność: X na q0, CNOT (q0 -> q1), X na q1
    # Reprezentujemy jako (target, *controls)
    gates = [
        (0,),  # NOT na q0
        (1, 0),  # CNOT: target=1, control=0
        (1,),  # NOT na q1
    ]
    f = _apply_gates(ideal, gates)
    algorithm(f, verbose=False)
    assert f.get_vectors() == ideal.get_vectors()


def test_algorithm_restores_ideal_3_qubits_with_chain_and_toffoli():
    ideal = TruthTable(3)
    gates = [
        (0,),  # X(q0)
        (1, 0),  # CNOT(q0 -> q1)
        (2, 1),  # CNOT(q1 -> q2)
        (2, 0, 1),  # Toffoli: target=2, controls=0,1
        (0,),  # X(q0) ponownie (zmieniamy rozkład bitów)
    ]
    f = _apply_gates(ideal, gates)
    algorithm(f, verbose=False)
    assert f.get_vectors() == ideal.get_vectors()


@pytest.mark.parametrize("n", [1, 2, 3])
def test_algorithm_leaves_ideal_unchanged(n):
    """Jeśli startujemy z idealnej tablicy, algorytm nic nie powinien zepsuć."""
    f = TruthTable(n)
    algorithm(f, verbose=False)
    assert f.get_vectors() == TruthTable(n).get_vectors()


def test_algorithm_row0_cleanup_side_effects():
    """
    Sprawdza, że algorytm radzi sobie z "brudnym" wierszem 0.
    Tworzymy sytuację, gdzie wiersz 0 ma jakieś jedynki, a algorytm powinien to wyzerować
    zanim przejdzie do dalszych wierszy.
    """
    ideal = TruthTable(2)
    # Zmieniamy tylko wiersz 0 (wektor [0,0]) – zróbmy NOT na obu bitach,
    # co zamienia [0,0] -> [1,1] w wierszu 0.
    dirty = ideal.__copy__()
    LogicGate(0).apply_gate_to_truth_table(dirty)
    LogicGate(1).apply_gate_to_truth_table(dirty)
    algorithm(dirty, verbose=False)
    assert dirty.get_vectors() == ideal.get_vectors()
