import io
import itertools
import unittest
from contextlib import redirect_stdout

import utilities as sim
import BasicAlgorithm as al


class FullCorrectnessTest(unittest.TestCase):
    def test_all_permutations_map_to_ideal(self):
        ideal = sim.TruthTable(3)
        N = 1 << ideal.n  # 8

        for perm in itertools.permutations(range(N)):
            with self.subTest(perm=perm):
                f = sim.TruthTable(ideal.n)
                f.set_output_permutation(list(perm))
                cir = sim.Circuit()

                with redirect_stdout(io.StringIO()):
                    al.algorithm(f, cir, verbose=False)

                # po przekształceniach f powinno być równe ideal
                self.assertListEqual(
                    ideal.get_vectors(),
                    f.get_vectors(),
                    msg=f"Permutation failed: {perm}"
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
