import simulator as sim

ideal = sim.TruthTable(3)
tt = sim.TruthTable(3)
tt.set_output_permutation([1, 2, 6, 0, 5, 7, 4, 3])
lg = sim.LogicGate(tt)
cir = sim.Circuit()
# test = [[0, 0, 1], [0, 0, 0], [0, 1, 1], [0, 1, 0], [1, 0, 1], [1, 1, 1], [1, 0, 0], [1, 1, 0]]
# tt.set_vectors(test)



def algorithm(ideal: sim.TruthTable, f: sim.TruthTable):
    #step 1
    lg = sim.LogicGate(f)
    print("cel:", ideal.get_vectors())
    print("obecny stan:", f.get_vectors())
    while any(f.get_single_vector(0)):
        vec = f.get_single_vector(0)           # za każdym obrotem czytaj na nowo
        for idx, bit in enumerate(vec):
            if bit == 1:
                lg.apply_gate_to_all(idx)
                cir.add_gate(idx)
    print("1. stan:", f.get_vectors())
    #step 2
    for i in range(1, 2**f.n):
        fv = f.get_single_vector(i)
        iv = ideal.get_single_vector(i)
        print("i:", i, "fv:", fv, "iv:", iv)
        if fv == iv:
            print("takie same")
            continue
        while(fv!=iv):
            p = [k for k, (a, b) in enumerate(zip(iv, fv)) if a == 1 and b == 0]
            q = [k for k, (a, b) in enumerate(zip(iv, fv)) if a == 0 and b == 1]
            print("p:", p)
            print("q:", q)
            print(f"Wiersz i={i}: f={fv}, ideal={iv}")
            if len(p) != 0:
                target = p[0]
                controls = [j for j, b in enumerate(fv) if b == 1 and j != target]
                print("Ptarget:", target, "Pcontrols:", controls)
                lg.apply_gate_to_all(p[0], *controls)
                cir.add_gate(p[0], *controls)
                print(f.get_vectors())
            if len(q) != 0:
                target = q[0]
                controls = [j for j, b in enumerate(iv) if b == 1 and j != target]
                print("Qtarget:", target, "Qcontrols:", controls, "\n")
                lg.apply_gate_to_all(q[0], *controls)
                cir.add_gate(q[0], *controls)

algorithm(ideal, tt)

print("Obliczone:", tt.get_vectors())
cir.show_instructions()

test = sim.TruthTable(3)
test_gate = sim.LogicGate(test)
print("\nWykonanie instrukcji na nowej tablicy prawdy:")
print("Stan początkowy:", test.get_vectors())
cir.apply_all_gates_reverse(test_gate)
print("Stan po wykonaniu instrukcji:", test.get_vectors_as_ints())