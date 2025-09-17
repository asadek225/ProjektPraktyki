from Circuit import Circuit
from TruthTable import TruthTable
from LogicGate import LogicGate


def algorithm(f: TruthTable, verbose: bool = False) -> Circuit:
    num_qubits = f.n
    ideal = TruthTable(num_qubits)

    cir = Circuit()

    if verbose:
        print("cel:", ideal.get_vectors())
        print("obecny stan:", f.get_vectors())

    # Step 1:
    while any(f.get_single_vector(0)):
        vec = f.get_single_vector(0)
        for idx, bit in enumerate(vec):
            if bit == 1:
                temp_gate = LogicGate(idx)
                temp_gate.apply_gate_to_truth_table(f)
                cir.add_gate_from_idx(idx)

    if verbose:
        print("1. stan:", f.get_vectors())

    # Step 2:
    for i in range(1, 2 ** f.n):
        fv = f.get_single_vector(i)
        iv = ideal.get_single_vector(i)

        if verbose:
            print("i:", i, "fv:", fv, "iv:", iv)

        if fv == iv:
            if verbose:
                print("takie same")
            continue

        # OBLICZ p i q na bazie aktualnego fv i iv
        p = [k for k, (a, b) in enumerate(zip(iv, fv)) if a == 1 and b == 0]
        q = [k for k, (a, b) in enumerate(zip(iv, fv)) if a == 0 and b == 1]

        if verbose:
            print("p:", p)
            print("q:", q)
            print(f"Wiersz i={i}: f={fv}, ideal={iv}")

        for target in list(p):
            controls = [j for j, b in enumerate(fv) if b == 1 and j != target]
            if verbose:
                print("Ptarget:", target, "Pcontrols:", controls)

            temp_gate = LogicGate(target, *controls)
            temp_gate.apply_gate_to_truth_table(f)
            cir.add_gate_from_idx(target, *controls)

            fv = f.get_single_vector(i)
            if verbose:
                print("po P:", f.get_vectors())

        q = [k for k, (a, b) in enumerate(zip(iv, fv)) if a == 0 and b == 1]
        for target in list(q):
            controls = [j for j, b in enumerate(iv) if b == 1 and j != target]
            if verbose:
                print("Qtarget:", target, "Qcontrols:", controls)

            temp_gate = LogicGate(target, *controls)
            temp_gate.apply_gate_to_truth_table(f)
            cir.add_gate_from_idx(target, *controls)
            fv = f.get_single_vector(i)
            if verbose:
                print("po Q:", f.get_vectors())

    if verbose:
        cir.show_gates()

    return cir
