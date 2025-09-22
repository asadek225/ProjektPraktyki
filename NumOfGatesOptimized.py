from itertools import combinations

from Circuit import Circuit
from LogicGate import LogicGate
from TruthTable import TruthTable


# GATE_COSTS = {1: 1, 2: 1, 3: 5}  # QNOT  # CNOT  # TOFFOLI


def hamming_distance(tt1, tt2) -> int:
    """
    Oblicza odległość Hamminga pomiędzy dwiema tablicami prawdy.
    Argumenty:
        tt1, tt2: listy wektorów bitowych (np. [[0,0],[0,1],[1,0],[1,1]])
    """
    if len(tt1) != len(tt2) or any(len(v1) != len(v2) for v1, v2 in zip(tt1, tt2)):
        raise ValueError("Tablice muszą mieć taki sam rozmiar i długość wektorów")
    return sum(sum(b1 != b2 for b1, b2 in zip(vec1, vec2)) for vec1, vec2 in zip(tt1, tt2))


def _no_effect_on_previous_rows(temp_f: TruthTable, ideal: TruthTable, upto_idx: int) -> bool:
    """
    True, jeśli zastosowanie bramki nie zmieniło żadnego wiersza.
    """
    for x in range(upto_idx):
        if temp_f.get_single_vector(x) != ideal.get_single_vector(x):
            return False
    return True


def _pick_and_apply_best_gate(
    f: TruthTable,
    ideal: TruthTable,
    i: int,
    target: int,
    possible_controls: list[int],
    cir: Circuit,
    verbose: bool = False,
) -> bool:
    """
    Dobiera i stosuje najmniejszą ilość bramek (spośród wszystkich podzbiorów sterowań),
    która nie narusza wcześniejszych wierszy. Zwraca True, jeśli cokolwiek zastosowano.
    (Bazuje na wyznaczeniu odległości hamminga).
    """
    best = None
    # Przeszukujemy WSZYSTKIE podzbiory sterowań (włącznie z pustym — QNOT).
    for r in range(len(possible_controls) + 1):
        for ctrls in combinations(possible_controls, r):
            gate = LogicGate(target, *ctrls)
            tmp = f.__copy__()
            gate.apply_gate_to_truth_table(tmp)

            if not _no_effect_on_previous_rows(tmp, ideal, i):
                continue

            gtype = gate.get_type()
            # cost = GATE_COSTS.get(gtype, 1)

            hamming_dist = hamming_distance(
                tmp.get_vectors(), ideal.get_vectors()
            )  # Wyznaczamy odległość hamminga

            key = (hamming_dist, r, list(ctrls))
            if best is None or key < best[0]:
                best = (key, ctrls, gate, tmp)

    if best is None:
        # Nie znaleziono bramki, która nie narusza wcześniejszych wierszy.
        if verbose:
            print(
                f"[i={i}] Brak bezpiecznej bramki dla target={target} przy possible_controls={possible_controls}"
            )
        return False

    # Zastosuj najlepszą bramkę do prawdziwej tablicy i dopisz do obwodu.
    _, ctrls, gate, _ = best
    gate.apply_gate_to_truth_table(f)
    cir.add_gate_from_idx(target, *ctrls)

    if verbose:
        print(
            f"[i={i}] apply: target={target}, controls={list(ctrls)}, "
            f"hamming distance={hamming_distance(f.get_vectors(), ideal.get_vectors())}"
        )

    return True


def algorithm(f: TruthTable, verbose: bool = False) -> Circuit:
    """
    Wersja zoptymalizowana:
    - Krok 1: zeruje wiersz 0 poprzez pojedyncze NOT-y na bitach, które są 1.
    - Krok 2: dla i=1..2^n-1 wyrównuje wiersz i do idealnego,
    """
    num_qubits = f.n
    ideal = TruthTable(num_qubits)
    cir = Circuit()

    if verbose:
        print("\ncel:", ideal.get_vectors())
        print("obecny stan:", f.get_vectors())

    # KROK 1: wyzeruj wiersz 0
    while any(f.get_single_vector(0)):
        vec0 = f.get_single_vector(0)
        for idx, bit in enumerate(vec0):
            if bit == 1:
                gate = LogicGate(idx)  # QNOT na idx
                gate.apply_gate_to_truth_table(f)
                cir.add_gate_from_idx(idx)
    if verbose:
        print("1. stan:", f.get_vectors())

    # KROK 2: przejdź po wierszach i ustawiaj je po kolei
    for i in range(1, 2**f.n):
        fv = f.get_single_vector(i)
        iv = ideal.get_single_vector(i)

        if verbose:
            print(f"\n[i={i}] fv={fv} iv={iv}")

        if fv == iv:
            if verbose:
                print("    już zgodny z celem")
            continue

        # p: bity, które powinny stać się 1 (są 0 -> mają być 1)
        # q: bity, które powinny stać się 0 (są 1 -> mają być 0)
        p = [k for k, (a, b) in enumerate(zip(iv, fv)) if a == 1 and b == 0]
        q = [k for k, (a, b) in enumerate(zip(iv, fv)) if a == 0 and b == 1]

        if verbose:
            print("   p (0->1):", p)
            print("   q (1->0):", q)

        # Najpierw ustawiamy bity, które muszą przejść 0 -> 1.
        # Dla p sterowania bierzemy z aktualnego wiersza fv (tam gdzie bity=1).
        for target in list(p):
            fv = f.get_single_vector(i)  # odśwież
            possible_controls = [j for j, b in enumerate(fv) if b == 1 and j != target]
            _pick_and_apply_best_gate(f, ideal, i, target, possible_controls, cir, verbose=verbose)

        # Następnie bity, które muszą przejść 1 -> 0.
        # Dla q sterowania bierzemy z idealnego wiersza iv (tam gdzie bity=1).
        fv = f.get_single_vector(i)  # odśwież po operacjach p
        q = [k for k, (a, b) in enumerate(zip(iv, fv)) if a == 0 and b == 1]
        for target in list(q):
            iv_now = ideal.get_single_vector(i)
            possible_controls = [j for j, a in enumerate(iv_now) if a == 1 and j != target]
            _pick_and_apply_best_gate(f, ideal, i, target, possible_controls, cir, verbose=verbose)

        if verbose:
            print("   po ustawianiu:", f.get_single_vector(i))

    if verbose:
        print("\nKońcowy obwód:")
        cir.show_gates()

    return cir
