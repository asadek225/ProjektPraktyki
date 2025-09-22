# test_algorithm.py
import random

import pytest

from Circuit import Circuit
from ComparingAlgorithm import GATE_COSTS, algorithm
from LogicGate import LogicGate
from TruthTable import TruthTable


def _first_bad_index(tt: TruthTable, ideal: TruthTable) -> int:
    for i in range(1 << tt.n):
        if tt.get_single_vector(i) != ideal.get_single_vector(i):
            return i
    return 1 << tt.n


def _random_reversible_tt(n: int, depth: int, rng: random.Random) -> TruthTable:
    tt = TruthTable(n)
    for _ in range(depth):
        target = rng.randrange(n)
        ctrls = [i for i in range(n) if i != target]
        rng.shuffle(ctrls)

        # losowo wybierz „docelową” liczbę sterowań: 0,1,2 (odpowiednio QNOT/CNOT/Toffoli)
        desired_ctrls = rng.choice([0, 1, 2])
        actual_ctrls = ctrls[: min(desired_ctrls, len(ctrls))]  # automatyczna degradacja
        gate = LogicGate(target, *actual_ctrls)
        gate.apply_gate_to_truth_table(tt)
    return tt


def _circuit_cost(cir: Circuit) -> int:
    return sum(GATE_COSTS.get(g.get_type(), 1) for g in cir.instructions)


# === TESTY tylko dla n = 3 ===


@pytest.mark.parametrize("depth", [5, 8, 10, 12])
def test_algorithm_restores_ideal_n3(depth):
    n = 3
    rng = random.Random(1234)
    original = _random_reversible_tt(n, depth, rng)

    f = original.__copy__()
    cir = algorithm(f, verbose=False)

    ideal = TruthTable(n)
    assert f.get_vectors() == ideal.get_vectors()

    reproduced = original.__copy__()
    for g in cir.instructions:
        g.apply_gate_to_truth_table(reproduced)
    assert reproduced.get_vectors() == ideal.get_vectors()


def test_prefix_of_correct_rows_never_decreases_n3():
    n, depth = 3, 12
    rng = random.Random(42)
    start = _random_reversible_tt(n, depth, rng)

    f = start.__copy__()
    cir = algorithm(f, verbose=False)

    ideal = TruthTable(n)
    prev_prefix = 0
    running = start.__copy__()

    for g in cir.instructions:
        g.apply_gate_to_truth_table(running)
        prefix = _first_bad_index(running, ideal)
        assert prefix >= prev_prefix, "Algorytm popsuł wcześniejsze wiersze w trakcie działania"
        prev_prefix = prefix

    assert running.get_vectors() == ideal.get_vectors()


def test_prefers_cheapest_when_safe_simple_qnot_n3():
    n = 3
    tt = TruthTable(n)
    LogicGate(0).apply_gate_to_truth_table(tt)

    f = tt.__copy__()
    cir = algorithm(f, verbose=False)

    ideal = TruthTable(n)
    assert f.get_vectors() == ideal.get_vectors()

    types = [g.get_type() for g in cir.instructions]
    assert 1 in types, "Powinien pojawić się tani QNOT"
    assert types.count(3) == 0, "TOFFOLI nie jest potrzebna w tym scenariuszu"


def test_gate_types_and_costs_coherent_n3():
    n = 3
    tt = TruthTable(n)
    f = tt.__copy__()
    cir = algorithm(f, verbose=False)

    cost = _circuit_cost(cir)
    assert cost >= 0

    for g in cir.instructions:
        t = g.get_type()
        assert t >= 1
        assert t == len(g.get_qubits())
        assert GATE_COSTS.get(t, 1) in (1, 5)
