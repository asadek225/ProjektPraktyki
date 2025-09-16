import unittest

import utilities as sim

ideal = sim.TruthTable(3)
tt = sim.TruthTable(3)
tt.set_output_permutation([7, 1, 4, 3, 6, 5, 0, 2])
cir = sim.Circuit()


def algorithm(f: sim.TruthTable, cir: sim.Circuit, verbose: bool = False):
    lg = sim.LogicGate(f)
    if verbose:
        print("cel:", ideal.get_vectors())
        print("obecny stan:", f.get_vectors())

    #Step 1:
    while any(f.get_single_vector(0)):
        vec = f.get_single_vector(0)
        for idx, bit in enumerate(vec):
            if bit == 1:
                lg.apply_gate_to_all(idx)
                cir.add_gate(idx)

    if verbose:
        print("1. stan:", f.get_vectors())

    #Step 2:
    for i in range(1, 2**f.n):
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

            lg.apply_gate_to_all(target, *controls)
            cir.add_gate(target, *controls)

            fv = f.get_single_vector(i)
            if verbose:
                print("po P:", f.get_vectors())

        q = [k for k, (a, b) in enumerate(zip(iv, fv)) if a == 0 and b == 1]
        for target in list(q):
            controls = [j for j, b in enumerate(iv) if b == 1 and j != target]
            if verbose:
                print("Qtarget:", target, "Qcontrols:", controls)

            lg.apply_gate_to_all(target, *controls)
            cir.add_gate(target, *controls)
            fv = f.get_single_vector(i)
            if verbose:
                print("po Q:", f.get_vectors())

    cir.show_instructions()
    return f



# algorithm(tt, cir, verbose=True)

