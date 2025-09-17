def qnot(vector, target):
    vector[target] = int(not vector[target])
    return vector

def cnot(vector, target, control):
    if vector[control] == 1:
        qnot(vector, target)
    return vector

def Toffoli(vector, target, control1, control2):
    if vector[control1] == 1 and vector[control2] == 1:
        qnot(vector, target)
    return vector

def MCT(vector, target, *controls):
    if all(vector[i] for i in controls):
        qnot(vector, target)
    return vector


class LogicGate:

    def __init__(self, *qubits):
        self.qubits = qubits

    def apply_gate_to_vector(self, vector):
        if len(self.qubits) == 1:
            qnot(vector, self.qubits[0])
        elif len(self.qubits) == 2:
            cnot(vector, self.qubits[0], self.qubits[1])
        elif len(self.qubits) == 3:
            Toffoli(vector, self.qubits[0], self.qubits[1], self.qubits[2])
        elif len(self.qubits) > 3:
            MCT(vector, self.qubits[0], *self.qubits[1:])

    def apply_gate_to_truth_table(self, truth_table):
        for vector in truth_table.get_vectors():
            self.apply_gate_to_vector(vector)
