#Vedangi Priyadarshini

#!/usr/bin/env python3
"""
Programming Project 1 - Ordinary vs. Strassen Matrix Multiplication

Purpose:
This program reads one or more test cases from an input text file. Each test case 
contains: An integer n (matrix dimension), where n is a power of two; n rows for 
matrix A; n rows for matrix B. For each case, the program computes products using 
ordinary multiplication and Strassen's algorithm, counts scalar multiplications, 
measures runtime, and writes results to an output file.
"""

import argparse
import time

def is_power_of_two(n):              # Strassen splits matrices in half repeatedly, so n must be 2^k
    """
    Check whether n is a positive power of two.
    Input: n - integer   Output: True if n is a power of two and n > 0, else False
    """
    return n > 0 and (n & (n - 1)) == 0  # Powers of two have exactly one 1-bit in binary 


def format_matrix(M):
    """
    Convert a matrix to a printable multi-line string.
    Input: M - list of lists of integers (matrix)
    Output: String where each row is space-separated on its own line
    """                   
    text = ""
    for row in M:                   # Make each row as space-separated values for readable output files.
        line = ""
        for x in row:
            line = line + str(x) + " "
        text = text + line.strip() + "\n"
    return text.strip()


def parse_cases(filename):          # Load the input file, validate formatting, and return a list of (n, A, B).
    """
    Parse all matrix test cases from an input file.
    Input: filename - path to the input file
    Output:(cases, error_message)
            cases: list of tuples (n, A, B) if parsing succeeds
            error_message: None if OK, otherwise a descriptive error string
    """
    with open(filename, "r") as file:
        lines = []
        for line in file:            # Parse multiple cases: n, then n rows of A, then n rows of B, blanks allowed.
            lines.append(line.strip())  # strip for easy blank checks

    cases = []
    i = 0

    while i < len(lines):
        while i < len(lines) and lines[i] == "":   # skip blank lines between cases
            i += 1
        if i >= len(lines):
            break

        n_text = lines[i]          # read n
        if not n_text.isdigit():
            return None, "Error: expected an integer n on line " + str(i + 1)

        n = int(n_text)
        if not is_power_of_two(n):
            return None, "Error: n must be a power of 2 on line " + str(i + 1)

        i += 1

        A = []                       # read Matrix A
        for r in range(1, n + 1):
            if i >= len(lines) or lines[i] == "":
                return None, "Error: missing row " + str(r) + " of A"

            parts = lines[i].split()
            if len(parts) != n:
                return None, ("Error: A row " + str(r) + " must have " + str(n) +
                              " values (line " + str(i + 1) + ")")

            row = []
            for x in parts:
                if not x.lstrip("-").isdigit():
                    return None, ("Error: non-integer in A row " + str(r) +
                                  " (line " + str(i + 1) + ")")
                row.append(int(x))

            A.append(row)
            i += 1

        B = []                       # read Matrix B
        for r in range(1, n + 1):
            if i >= len(lines) or lines[i] == "":
                return None, "Error: missing row " + str(r) + " of B"

            parts = lines[i].split()
            if len(parts) != n:
                return None, ("Error: B row " + str(r) + " must have " + str(n) +
                              " values (line " + str(i + 1) + ")")

            row = []
            for x in parts:
                if not x.lstrip("-").isdigit():
                    return None, ("Error: non-integer in B row " + str(r) +
                                  " (line " + str(i + 1) + ")")
                row.append(int(x))

            B.append(row)
            i += 1

        cases.append((n, A, B))     # store one complete validated test case

    return cases, None


def add_matrix(X, Y):          # Sum used by Strassen to build intermediate S matrices.
    """
    Compute element-wise addition Z = X + Y
    Inputs: X, Y - same-dimension square matrices
    Output: Z - element-wise sum matrix with Z[i][j] = X[i][j] + Y[i][j]
    """
    n = len(X)
    Z = []
    for i in range(n):
        row = []
        for j in range(n):
            row.append(X[i][j] + Y[i][j])
        Z.append(row)
    return Z


def sub_matrix(X, Y):          # Difference used by Strassen to build intermediate S matrices.
    """
    Compute element-wise subtraction Z = X - Y
    Inputs: X, Y - same-dimension square matrices
    Output: Z - element-wise difference matrix with Z[i][j] = X[i][j] - Y[i][j]
    """
    n = len(X)
    Z = []
    for i in range(n):
        row = []
        for j in range(n):
            row.append(X[i][j] - Y[i][j])
        Z.append(row)
    return Z


def split_quadrants(M):        # Split matrix into four quadrants so Strassen can recurse on half-size blocks.
    """
    Split an n x n matrix into four (n/2) x (n/2) quadrants.
    Input: M - square matrix where n is even
    Output: (M11, M12, M21, M22) quadrants as new matrices
    """
    n = len(M)
    mid = n // 2

    M11 = []
    M12 = []
    M21 = []
    M22 = []

    for i in range(mid):
        M11.append(M[i][0:mid])    # top-left of matrix
        M12.append(M[i][mid:n])    # top-right of matrix

    for i in range(mid, n):
        M21.append(M[i][0:mid])    # bottom-left of matrix
        M22.append(M[i][mid:n])    # bottom-right of matrix

    return M11, M12, M21, M22


def combine_quadrants(C11, C12, C21, C22):  # Rebuild a full matrix after computing the four result quadrants
    """
    Combine four quadrants into one full matrix.
    Inputs: C11, C12, C21, C22 - (n/2) x (n/2) matrices
    Output: C - n x n combined matrix
    """
    mid = len(C11)
    C = []
    for i in range(mid):
        C.append(C11[i] + C12[i])   # stitch top row blocks
    for i in range(mid):
        C.append(C21[i] + C22[i])   # stitch bottom row blocks
    return C


def ordinary_multiply(A, B):       # Ordinary O(n^3) multiplication; counts scalar multiplications for comparison.
    """
    Multiply matrices using the standard O(n^3) triple-loop algorithm.
    Inputs: A, B - n x n integer matrices
    Output:(C, mult_count)
            C: product matrix
            mult_count: number of scalar multiplications performed (n^3)
    """
    n = len(A)

    C = []                         # Initialize output matrix with zeros
    for i in range(n):
        row = []
        for j in range(n):
            row.append(0)
        C.append(row)

    mult_count = 0

    for i in range(n):
        for j in range(n):
            total = 0                # accumulate dot product for C[i][j]
            for k in range(n):
                total = total + (A[i][k] * B[k][j])
                mult_count += 1       # count each scalar multiply A[i][k]*B[k][j]
            C[i][j] = total

    return C, mult_count


def strassen_multiply(A, B):       # Strassen recursion: reduces multiplications at the cost of extra additions.
    """
    Multiply matrices using Strassen's recursive algorithm.
    Inputs: A, B - n x n integer matrices where n is a power of two
    Output: (C, mult_count)
            C: product matrix
            mult_count: counts only base-case scalar multiplications (n == 1)
    - Uses 7 recursive multiplications (P1..P7) per level.
    - Uses matrix adds/subtracts (S1..S10) to reduce multiplications.
    """
    n = len(A)

    if n == 1:
        return [[A[0][0] * B[0][0]]], 1      # base case: exactly one multiply

    # Split A and B into quadrants.
    A11, A12, A21, A22 = split_quadrants(A)
    B11, B12, B21, B22 = split_quadrants(B)

    # S1..S10 are chosen to enable 7 multiplications (P1..P7) instead of 8.
    S1 = sub_matrix(B12, B22)
    S2 = add_matrix(A11, A12)
    S3 = add_matrix(A21, A22)
    S4 = sub_matrix(B21, B11)
    S5 = add_matrix(A11, A22)
    S6 = add_matrix(B11, B22)
    S7 = sub_matrix(A12, A22)
    S8 = add_matrix(B21, B22)
    S9 = sub_matrix(A11, A21)
    S10 = add_matrix(B11, B12)

    # P1..P7 are the only recursive multiplications
    P1, c1 = strassen_multiply(A11, S1)
    P2, c2 = strassen_multiply(S2, B22)
    P3, c3 = strassen_multiply(S3, B11)
    P4, c4 = strassen_multiply(A22, S4)
    P5, c5 = strassen_multiply(S5, S6)
    P6, c6 = strassen_multiply(S7, S8)
    P7, c7 = strassen_multiply(S9, S10)

    mult_count = c1 + c2 + c3 + c4 + c5 + c6 + c7       # total scalar multiplications

    # Combine P products into the four result quadrants
    C11 = add_matrix(sub_matrix(add_matrix(P5, P4), P2), P6)
    C12 = add_matrix(P1, P2)
    C21 = add_matrix(P3, P4)
    C22 = sub_matrix(sub_matrix(add_matrix(P5, P1), P3), P7)

    C = combine_quadrants(C11, C12, C21, C22)
    return C, mult_count


def main():                       # Driver: parse args, load cases, run both algorithms, and write report output.
    """
    Driver for the program.
    - Read command-line arguments for input/output filenames.
    - Parse all matrix cases from the input file.
    - For each case, run both multiplication methods, measure runtime, 
      and record multiplication counts.
    - Write a readable report to the output file.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Input file name")
    parser.add_argument("--output", required=True, help="Output file name")
    args = parser.parse_args()

    cases, err = parse_cases(args.input)
    if err is not None:
        print(err)                # immediate feedback if run interactively
        with open(args.output, "w") as out:
            out.write("Input file: " + args.input + "\n\n")
            out.write(err + "\n")
        return

    with open(args.output, "w") as out:
        out.write("Input file: " + args.input + "\n\n")

        for (n, A, B) in cases:
            out.write("n = " + str(n) + "\n\n")

            out.write("Matrix A:\n")
            out.write(format_matrix(A) + "\n\n")

            out.write("Matrix B:\n")
            out.write(format_matrix(B) + "\n\n")

            # Measure ordinary multiplication runtime for this case.
            start = time.perf_counter()
            C_ord, mults_ord = ordinary_multiply(A, B)
            end = time.perf_counter()
            t_ord = end - start

            # Measure Strassen multiplication runtime for this case.
            start = time.perf_counter()
            C_str, mults_str = strassen_multiply(A, B)
            end = time.perf_counter()
            t_str = end - start

            out.write("Ordinary Result:\n")
            out.write(format_matrix(C_ord) + "\n\n")
            out.write("Ordinary multiplications: " + str(mults_ord) + "\n")
            out.write("Ordinary time (sec): " + str(t_ord) + "\n\n")

            out.write("Strassen Result:\n")
            out.write(format_matrix(C_str) + "\n\n")
            out.write("Strassen multiplications: " + str(mults_str) + "\n")
            out.write("Strassen time (sec): " + str(t_str) + "\n\n")

            match = (C_ord == C_str)   # Equality check ensures both algorithms produce identical integers.
            out.write("Results match: " + ("YES" if match else "NO") + "\n\n")


if __name__ == "__main__":
    main()
