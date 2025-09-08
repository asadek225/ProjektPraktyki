# main.py

from simulator import LogicGate, Circuit, TruthTable

# Initialize the simulator for 3 qubits
tt = TruthTable(4)
simulator = LogicGate(tt)
# Create a quantum circuit and add gates
circuit = Circuit()
circuit.add_gate(2)                   # QNOT
circuit.add_gate(0, 1)         # CNOT
circuit.add_gate(2, 0, 1)       # TOFFOLI
circuit.add_gate(1, 0, 2, 3)       # MCT

# Display gate instructions
print("Quantum Circuit Instructions:")
circuit.show_instructions()

# Print initial truth table
print("\nTruth Table Before Execution:")
print(tt.get_vectors())

# Apply circuit
circuit.apply_all_gates(simulator)
print("\nTruth Table After Execution:")
print(tt.get_vectors())

# # Reverse the circuit (undo)
# circuit.apply_all_gates_reverse(simulator)
# print("\nTruth Table After Reversing:")
# print(tt.get_vectors())

simulator.apply_gate_to_all(2)# Apply only the CNOT gate
print(tt.get_vectors())
circuit.remove_instruction(1)
circuit.show_instructions()