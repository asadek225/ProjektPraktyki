import itertools
import gates

class TruthTable:
    def __init__(self, num_qubits: int):
        self.vectors = [list(bits) for bits in itertools.product([0, 1], repeat=num_qubits)]

    def get_vectors(self):
        return self.vectors

    def get_single_vector(self, index: int):
        return self.vectors[index]

    def get_vectors_as_ints(self):
        int_states = []
        for vector in self.vectors:
            binary_str = ''.join(map(str, vector))
            int_states.append(int(binary_str, 2))
        return int_states


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
    def __init__(self, num_qubits: int):
        self.num_qubits = num_qubits
        self.circuit = Circuit()
        self.truth_table = TruthTable(num_qubits)
        self.logic_gate = LogicGate(self.truth_table)

    def permutate_vectors(self, permutation: list) -> None:
        # Permutujemy wektory według zadanej permutacji
        original_vectors = self.truth_table.get_vectors()
        permutated = [original_vectors[p] for p in permutation]
        self.truth_table.vectors = permutated

    def apply_not(self, target: int):
        self.logic_gate.apply_gate_to_all(target)

    def apply_toffoli(self, target: int, *controls: int):
        self.logic_gate.apply_gate_to_all(target, *controls)

    def synthesize(self, permutation: list) -> Circuit:
        print("\nPoczątkowa tablica prawdy:")
        print(self.truth_table.get_vectors())

        self.permutate_vectors(permutation)
        print(f"\nPo permutacji: {self.truth_table.vectors}")

        # Krok 1: Napraw pierwszy wektor
        first_vector = self.truth_table.get_single_vector(0)
        for i, bit in enumerate(first_vector):
            if bit == 1:
                self.apply_not(i)
                self.circuit.add_gate(i)
                print(f"Apply QNOT on q{self.num_qubits - 1 - i} -> {self.truth_table.vectors}")

        # Krok 2: Napraw pozostałe wektory (od największego indeksu)
        for i in range(2 ** self.num_qubits - 1, 0, -1):
            target_vector = [int(x) for x in format(i, f'0{self.num_qubits}b')]
            current_vector = self.truth_table.get_single_vector(i)

            if current_vector != target_vector:
                diff_positions = [j for j in range(self.num_qubits) if current_vector[j] != target_vector[j]]
                for target in diff_positions:
                    # Zawsze używamy co najmniej 2 kontroli
                    controls = [k for k in range(self.num_qubits)
                                if k != target and target_vector[k] == 1 and current_vector[k] == 1]

                    # Jeśli mamy tylko jedną kontrolę, dodajemy dodatkową kontrolę z bitem 0
                    if len(controls) == 1:
                        additional_control = next(k for k in range(self.num_qubits)
                                                  if k != target and k != controls[0] and target_vector[k] == 0)
                        controls.append(additional_control)

                    if len(controls) >= 2:
                        self.apply_toffoli(target, *controls[:2])  # używamy tylko pierwszych dwóch kontroli
                        self.circuit.add_gate(target, *controls[:2])
                        print(
                            f"Apply TOF target=q{self.num_qubits - 1 - target} controls=[q{self.num_qubits - 1 - controls[0]}, q{self.num_qubits - 1 - controls[1]}] -> {self.truth_table.vectors}")

        return self.circuit
