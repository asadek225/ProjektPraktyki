from simulator import Synthesizer, TruthTable, LogicGate

# Inicjalizacja syntezy dla 3 qubitów
synthesizer = Synthesizer(3)

# Przykładowa permutacja
perm = [0, 1, 2, 3, 4, 6, 5, 7]

# Uruchomienie syntezy
circuit = synthesizer.synthesize(perm)

print("\nWygenerowany obwód:")
circuit.show_instructions()

print("\nTablica prawdy po syntezie:")
print(synthesizer.truth_table.get_vectors())

# Weryfikacja - wykonanie wygenerowanych instrukcji na nowej tablicy
test_table = TruthTable(3)
test_gate = LogicGate(test_table)

print("\nWykonanie instrukcji na nowej tablicy prawdy:")
print("Stan początkowy:", test_table.get_vectors())

circuit.apply_all_gates(test_gate)

print("Stan po wykonaniu instrukcji:", test_table.get_vectors_as_ints())
