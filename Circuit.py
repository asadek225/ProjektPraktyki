from typing import List

from LogicGate import LogicGate
from TruthTable import TruthTable


class Circuit:
    def __init__(self):
        self.instructions: List[LogicGate] = []

    def add_gate(self, lg: LogicGate):
        self.instructions.append(lg)

    def add_gate_from_idx(self, *qubits: int):
        lg = LogicGate(*qubits)
        self.add_gate(lg)

    def apply_circuit_to_vector(self, vector: List[int]):
        for lg in self.instructions:
            lg.apply_gate_to_vector(vector)

    def apply_circuit(self, tt: TruthTable):
        for gate in self.instructions:
            gate.apply_gate_to_truth_table(tt)

    def apply_circuit_reverse(self, tt: TruthTable):
        for gate in reversed(self.instructions):
            gate.apply_gate_to_truth_table(tt)

    def show_gates(self):
        for gate in self.instructions:
            gate_name = {
                1: "QNOT",
                2: "CNOT",
                3: "TOFFOLI"
            }.get(len(gate.qubits), "MCT")
            print(f"{gate_name}: {gate.get_qubits()}")

    def remove_gate(self, index: int):
        self.instructions.pop(index)

    def clear(self):
        self.instructions.clear()
