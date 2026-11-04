# Algorithms for Bioinformatics

Three algorithms implemented from their recurrences in pure Python, instrumented to count operations, and benchmarked against their theoretical complexity.

The point of each was not to produce a fast implementation — it was to measure where theory and practice diverge, and each one did.

| | Implementation | What the measurement showed |
|:--|:--|:--|
| 1 | [Strassen vs. ordinary matrix multiplication](#1--strassen-vs-ordinary-matrix-multiplication) | Strassen uses fewer multiplications at every size and is **9× slower** anyway |
| 2 | [Fourteen hash table schemes](#2--fourteen-hash-table-schemes) | Collision strategy dominates hash function — the same hash gives the best *and* worst scheme |
| 3 | [LCS: dynamic programming vs. brute force](#3--lcs-dynamic-programming-vs-brute-force) | 484 comparisons vs. 92 million on the same input |

No external dependencies. Python 3 standard library only.

---

## 1 · Strassen vs. ordinary matrix multiplication

Ordinary multiplication is the standard triple loop, Θ(n³). Strassen recurses on quadrants, trading one multiplication for eighteen additions at each level: T(n) = 7T(n/2) + O(n²), giving Θ(n^log₂7) ≈ Θ(n^2.807). Both run on every input and their outputs are compared entry by entry, so the operation counts come from implementations verified to be correct.

```bash
cd strassen
python3 project1_strassen.py --input data/sample_input.txt --output results.txt
```

**Measured** (random integer matrices, seed 7):

| n | Ordinary mults | Strassen mults | Ratio | Ordinary time | Strassen time |
|--:|--:|--:|--:|--:|--:|
| 2 | 8 | 7 | 1.14× | 0.000013 s | 0.000021 s |
| 4 | 64 | 49 | 1.31× | 0.000007 s | 0.000077 s |
| 8 | 512 | 343 | 1.49× | 0.000032 s | 0.000655 s |
| 16 | 4,096 | 2,401 | 1.71× | 0.000235 s | 0.003729 s |
| 32 | 32,768 | 16,807 | 1.95× | 0.001957 s | 0.026377 s |
| 64 | 262,144 | 117,649 | 2.23× | 0.016281 s | 0.195501 s |
| 128 | 2,097,152 | 823,543 | 2.55× | 0.132937 s | 1.519051 s |
| 256 | 16,777,216 | 5,764,801 | 2.91× | 1.138214 s | 10.112339 s |

Counts land exactly on n³ and 7^log₂n, and the ratio widens with n as the asymptotics predict — the theory is confirmed on the axis it makes a claim about.

**Runtime goes the other way.** Strassen is 1.6× slower at n=2 and still 8.9× slower at n=256, with no crossover in sight. Every recursion level allocates ten intermediate sum/difference matrices and seven product matrices, and each addition touches Θ(n²) elements. In Python those allocations cost more than the multiplications they save.

An asymptotic improvement is a claim about operation counts, not about wall time. A hybrid that stops recursing below a cutoff size and finishes with the ordinary method would keep the asymptotic advantage and drop most of the overhead.

*Bioinformatics relevance:* matrix multiplication sits under HMM forward/backward computation, covariance in expression analysis, and the linear algebra behind PCA and other dimensionality reduction.

---

## 2 · Fourteen hash table schemes

Fourteen combinations of hash function, collision resolution, and table layout, measured by comparisons needed to insert every key. Keys are 5-digit strings kept as strings — stored as integers, `00358` and `358` collapse into the same key.

Chaining is implemented **inside** the table using a free-space stack, not with external lists, so all fourteen schemes compete for the same 120 physical slots.

```bash
cd hashing
python3 project2_hashing.py data/input120.txt results.txt
```

**Measured** at 120 keys into 120 slots — load factor 1.0, the worst case for open addressing:

| # | Hash | Collision resolution | Layout | Comparisons |
|--:|:--|:--|:--|--:|
| 14 | Multiplication | Chaining | 120 × 1 | **185** |
| 9 | Division, mod 113 | Chaining | 120 × 1 | 196 |
| 6 | Division, mod 127 | Chaining | 120 × 1 | 199 |
| 3 | Division, mod 120 | Chaining | 120 × 1 | 230 |
| 11 | Division, mod 41 | Quadratic probing | 40 × 3 | 378 |
| 10 | Division, mod 41 | Linear probing | 40 × 3 | 438 |
| 5 | Division, mod 127 | Quadratic probing | 120 × 1 | 621 |
| 2 | Division, mod 120 | Quadratic probing | 120 × 1 | 656 |
| 13 | Multiplication | Quadratic probing | 120 × 1 | 734 |
| 8 | Division, mod 113 | Quadratic probing | 120 × 1 | 760 |
| 1 | Division, mod 120 | Linear probing | 120 × 1 | 813 |
| 4 | Division, mod 127 | Linear probing | 120 × 1 | 829 |
| 7 | Division, mod 113 | Linear probing | 120 × 1 | 898 |
| 12 | Multiplication | Linear probing | 120 × 1 | 1,599 |

**The hash function is not what matters here.** The multiplication hash produces both the best scheme (#14, 185 comparisons) and the worst (#12, 1,599) — an 8.6× spread from changing only the collision strategy. Swapping division for multiplication hashing, on its own, improved nothing reliably.

Three results worth separating:

- **Chaining beats open addressing by 3–8×** at full load. Probing has to walk clusters; chaining follows one pointer per step. It costs more implementation complexity — the free-space stack is the fiddly part — and that is the whole trade.
- **Buckets of 3 cut probing cost roughly in half** (#10, #11 against their single-slot equivalents) without changing total capacity. Three keys share an address before anything probes at all, so clusters never start.
- **Divisor choice barely registers.** Primes 127 and 113 against composite 120 move the result by a few percent, far less than the collision strategy does.

*Bioinformatics relevance:* k-mer counting is hash table insertion at scale. DSK (Rizk et al., 2013) partitions k-mers and loads each partition into a temporary hash table, so insertion cost at high load factor is the operation the whole method rests on.

---

## 3 · LCS: dynamic programming vs. brute force

Longest common subsequence on DNA-like strings, both ways. The DP method fills an (m+1)(n+1) table and traces back for the actual subsequence, Θ(mn). The brute-force method generates subsequences of the shorter string, longest first, and tests each against the longer one — returning on the first hit, which is the generous version of brute force.

Both report the subsequence, its length, comparison count, and runtime, so the two agree on the answer while disagreeing wildly on cost.

```bash
cd lcs
python3 project3_lcs.py data/asymptotic_small.txt results.txt
```

**Measured** on equal-length sequence pairs:

| n | DP comparisons | Brute-force comparisons | DP time | Brute-force time |
|--:|--:|--:|--:|--:|
| 4 | 16 | 60 | < 0.0001 s | 0.000035 s |
| 22 | 484 | 92,274,666 | < 0.001 s | 5.053444 s |

DP tracks n² exactly, as table-filling must. Brute force grows by six orders of magnitude over the same span — at n=22 it does **190,000× more work** for the same answer, and the largest required pair took over a minute.

The space trade is the reverse: DP pays Θ(mn) for the table, brute force stores almost nothing and pays in recomputation instead. Overlapping subproblems are the entire difference, and this is what memoizing them is worth.

*Bioinformatics relevance:* LCS is the structural core of sequence alignment. Needleman–Wunsch and Smith–Waterman are the same prefix-table recurrence with gap penalties and a scoring matrix added. The reason alignment is tractable at all is the reason the right column of this table is not nine digits.

---

## Repository layout

```
strassen/
  project1_strassen.py      ordinary + Strassen, with verification
  data/sample_input.txt     multi-case input, n = 2 to 8
  data/error_input.txt      malformed input, for the error path
hashing/
  project2_hashing.py       14 schemes, in-table chaining
  data/input120.txt         120 keys — load factor 1.0
  data/input12.txt          12 keys — low load
lcs/
  project3_lcs.py           DP + brute force
  data/asymptotic_small.txt labeled sequence pairs
  data/asymptotic_mid.txt
```

Each program validates its input and writes a readable error report rather than raising: malformed matrices, non-power-of-two dimensions, missing `=` separators, duplicate labels, files with too few sequences. The stress-test inputs used for the largest benchmarks are not included here — they run to tens of megabytes.

---

Programming projects 1–3, Algorithms for Bioinformatics, M.S. Bioinformatics, Johns Hopkins University.

Complexity analysis follows Cormen, Leiserson, Rivest & Stein, *Introduction to Algorithms* (4th ed., MIT Press, 2022).
