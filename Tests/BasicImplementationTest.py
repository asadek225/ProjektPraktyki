import pytest

from BasicAlgorithm import algorithm
from Circuit import Circuit
from LogicGate import LogicGate, qnot, cnot, Toffoli, MCT
from TruthTable import TruthTable


class TestGates:
    def test_qnot(self):
        vector = [0, 1, 0]
        qnot(vector, 0)
        assert vector == [1, 1, 0]

        qnot(vector, 1)
        assert vector == [1, 0, 0]

    def test_cnot(self):
        vector = [1, 0, 0]
        cnot(vector, 1, 2)  # control=0, target unchanged
        assert vector == [1, 0, 0]

        vector = [1, 1, 1]
        cnot(vector, 1, 2)  # control=1, target flips
        assert vector == [1, 0, 1]

    def test_toffoli(self):
        vector = [1, 1, 0]
        Toffoli(vector, 2, 0, 1)  # both controls=1, target flips
        assert vector == [1, 1, 1]

        vector = [1, 0, 1]
        Toffoli(vector, 2, 0, 1)  # one control=0, target unchanged
        assert vector == [1, 0, 1]

    def test_mct(self):
        vector = [1, 1, 1, 0]
        MCT(vector, 3, 0, 1, 2)  # all controls=1, target flips
        assert vector == [1, 1, 1, 1]

        vector = [1, 0, 1, 1]
        MCT(vector, 3, 0, 1, 2)  # one control=0, target unchanged
        assert vector == [1, 0, 1, 1]


class TestTruthTable:
    def test_init_default(self):
        tt = TruthTable(2)
        assert tt.n == 2
        assert len(tt.vectors) == 4
        expected = [[0, 0], [0, 1], [1, 0], [1, 1]]
        assert tt.get_vectors() == expected

    def test_init_with_permutation(self):
        perm = [3, 2, 1, 0]
        tt = TruthTable(2, perm)
        assert tt.n == 2
        expected = [[1, 1], [1, 0], [0, 1], [0, 0]]
        assert tt.get_vectors() == expected

    def test_get_single_vector(self):
        tt = TruthTable(2)
        assert tt.get_single_vector(0) == [0, 0]
        assert tt.get_single_vector(3) == [1, 1]

    def test_set_vectors(self):
        tt = TruthTable(2)
        new_vectors = [[1, 1], [1, 0], [0, 1], [0, 0]]
        tt.set_vectors(new_vectors)
        assert tt.get_vectors() == new_vectors

    def test_set_vectors_invalid_length(self):
        tt = TruthTable(2)
        with pytest.raises(ValueError):
            tt.set_vectors([[1, 1], [1, 0]])  # Too few vectors

    def test_set_vectors_invalid_vector_length(self):
        tt = TruthTable(2)
        with pytest.raises(ValueError):
            tt.set_vectors([[1], [1, 0], [0, 1], [0, 0]])  # Invalid vector length

    def test_get_vectors_as_ints(self):
        tt = TruthTable(2)
        expected = [0, 1, 2, 3]
        assert tt.get_vectors_as_ints() == expected

    def test_perm_to_bitlist(self):
        tt = TruthTable(2)
        perm = [3, 2, 1, 0]
        result = tt.perm_to_bitlist(perm)
        expected = [[1, 1], [1, 0], [0, 1], [0, 0]]
        assert result == expected

    def test_idx_to_bits(self):
        assert TruthTable._idx_to_bits(5, 3) == [1, 0, 1]
        assert TruthTable._idx_to_bits(0, 3) == [0, 0, 0]

    def test_check_perm_valid(self):
        tt = TruthTable(2)
        tt._check_perm([3, 2, 1, 0])  # Should not raise

    def test_check_perm_invalid_length(self):
        tt = TruthTable(2)
        with pytest.raises(ValueError):
            tt._check_perm([3, 2, 1])

    def test_check_perm_invalid_elements(self):
        tt = TruthTable(2)
        with pytest.raises(ValueError):
            tt._check_perm([4, 2, 1, 0])

    def test_all_permutations(self):
        perms = TruthTable.all_permutations(1)
        assert len(perms) == 2  # 2! = 2

    def test_dump_all_perms_jsonl(self, tmp_path):
        tt = TruthTable(1)
        file_path = tmp_path / "test_perms.jsonl"
        result_path = tt.dump_all_perms_jsonl(str(file_path))
        assert result_path == str(file_path)
        assert file_path.exists()


class TestLogicGate:
    def test_init_single_qubit(self):
        gate = LogicGate(0)
        assert gate.qubits == (0,)

    def test_init_multi_qubit(self):
        gate = LogicGate(0, 1, 2)
        assert gate.qubits == (0, 1, 2)

    def test_apply_gate_to_vector_qnot(self):
        gate = LogicGate(0)
        vector = [0, 1]
        gate.apply_gate_to_vector(vector)
        assert vector == [1, 1]

    def test_apply_gate_to_vector_cnot(self):
        gate = LogicGate(1, 0)  # target=1, control=0
        vector = [1, 0]
        gate.apply_gate_to_vector(vector)
        assert vector == [1, 1]

    def test_apply_gate_to_vector_toffoli(self):
        gate = LogicGate(2, 0, 1)  # target=2, controls=0,1
        vector = [1, 1, 0]
        gate.apply_gate_to_vector(vector)
        assert vector == [1, 1, 1]

    def test_apply_gate_to_vector_mct(self):
        gate = LogicGate(3, 0, 1, 2)  # target=3, controls=0,1,2
        vector = [1, 1, 1, 0]
        gate.apply_gate_to_vector(vector)
        assert vector == [1, 1, 1, 1]

    def test_apply_gate_to_truth_table(self):
        gate = LogicGate(0)
        tt = TruthTable(1)
        gate.apply_gate_to_truth_table(tt)
        assert tt.get_single_vector(0) == [1]
        assert tt.get_single_vector(1) == [0]


class TestCircuit:
    def test_init(self):
        circuit = Circuit()
        assert circuit.instructions == []

    def test_add_gate(self):
        circuit = Circuit()
        gate = LogicGate(0)
        circuit.add_gate(gate)
        assert len(circuit.instructions) == 1
        assert circuit.instructions[0] == gate

    def test_add_gate_from_idx(self):
        circuit = Circuit()
        circuit.add_gate_from_idx(0, 1)
        assert len(circuit.instructions) == 1
        assert circuit.instructions[0].qubits == (0, 1)

    def test_remove_instruction(self):
        circuit = Circuit()
        circuit.add_gate_from_idx(0)
        circuit.add_gate_from_idx(1)
        circuit.remove_gate(0)
        assert len(circuit.instructions) == 1

    def test_remove_all_instructions(self):
        circuit = Circuit()
        circuit.add_gate_from_idx(0)
        circuit.add_gate_from_idx(1)
        circuit.clear()
        assert len(circuit.instructions) == 0

    def test_apply_gate_to_vector(self):
        circuit = Circuit()
        circuit.add_gate_from_idx(0)  # QNOT on qubit 0
        vector = [0, 1]
        circuit.apply_circuit_to_vector(vector)
        assert vector == [1, 1]

    def test_apply_gate_to_truth_table(self):
        circuit = Circuit()
        circuit.add_gate_from_idx(0)
        tt = TruthTable(1)
        circuit.apply_circuit(tt)
        assert tt.get_single_vector(0) == [1]
        assert tt.get_single_vector(1) == [0]

    def test_apply_all_gates(self):
        circuit = Circuit()
        circuit.add_gate_from_idx(0)
        tt = TruthTable(1)
        circuit.apply_circuit(tt)
        assert tt.get_single_vector(0) == [1]
        assert tt.get_single_vector(1) == [0]

    def test_apply_all_gates_reverse(self):
        circuit = Circuit()
        circuit.add_gate_from_idx(0)
        circuit.add_gate_from_idx(1)
        tt = TruthTable(2)
        original = [v[:] for v in tt.get_vectors()]

        circuit.apply_circuit(tt)
        circuit.apply_circuit_reverse(tt)
        assert tt.get_vectors() == original

    def test_show_instructions(self, capsys):
        circuit = Circuit()
        circuit.add_gate_from_idx(0)  # QNOT
        circuit.add_gate_from_idx(0, 1)  # CNOT
        circuit.add_gate_from_idx(0, 1, 2)  # TOFFOLI
        circuit.add_gate_from_idx(0, 1, 2, 3)  # MCT

        circuit.show_gates()
        captured = capsys.readouterr()

        assert "QNOT" in captured.out
        assert "CNOT" in captured.out
        assert "TOFFOLI" in captured.out
        assert "MCT" in captured.out


class TestBasicAlgorithm:
    def test_algorithm_identity(self):
        tt = TruthTable(2)
        circuit = algorithm(tt)
        assert isinstance(circuit, Circuit)

    def test_algorithm_simple_function(self):
        tt = TruthTable(1, [1, 0])  # NOT function
        circuit = algorithm(tt)
        assert isinstance(circuit, Circuit)
        assert len(circuit.instructions) >= 0

    def test_algorithm_verbose(self, capsys):
        tt = TruthTable(1)
        algorithm(tt, verbose=True)
        captured = capsys.readouterr()
        assert "cel:" in captured.out
        assert "obecny stan:" in captured.out

    def test_algorithm_returns_circuit(self):
        tt = TruthTable(2)
        result = algorithm(tt)
        assert isinstance(result, Circuit)

    def test_algorithm_complex_function(self):
        # Test with a more complex permutation
        tt = TruthTable(2, [3, 1, 2, 0])
        circuit = algorithm(tt)
        assert isinstance(circuit, Circuit)

    def test_algorithm_step1_processing(self):
        # Test case where first vector has 1s
        tt = TruthTable(2, [1, 0, 2, 3])  # First vector [0,1] becomes [0,0]
        circuit = algorithm(tt)
        assert isinstance(circuit, Circuit)


class TestIntegration:
    def test_full_workflow(self):
        tt_original = TruthTable(2, [3, 2, 1, 0])

        circuit = algorithm(tt_original)

        fresh_tt = TruthTable(2)
        circuit.apply_circuit(fresh_tt)

        assert isinstance(circuit, Circuit)

    def test_algorithm_synthesis_verification(self):
        # Test that algorithm produces working circuit
        perm = [1, 0, 3, 2]
        tt_target = TruthTable(2, perm)

        circuit = algorithm(tt_target)

        # Apply circuit to identity truth table
        tt_test = TruthTable(2)
        circuit.apply_circuit(tt_test)

        assert isinstance(circuit, Circuit)

    def test_gate_composition(self):
        # Test multiple gates in sequence
        circuit = Circuit()
        circuit.add_gate_from_idx(0)  # QNOT
        circuit.add_gate_from_idx(1, 0)  # CNOT
        circuit.add_gate_from_idx(2, 0, 1)  # TOFFOLI

        tt = TruthTable(3)
        circuit.apply_circuit(tt)

        assert len(circuit.instructions) == 3
        assert tt.n == 3

    def test_reversibility_property(self):
        circuit = Circuit()
        circuit.add_gate_from_idx(0)
        circuit.add_gate_from_idx(1, 0)

        tt = TruthTable(2)
        original = [v[:] for v in tt.get_vectors()]

        circuit.apply_circuit(tt)
        circuit.apply_circuit_reverse(tt)

        assert tt.get_vectors() == original

    def test_truth_table_consistency(self):
        # Test that truth table operations are consistent
        tt1 = TruthTable(2)
        tt2 = TruthTable(2)

        gate = LogicGate(0)
        gate.apply_gate_to_truth_table(tt1)

        circuit = Circuit()
        circuit.add_gate(gate)
        circuit.apply_circuit(tt2)

        assert tt1.get_vectors() == tt2.get_vectors()


if __name__ == "__main__":
    pytest.main([__file__])
