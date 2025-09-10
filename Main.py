# main.py
from simulator import LogicGate, Circuit, TruthTable, Synthesizer

q_num = 3
tt = TruthTable(q_num)
simulator = LogicGate(tt)
circuit = Circuit()

# Use Synthesizer
permutation = [1, 0, 2, 3, 4, 5, 6, 7]  # Example permutation
synth = Synthesizer(simulator, circuit, q_num)
synth.synthesize(permutation)

print("\nCircuit after synthesis:")
circuit.show_instructions()

print("\nTruth Table After synthesis:")
print(tt.get_vectors())

circuit.apply_all_gates(simulator)
print("\nTruth Table After Circuit Execution:")
print(tt.get_vectors())