import simulator as sim

ideal = sim.TruthTable(3)
tt = sim.TruthTable(3)
tt.set_output_permutation([3, 0, 2, 1, 4, 5, 6, 7])
lg = sim.LogicGate(tt)
cir = sim.Circuit()
test = [[0, 0, 1], [0, 0, 0], [0, 1, 1], [0, 1, 0], [1, 0, 1], [1, 1, 1], [1, 0, 0], [1, 1, 0]]
tt.set_vectors(test)



def algorithm(ideal: sim.TruthTable, f: sim.TruthTable):
    #step 1
    lg = sim.LogicGate(f)
    while any(f.get_single_vector(0)):
        vec = f.get_single_vector(0)           # za każdym obrotem czytaj na nowo
        for idx, bit in enumerate(vec):
            if bit == 1:
                lg.apply_gate_to_all(idx)
                cir.add_gate(idx)
    print("cel:", ideal.get_vectors())
    print("obecny stan:", f.get_vectors())
    #step 2
    for i in range(2**f.n):
        fv = f.get_single_vector(i)
        iv = ideal.get_single_vector(i)

        if fv == iv:
            continue

        p = [k for k, (a, b) in enumerate(zip(iv, fv)) if a == 1 and b == 0]
        q = [k for k, (a, b) in enumerate(zip(iv, fv)) if a == 0 and b == 1]
        print("p:", p)
        print("q:", q)
        print(f"Wiersz i={i}: f={fv}, ideal={iv}")
        if any(p):
            print("!")
            target = p[0]
            controls = [j for j, b in enumerate(fv) if b == 1 and j != target]
            print("Ptarget:", target, "Pcontrols:", controls)
            lg.apply_gate_to_all(p[0], *controls)
            cir.add_gate(p[0], *controls)
            print(f.get_vectors())
        if any(q):
            target = q[0]
            controls = [j for j, b in enumerate(iv) if b == 1 and j != target]
            print("Qtarget:", target, "Qcontrols:", controls, "\n")
            lg.apply_gate_to_all(q[0], *controls)
            cir.add_gate(q[0], *controls)

algorithm(ideal, tt)

print("Obliczone:", tt.get_vectors())
cir.show_instructions()
