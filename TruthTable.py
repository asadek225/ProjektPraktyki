import gzip
import itertools
import json
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
        Sets the truth table to the given list of bits.
        Each element must be a list of length n.
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
        return [int(b) for b in format(idx, f"0{n}b")]

    def perm_to_bitlist(self, perm):
        """
        Converts a permutation of indices to a list of bits.
        Returns a list [[bits], [bits], ...] corresponding to the elements of perm.
        """
        self._check_perm(perm)
        return [self._idx_to_bits(f, self.n) for f in perm]

    def get_vectors_as_ints(self):
        """
        Returns the vectors as a list of integers.
        Each bit vector is converted to its corresponding decimal number.
        """
        return [int("".join(map(str, vector)), 2) for vector in self.vectors]

    @staticmethod
    def all_permutations(n: int):  # static method factory design pattern
        """
        Generator of all permutations for the truth table
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

    def __copy__(self):
        new_tt = TruthTable(self.n)
        new_tt.vectors = [vec.copy() for vec in self.vectors]
        return new_tt
