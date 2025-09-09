import itertools
import gates

class TruthTable:
    def __init__(self, num_qubits: int):
        self.n = num_qubits
        self.vectors = [list(bits) for bits in itertools.product([0, 1], repeat=num_qubits)]

    def get_vectors(self):
        return self.vectors

    def get_single_vector(self, index: int):
        return self.vectors[index]

    def _check_perm(self, perm):
        N = 1 << self.n
        if not isinstance(perm, (list, tuple)) or len(perm) != N:
            raise ValueError("Invalid permutation length")
        if sorted(perm) != list(range(N)):
            raise ValueError("Invalid permutation elements")

    @staticmethod
    def _idx_to_bits(idx: int, n: int):
        return [int(b) for b in format(idx, f'0{n}b')]

    def perm_to_bitlist(self, perm):
        """
        Zamienia permutację indeksów na listę bitów.
        Zwraca listę [ [bity], [bity], ... ] odpowiadającą elementom perm.
        """
        self._check_perm(perm)
        return [self._idx_to_bits(f, self.n) for f in perm]

    def set_output_permutation(self, perm):
        """
        Ustawia tablice prawdy na podstawie podanej permutacji
        Przyklad (n = 3): set_output_permutation([3,7,1,0,4,6,2,5]) ustawia:
        f(0) = 3, f(1) = 7, f(2) = 1, f(3) = 0, f(4) = 4, f(5) = 6, f(6) = 2, f(7) = 5
        """
        self._check_perm(perm)
        self.vectors = [self._idx_to_bits(i, self.n) for i in perm]
        return self

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