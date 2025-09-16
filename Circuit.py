from typing import List
from TruthTable import TruthTable
from LogicGate import LogicGate

class Circuit:
    def __init__(self):
        self.instructions: List[LogicGate] = []

    def add_gate(self, lg: LogicGate):
        self.instructions.append(lg)

    def add_gate_from_idx(self, *qubits: int):
        lg = LogicGate(*qubits)
        self.add_gate(lg)

    def apply_gate_to_vector(self, vector: List[int]):
        for lg in self.instructions:
            lg.apply_gate_to_vector(vector)

    def apply_gate_to_truth_table(self, tt: TruthTable):
        for lg in self.instructions:
            lg.apply_gate_to_truth_table(tt)

    def apply_all_gates(self, tt: TruthTable):
        for gate in self.instructions:
            gate.apply_gate_to_truth_table(tt)

    def apply_all_gates_reverse(self, tt: TruthTable):
        for gate in reversed(self.instructions):
            gate.apply_gate_to_truth_table(tt)

    def show_instructions(self):
        for gate in self.instructions:
            gate_name = {
                1: "QNOT",
                2: "CNOT",
                3: "TOFFOLI"
            }.get(len(gate.qubits), "MCT")
            print(f"{gate_name}: {gate}")

    def remove_instruction(self, index: int):
        self.instructions.pop(index)

    def remove_all_instructions(self):
        self.instructions.clear()
