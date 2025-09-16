import gates

class LogicGate:
    # def __init__(self, truth_table: TruthTable):
    #     self.truth_table = truth_table

    def __init__(self, *qubits):
        self.qubits = qubits

    def apply_gate_to_vector(self, vector):
        if len(self.qubits) == 1:
            gates.qnot(vector, self.qubits[0])
        elif len(self.qubits) == 2:
            gates.cnot(vector, self.qubits[0], self.qubits[1])
        elif len(self.qubits) == 3:
            gates.Toffoli(vector, self.qubits[0], self.qubits[1], self.qubits[2])
        elif len(self.qubits) > 3:
            gates.MCT(vector, self.qubits[0], *self.qubits[1:])

    def apply_gate_to_truth_table(self, truth_table):
        for vector in truth_table.get_vectors():
            self.apply_gate_to_vector(vector)
