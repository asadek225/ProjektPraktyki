import argparse
import gzip
import io
import json
import sys
from collections import Counter
from contextlib import redirect_stdout
from typing import Iterable, List, Tuple

import ComparingAlgorithm as al
from TruthTable import TruthTable


# ---------- I/O ----------


def iter_jsonl(path: str) -> Iterable[List[List[int]]]:
    """Zwraca po kolei wpisy (lista wektorów bitowych) z JSONL / JSONL.GZ."""
    open_fn = gzip.open if path.endswith(".gz") else open
    with open_fn(path, "rt", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s:
                yield json.loads(s)


# ---------- Bramki / koszty ----------


def gate_label(qubits: Tuple[int, ...]) -> str:
    """Nazwa bramki wg liczby qubitów w krotce."""
    t = len(qubits)
    return {1: "QNOT", 2: "CNOT", 3: "TOFFOLI"}.get(t, "MCT")


def gate_cost(qubits: Tuple[int, ...]) -> int:
    return 1 if len(qubits) <= 2 else 5


# ---------- Główna pętla ----------


def run_all(
    input_path: str,
    output_path: str,
    stats_path: str,
    suppress_output: bool = True,
    progress_every: int = 1000,
    print_gates: bool = False,
    print_first_n: int = 3,
) -> None:
    """
    Przetwarza wszystkie permutacje z pliku wejściowego:
    - uruchamia al.algorithm,
    - zlicza liczbę bramek i koszt,
    - zapisuje rekordy JSONL i statystyki JSON.
    """

    hist_num_gates = Counter()
    hist_cost = Counter()
    total = 0
    failures = 0
    errors = 0

    open_out = gzip.open if output_path.endswith(".gz") else open
    with open_out(output_path, "wt", encoding="utf-8") as out_f:
        for idx, vectors in enumerate(iter_jsonl(input_path), start=1):
            total = idx
            try:
                # wyznacz n z danych
                if not vectors or not isinstance(vectors[0], list):
                    raise ValueError(f"Wpis {idx}: niepoprawny format (brak listy bitów).")
                n = len(vectors[0])

                # zbuduj TT i uruchom algorytm
                f = TruthTable(n).set_vectors(vectors)
                if suppress_output:
                    with redirect_stdout(io.StringIO()):
                        cir = al.algorithm(f, verbose=False)
                else:
                    cir = al.algorithm(f, verbose=True)

                # weryfikacja — po algorithm f powinno być ideałem
                ideal = TruthTable(n)
                is_ok = f.get_vectors() == ideal.get_vectors()
                if not is_ok:
                    failures += 1

                instr = [tuple(g.qubits) for g in cir.instructions]
                num_gates = len(cir.instructions)
                instr_names = [gate_label(t) for t in instr]
                circuit_cost = sum(gate_cost(t) for t in instr)

                # histogramy
                hist_num_gates.update([num_gates])
                hist_cost.update([circuit_cost])

                # podgląd pierwszych obwodów
                if print_gates and idx <= print_first_n:
                    print(
                        f"perm {idx}: n={n}, ok={is_ok}, "
                        f"{num_gates} bramek, koszt={circuit_cost} -> {' '.join(instr_names)}"
                    )

                # zapis JSONL
                record = {
                    "perm_idx": idx,
                    "n": n,
                    "ok": is_ok,
                    "num_gates": num_gates,
                    "circuit_cost": circuit_cost,
                    "gates_used": dict(Counter(instr_names)),
                    "instructions": [
                        {"gate": name, "num_args": len(t), "qubits": list(t)}
                        for name, t in zip(instr_names, instr)
                    ],
                    "perm_bits": vectors,
                }
                out_f.write(json.dumps(record, separators=(",", ":")) + "\n")

                if progress_every and idx % progress_every == 0:
                    print(f"Przetworzono {idx} permutacji...")

            except Exception as e:
                errors += 1
                # wpisz do outputu informację o błędzie dla spójności śledzenia
                error_record = {"perm_idx": idx, "error": repr(e)}
                out_f.write(json.dumps(error_record, separators=(",", ":")) + "\n")
                # i kontynuuj

    # statystyki zbiorcze
    def _avg(counter: Counter) -> float:
        total_items = sum(counter.values())
        if total_items == 0:
            return 0.0
        tot = sum(value * count for value, count in counter.items())
        return tot / total_items

    stats = {
        "total_perms": total,
        "failures": failures,  # przypadki, gdzie algorytm nie doprowadził do ideału
        "errors": errors,  # nieoczekiwane wyjątki podczas przetwarzania wpisu
        "hist_num_gates": dict(sorted(hist_num_gates.items())),
        "hist_cost": dict(sorted(hist_cost.items())),
        "avg_num_gates": _avg(hist_num_gates),
        "avg_cost": _avg(hist_cost),
        "min_num_gates": min(hist_num_gates.keys()) if hist_num_gates else None,
        "max_num_gates": max(hist_num_gates.keys()) if hist_num_gates else None,
        "min_cost": min(hist_cost.keys()) if hist_cost else None,
        "max_cost": max(hist_cost.keys()) if hist_cost else None,
    }

    with open(stats_path, "w", encoding="utf-8") as sf:
        json.dump(stats, sf, ensure_ascii=False, indent=2)


# ---------- CLI ----------


def parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Batch-run ComparingAlgorithm on JSONL permutations.")
    p.add_argument(
        "--input",
        default="permutacje_n3.jsonl",
        help="Ścieżka do JSONL/JSONL.GZ z permutacjami (bitlisty).",
    )
    p.add_argument(
        "--output", default="results_n3.jsonl", help="Ścieżka wyjściowa JSONL/JSONL.GZ z wynikami."
    )
    p.add_argument(
        "--stats", default="stats_n3.json", help="Ścieżka wyjściowa JSON ze statystykami."
    )
    p.add_argument(
        "--no-suppress", action="store_true", help="Nie tłum stdout (domyślnie wyciszone)."
    )
    p.add_argument(
        "--progress-every",
        type=int,
        default=1000,
        help="Co ile rekordów wypisać postęp (0 = wyłącz).",
    )
    p.add_argument(
        "--print-gates", action="store_true", help="Wypisz bramki dla pierwszych N permutacji."
    )
    p.add_argument(
        "--print-first-n",
        type=int,
        default=3,
        help="Ile pierwszych permutacji wypisać, jeśli --print-gates.",
    )
    return p.parse_args(argv)


def main(argv: List[str] | None = None) -> None:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    run_all(
        input_path=args.input,
        output_path=args.output,
        stats_path=args.stats,
        suppress_output=not args.no_suppress,
        progress_every=args.progress_every if args.progress_every > 0 else 0,
        print_gates=args.print_gates,
        print_first_n=args.print_first_n,
    )


if __name__ == "__main__":
    main()
