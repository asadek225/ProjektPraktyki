import itertools
import json
import gzip
import gates
from typing import List


class TruthTable:
    def __init__(self, num_qubits: int):
        self.n = num_qubits
        self.vectors = [list(bits) for bits in itertools.product([0, 1], repeat=num_qubits)]

    def get_vectors(self):
        return self.vectors

    def get_single_vector(self, index: int):
        return self.vectors[index]

    def set_vectors(self, vectors: List[List[int]]):
        """
        Ustawia tablicę prawdy na podaną listę bitów.
        Każdy element musi być listą długości n.
        """
        if not all(len(vec) == self.n for vec in vectors):
            raise ValueError("Kazdy wektor musi mieć dlugośsc rowna liczbie qubitow")
        if len(vectors) != (1 << self.n):
            raise ValueError("Liczba wektorow musi wynosić 2^n")
        self.vectors = [list(vec) for vec in vectors]
        return self

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

    def get_vectors_as_ints(self):
        """
        Zwraca wektory jako listę liczb całkowitych.
        Każdy wektor bitów jest konwertowany na odpowiednią liczbę dziesiętną.
        """
        return [int(''.join(map(str, vector)), 2) for vector in self.vectors]


    def all_permutations(self):
        """
        Generator wszystkich permutacji dla tablicy prawdy
        """
        N = 1 << self.n
        return itertools.permutations(range(N))

    def dump_all_perms_jsonl(self, path="permutacje_n3.jsonl"):
        N = 1 << self.n
        open_fn = gzip.open if path.endswith(".gz") else open
        with open_fn(path, "wt", encoding="utf-8") as f:
            for perm in itertools.permutations(range(N)):
                bitlist = self.perm_to_bitlist(perm)  # [[...],[...],...]
                json.dump(bitlist, f, separators=(",", ":"))
                f.write("\n")
        return path


class LogicGate:
    # def __init__(self, truth_table: TruthTable):
    #     self.truth_table = truth_table

    def __init__(self, *qubits):
        self.qubits = qubits

    def apply_gate_to_vector(self, vector):
        if len(qubits) == 1:
            gates.qnot(vector, self.qubits[0])
        elif len(qubits) == 2:
            gates.cnot(vector, qubits[0], qubits[1])
        elif len(qubits) == 3:
            gates.Toffoli(vector, qubits[0], qubits[1], qubits[2])
        elif len(qubits) > 3:
            gates.MCT(vector, qubits[0], *qubits[1:])

    def apply_gate_to_truth_table(self, truth_table):
        for vector in truth_table.get_vectors():
            self.apply_gate_to_vector(vector, *self.qubits)


class Circuit:
    def __init__(self):
        self.instructions : list[LogicGate] = []

    def add_gate(self, lg: LogicGate):
        self.instructions.append(lg)
    
    def add_gate_from_idx(self, *qubits: int):
        lg = LogicGate(*qubits)
        self.add_gate(lg)

    def apply_gate_to_vector(self, vector: list[int]):
        for lg in self.instructions:
            lg.apply_gate_to_vector(vector)

    def apply_gate_to_truth_table(self, tt: TruthTable):
        for lg in self.instructions:
            lg.apply_gate_to_truth_table(vector)

    
    def apply_gate_at(self, utilities: LogicGate, index: int):
        gate = self.instructions[index]
        utilities.apply_gate_to_all(*gate)

    def apply_all_gates(self, utilities: LogicGate):
        for gate in self.instructions:
            utilities.apply_gate_to_all(*gate)

    def apply_all_gates_reverse(self, utilities: LogicGate):
        for gate in reversed(self.instructions):
            utilities.apply_gate_to_all(*gate)

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

