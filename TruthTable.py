import itertools
import json
import gzip
from typing import List


class TruthTable:
    def __init__(self, num_qubits: int, initial_permutation: List[int] = None):
        self.n = num_qubits

        if initial_permutation is not None:
            perm = initial_permutation
            self._check_perm(perm)
            self.vectors = [self._idx_to_bits(i, self.n) for i in perm]

        else:
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

    def get_vectors_as_ints(self):
        """
        Zwraca wektory jako listę liczb całkowitych.
        Każdy wektor bitów jest konwertowany na odpowiednią liczbę dziesiętną.
        """
        return [int(''.join(map(str, vector)), 2) for vector in self.vectors]

    @staticmethod
    def all_permutations(n: int):  # static method factory desgin pattern
        """
        Generator wszystkich permutacji dla tablicy prawdy
        """
        N = 1 << n
        all_truth_tables = []
        for permutation in itertools.permutations(range(N)):
            tt = TruthTable(n, permutation)
            all_truth_tables.append(tt)
        return all_truth_tables

    def dump_all_perms_jsonl(self, path="permutacje_n3.jsonl"):
        N = 1 << self.n
        open_fn = gzip.open if path.endswith(".gz") else open
        with open_fn(path, "wt", encoding="utf-8") as f:
            for perm in itertools.permutations(range(N)):
                bitlist = self.perm_to_bitlist(perm)  # [[...],[...],...]
                json.dump(bitlist, f, separators=(",", ":"))
                f.write("\n")
        return path

    # for tt in TruthTables.all_permutations(3):
    #     circ = synth(tt)