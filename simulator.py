import itertools
import gates

class TruthTable:
    def __init__(self, num_qubits: int):
        self.vectors = [list(bits) for bits in itertools.product([0, 1], repeat=num_qubits)]

    def get_vectors(self):
        return self.vectors

    def get_single_vector(self, index: int):
        return self.vectors[index]

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

class Synthesizer:
    def __init__(self, simulator: LogicGate, circuit: Circuit, num_qubits: int):
        self.simulator = simulator
        self.circuit = circuit
        self.num_qubits = num_qubits

    @staticmethod
    def bit(num: int, pos: int) -> int:
        return (num >> pos) & 1

    @staticmethod
    def bits_where_1(num: int, m: int) -> list:
        return [j for j in range(m) if Synthesizer.bit(num, j) == 1]

    @staticmethod
    def apply_not(f: list, target: int):
        for idx in range(len(f)):
            f[idx] ^= (1 << target)

    @staticmethod
    def apply_toffoli(f: list, controls: list, target: int):
        for idx in range(len(f)):
            if all(Synthesizer.bit(f[idx], c) == 1 for c in controls):
                f[idx] ^= (1 << target)

    def synthesize(self, permutation: list) -> Circuit:
        f = permutation[:]
        print(f"\nStart: {f}")

        # Step 1: Fix f[0]
        if f[0] != 0:
            bits_to_invert = self.bits_where_1(f[0], self.num_qubits)
            for bitpos in bits_to_invert:
                self.apply_not(f, bitpos)
                reversed_bitpos = self.num_qubits - 1 - bitpos
                self.circuit.add_gate(reversed_bitpos)
                print(f"Apply QNOT on q{reversed_bitpos} -> {f}")

        # Step 2: Fix remaining values
        for i in range(1, 2 ** self.num_qubits - 1):
            if f[i] == i:
                continue

            source = f[i]
            p = [j for j in range(self.num_qubits) if self.bit(i, j) == 1 and self.bit(source, j) == 0]
            q = [j for j in range(self.num_qubits) if self.bit(i, j) == 0 and self.bit(source, j) == 1]

            for j in p:
                controls = [k for k in range(self.num_qubits) if self.bit(i, k) == 1 and k != j]
                self.apply_toffoli(f, controls, j)
                reversed_target = self.num_qubits - 1 - j
                reversed_controls = [self.num_qubits - 1 - k for k in controls]
                self.circuit.add_gate(reversed_target, *reversed_controls)
                gate_name = "CNOT" if len(controls) == 1 else "TOF"
                print(
                    f"Apply {gate_name} target=q{reversed_target} controls={[f'q{c}' for c in reversed_controls]} -> {f}")

            for j in q:
                controls = [k for k in range(self.num_qubits) if self.bit(source, k) == 1 and k != j]
                self.apply_toffoli(f, controls, j)
                reversed_target = self.num_qubits - 1 - j
                reversed_controls = [self.num_qubits - 1 - k for k in controls]
                self.circuit.add_gate(reversed_target, *reversed_controls)
                gate_name = "CNOT" if len(controls) == 1 else "TOF"
                print(
                    f"Apply {gate_name} target=q{reversed_target} controls={[f'q{c}' for c in reversed_controls]} -> {f}")

        return self.circuit
