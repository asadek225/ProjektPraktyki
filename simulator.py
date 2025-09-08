import itertools
import gates

class TruthTable:
    def __init__(self, num_qubits: int):
        self.vectors = [list(bits) for bits in itertools.product([0, 1], repeat=num_qubits)]

    def get_vectors(self):
        return self.vectors

    def get_single_vector(self, index: int):
        return self.vectors[index]

class LogicGate:
    def __init__(self, truth_table: TruthTable):
        self.truth_table = truth_table

    @staticmethod
    def apply_gate_to_vector(vector, *qubits: int):
        if len(qubits) == 1:
            gates.qnot(vector, qubits[0])
        elif len(qubits) == 2:
            gates.cnot(vector, qubits[0], qubits[1])
        elif len(qubits) == 3:
            gates.Toffoli(vector, qubits[0], qubits[1], qubits[2])
        elif len(qubits) > 3:
            gates.MCT(vector, qubits[0], *qubits[1:])

    def apply_gate_to_all(self, *qubits: int):
        for vector in self.truth_table.get_vectors():
            self.apply_gate_to_vector(vector, *qubits)

class Circuit:
    def __init__(self):
        self.instructions = []

    def add_gate(self, *qubits: int):
        self.instructions.append(qubits)

    def apply_gate_at(self, simulator: LogicGate, index: int):
        gate = self.instructions[index]
        simulator.apply_gate_to_all(*gate)

    def apply_all_gates(self, simulator: LogicGate):
        for gate in self.instructions:
            simulator.apply_gate_to_all(*gate)

    def apply_all_gates_reverse(self, simulator: LogicGate):
        for gate in reversed(self.instructions):
            simulator.apply_gate_to_all(*gate)

    def show_instructions(self):
        for gate in self.instructions:
            gate_name = {
                1: "QNOT",
                2: "CNOT",
                3: "TOFFOLI"
            }.get(len(gate), "MCT")
            print(f"{gate_name}: {gate}")

    def remove_instruction(self, index: int):
        self.instructions.pop(index)

    def remove_all_instructions(self):
        self.instructions.clear()