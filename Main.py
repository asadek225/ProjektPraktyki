import gzip, json, io
from collections import Counter
from contextlib import redirect_stdout
from Circuit import Circuit
from TruthTable import TruthTable
import BasicAlgorithm as al

def iter_jsonl(path):
    open_fn = gzip.open if path.endswith(".gz") else open
    with open_fn(path, "rt", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s:
                yield json.loads(s)

def gate_label(t):
    return {1: "QNOT", 2: "CNOT", 3: "TOFFOLI"}.get(len(t), "MCT")

def gate_cost_from_tuple(t):
    return 1 if len(t) <= 2 else 5

def run_all(
    input_path="permutacje_n3.jsonl",
    output_path="results_n3.jsonl",
    stats_path="stats_n3.json",
    suppress_output=True,
    progress_every=1000,
    print_gates=False,
    print_first_n=3
):
    hist_num_gates = Counter()
    hist_cost = Counter()
    total = 0

    open_out = gzip.open if output_path.endswith(".gz") else open
    with open_out(output_path, "wt", encoding="utf-8") as out_f:
        for idx, vectors in enumerate(iter_jsonl(input_path), start=1):
            total = idx
            f = TruthTable(3).set_vectors(vectors)

            if suppress_output:
                with redirect_stdout(io.StringIO()):
                    cir = al.algorithm(f, verbose=False)
            else:
                cir = al.algorithm(f, verbose=True)

            instr = [(gate.qubits[0], *gate.qubits[1:]) for gate in cir.instructions]
            instr_names = [gate_label(t) for t in instr]
            num_gates = len(instr)
            circuit_cost = sum(gate_cost_from_tuple(t) for t in instr)

            hist_num_gates.update([num_gates])
            hist_cost.update([circuit_cost])

            if print_gates and idx <= print_first_n:
                print(f"perm {idx}: {num_gates} bramek, koszt={circuit_cost} -> {' '.join(instr_names)}")

            record = {
                "perm_idx": idx,
                "perm_bits": vectors,
                "num_gates": num_gates,
                "circuit_cost": circuit_cost,
                "gates_used": dict(Counter(instr_names)),
                "instructions": [
                    {"gate": name, "num_args": len(t), "qubits": list(t)}
                    for name, t in zip(instr_names, instr)
                ],
            }
            out_f.write(json.dumps(record, separators=(",", ":")) + "\n")

            if progress_every and idx % progress_every == 0:
                print(f"Przetworzono {idx} permutacji...")

    hist_num_gates_sorted = dict(sorted(hist_num_gates.items()))
    hist_cost_sorted = dict(sorted(hist_cost.items()))
    stats = {
        "total_perms": total,
        "hist_num_gates": hist_num_gates_sorted,
        "hist_cost": hist_cost_sorted,
        "avg_num_gates": (sum(k*v for k, v in hist_num_gates.items()) / total) if total else 0.0,
        "avg_cost": (sum(k*v for k, v in hist_cost.items()) / total) if total else 0.0,
    }
    with open(stats_path, "w", encoding="utf-8") as sf:
        json.dump(stats, sf, ensure_ascii=False, indent=2, sort_keys=False)

def main():
    run_all(
        input_path="permutacje_n3.jsonl",
        output_path="results_n3.jsonl",
        stats_path="stats_n3.json",
        suppress_output=True,
        progress_every=1000,
        print_gates=True,
        print_first_n=3
    )

if __name__ == "__main__":
    main()
