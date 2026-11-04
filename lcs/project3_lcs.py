#Vedangi Priyadarshini

#!/usr/bin/env python3
"""
Programming Project 3 - Longest Common Subsequence

Purpose:
This program reads labeled sequences from input file and compares every unique
pair of sequences in that file. For each pair, it computes the longest common
subsequence using both a dynamic-programming method and a brute-force method.
The program reports the LCS, its length, the number of comparisons, and the
execution time for each method.

Command line format: python project3_lcs.py input_file output_file
"""

import sys
import time

def read_input_file(input_filename):
    """
    Read labeled sequences from the input file.
    Input: input_filename - name of the input text file
    Output: A dictionary whose keys are sequence labels and whose values are
            the corresponding sequence strings.
    Raises: ValueError if the file contains invalid formatting, duplicate
            labels, or fewer than two labeled sequences.
    """
    sequences = {}    #Store each label and sequence together in a dictionary.

    with open(input_filename, "r", encoding="utf-8") as file:   #Open the input file and read it one line at a time.
        for line_number, raw_line in enumerate(file, start=1):
            line = raw_line.strip()                             #Remove leading and trailing whitespace.

            if line == "":                                      #Ignore blank lines so the file can be spaced neatly.
                continue

            if "=" not in line:                                 #Every valid line must contain an equals sign.
                raise ValueError(
                    f"Line {line_number}: missing '=' in input line."
                )

            label, sequence = line.split("=", 1)                #Split once at the equals sign into label and sequence.
            label = label.strip()
            sequence = sequence.strip()

            if label == "":                                     #A sequence label must be present.
                raise ValueError(
                    f"Line {line_number}: missing sequence label."
                )

            if sequence == "":                                  #A sequence value must also be present.
                raise ValueError(
                    f"Line {line_number}: missing sequence value."
                )

            if label in sequences:                              #Duplicate labels are not allowed in one input file.
                raise ValueError(
                    f"Line {line_number}: duplicate label '{label}'."
                )

            sequences[label] = sequence                         #Save the validated label and sequence.

    if len(sequences) < 2:                                      #It requires pairwise comparison, so at least two sequences must exist in the file.
        raise ValueError(
            "Input file must contain at least two labeled sequences."
        )

    return sequences

def generate_pairs(sequences):
    """
    Generate all unique pairwise comparisons from the input sequences.
    Input: sequences - dictionary of labeled sequences
    Output: A list of tuples in the form: (label1, seq1, label2, seq2)
    """
    pairs = []                                                  #This list will hold every unique pair of sequences.
    labels = list(sequences.keys())                             #Convert the dictionary keys to a list so they can be indexed.

    for i in range(len(labels)):                                #Generate each unique pair exactly once.
        for j in range(i + 1, len(labels)):
            label1 = labels[i]
            label2 = labels[j]
            seq1 = sequences[label1]
            seq2 = sequences[label2]

            pairs.append((label1, seq1, label2, seq2))          #Store both labels and both sequences together.

    return pairs

def lcs_dynamic(seq1, seq2):
    """
    Compute the longest common subsequence using dynamic programming.
    Input: seq1 - first sequence string
           seq2 - second sequence string
    Output: A tuple containing: (lcs_string, lcs_length, comparisons)
    The comparison count is based on the number of character comparisons 
    made while filling the dynamic-programming table.
    """
    m = len(seq1)                                               #m and n are the lengths of the two input sequences.
    n = len(seq2)

    comparisons = 0                                             #Count character comparisons used while filling the DP table.

    c = []                                                      #c[i][j] will store the LCS length for the prefixes seq1[0:i] and seq2[0:j].

    for i in range(m + 1):                                      #Build an (m + 1) by (n + 1) table initialized to 0.
        row = []
        for j in range(n + 1):
            row.append(0)
        c.append(row)

    for i in range(1, m + 1):                                   #Fill the table row by row using the LCS recurrence.
        for j in range(1, n + 1):
            comparisons += 1                                    #Count the comparison of the current characters.

            if seq1[i - 1] == seq2[j - 1]:                      #If the current characters match, take the diagonal value and add 1.
                c[i][j] = c[i - 1][j - 1] + 1

            elif c[i - 1][j] >= c[i][j - 1]:                    #Otherwise take the better of the upper and left cells.
                c[i][j] = c[i - 1][j]
            else:
                c[i][j] = c[i][j - 1]

    lcs_characters = []                                         #Reconstruct one actual LCS by tracing backward through the table.
    i = m
    j = n

    while i > 0 and j > 0:                                      #If the current characters match, that character belongs to one LCS.
        if seq1[i - 1] == seq2[j - 1]:
            lcs_characters.append(seq1[i - 1])
            i -= 1
            j -= 1

        elif c[i - 1][j] >= c[i][j - 1]:                        #Otherwise move in the direction of the larger subproblem.
            i -= 1
        else:
            j -= 1

    lcs_characters.reverse()                                    #Characters were collected backward, so reverse them.

    lcs_string = "".join(lcs_characters)                        #Join the character list into one string.

    return lcs_string, len(lcs_string), comparisons

def lcs_bruteforce(seq1, seq2):
    """
    Compute the longest common subsequence using a brute-force approach.
    This method generates subsequences of the shorter string from longest to 
    shortest and checks whether each candidate is a subsequence of the longer string.
    """
    if len(seq1) <= len(seq2):                                  #Work with the shorter string when generating candidates.
        shorter = seq1
        longer = seq2
    else:
        shorter = seq2
        longer = seq1

    total_comparisons = 0                                       #Count total character comparisons made by the brute-force method.

    def is_subsequence(candidate, sequence):
        """
        Check whether candidate is a subsequence of sequence.
        """
        candidate_index = 0                                      #candidate_index tracks progress through the candidate string.

        comparisons = 0                                          #comparisons counts character checks for this one test.

        for character in sequence:                               #Scan through the longer sequence from left to right.
            if candidate_index == len(candidate):                #Stop early if the full candidate was already matched.
                break

            comparisons += 1                                     #Count this character comparison.

            if candidate[candidate_index] == character:          #If the next needed character matches, advance in the candidate subsequence.
                candidate_index += 1

        if candidate_index == len(candidate):                    #If every candidate character was matched in order, then it is a subsequence of the longer sequence.
            return True, comparisons

        return False, comparisons

    def find_lcs_of_length(target_length):
        """
        Search for a common subsequence of a specific target length.
        Output: The first common subsequence found of that length, or None.
        """

        found = None                                              #found will store the first common subsequence discovered.

        def build_subsequence(start_index, current):
            """
            Build subsequences of the shorter string recursively.
            """
            nonlocal found
            nonlocal total_comparisons

            if found is not None:                                  #Stop searching once a valid answer of this length is found.
                return

            if len(current) == target_length:                      #If the candidate reached the target length, test whether it is also a subsequence of the longer string.
                candidate = "".join(current)
                is_common, comparisons = is_subsequence(candidate, longer)
                total_comparisons += comparisons

                if is_common:
                    found = candidate

                return

            remaining_needed = target_length - len(current)        #If there are not enough characters left to complete a candidate of this length, stop this branch.
            remaining_available = len(shorter) - start_index

            if remaining_available < remaining_needed:
                return

            for i in range(start_index, len(shorter)):             #Choose the next character position and continue building.
                current.append(shorter[i])
                build_subsequence(i + 1, current)
                current.pop()

                if found is not None:                              #Stop immediately once a solution is found.
                    return

        build_subsequence(0, [])                                   #Start building candidates from an empty subsequence.
        return found

    for length in range(len(shorter), -1, -1):                     #Search from the maximum possible subsequence length downward.
        result = find_lcs_of_length(length)

        if result is not None:                                     #The first match found this way is a longest common subsequence.
            return result, len(result), total_comparisons

    return "", 0, total_comparisons

def write_output_file(output_filename, input_filename, sequences, pairs):
    """
    Write the program results to the output file.
    """
    with open(output_filename, "w", encoding="utf-8") as outfile:    #Open the output file for writing the full report.
        outfile.write("Vedangi Priyadarshini\n")
        outfile.write("605.620 Project 3 - Longest Common Subsequence\n\n")
        outfile.write("INPUT DATA\n")                                #Write a header showing the input file and sequence count.
        outfile.write("----------------------------------------\n")
        outfile.write(f"Input file: {input_filename}\n")
        outfile.write(f"Number of sequences read: {len(sequences)}\n\n")

        for label in sequences:                                       #List all sequences that were read from the file.
            outfile.write(f"{label} = {sequences[label]}\n")

        outfile.write("\n")
        outfile.write("PAIRWISE COMPARISONS\n")
        outfile.write("----------------------------------------\n")
        outfile.write(f"Number of pairs: {len(pairs)}\n\n")

        for pair in pairs:                                             #Process each unique pair of input sequences.
            label1 = pair[0]
            seq1 = pair[1]
            label2 = pair[2]
            seq2 = pair[3]

            dp_start = time.perf_counter()                             #Run the dynamic-programming method and time it.
            dp_lcs, dp_length, dp_comparisons = lcs_dynamic(seq1, seq2)
            dp_end = time.perf_counter()
            dp_time = dp_end - dp_start

            brute_start = time.perf_counter()                          #Run the brute-force method and time it.
            brute_lcs, brute_length, brute_comparisons = lcs_bruteforce(
                seq1, seq2
            )
            brute_end = time.perf_counter()
            brute_time = brute_end - brute_start

            outfile.write(f"{label1} vs {label2}\n\n")                 #Write the pair label first.
            outfile.write("Dynamic Programming Method\n")              #Write the dynamic-programming results.
            outfile.write(f"LCS: {dp_lcs}\n")
            outfile.write(f"LCS Length: {dp_length}\n")
            outfile.write(f"Comparisons: {dp_comparisons}\n")
            outfile.write(f"Time: {dp_time:.6f} seconds\n\n")

            outfile.write("Brute Force Method\n")                      #Write the brute-force results.
            outfile.write(f"LCS: {brute_lcs}\n")
            outfile.write(f"LCS Length: {brute_length}\n")
            outfile.write(f"Comparisons: {brute_comparisons}\n")
            outfile.write(f"Time: {brute_time:.6f} seconds\n\n")

            outfile.write("----------------------------------------\n\n")  #Separate the current pair from the next pair.


def write_error_file(output_filename, input_filename, message):
    """
    Write input-related error information to the output file.
    """
    with open(output_filename, "w", encoding="utf-8") as outfile:           #Open the output file and write a simple error report.
        outfile.write("Vedangi Priyadarshini\n")
        outfile.write("605.620 Project 3 - Longest Common Subsequence\n\n")
        outfile.write("INPUT DATA\n")
        outfile.write("----------------------------------------\n")
        outfile.write(f"Input file: {input_filename}\n\n")
        outfile.write("ERROR\n")
        outfile.write("----------------------------------------\n")
        outfile.write(message + "\n")

def main():
    """
    Driver function for the LCS project.
    """
    if len(sys.argv) != 3:                                                  #The program requires exactly one input file and one output file.
        raise ValueError(
            "Usage: python project3_lcs.py <input_file> <output_file>"
        )

    input_filename = sys.argv[1]                                            #Read the file names from the command line.
    output_filename = sys.argv[2]

    try:
        sequences = read_input_file(input_filename)                         #Read the sequences from the input file.
        pairs = generate_pairs(sequences)                                   #Generate every unique sequence pair.
        write_output_file(output_filename, input_filename, sequences, pairs)  #Write the full comparison report to the output file.

    except FileNotFoundError:                                               #Write a file-open error to the output file.
        write_error_file(
            output_filename,
            input_filename,
            f"Could not open input file: {input_filename}"
        )

    except ValueError as error:
        write_error_file(output_filename, input_filename, str(error))       #Write any input-format error to the output file.

if __name__ == "__main__":                                                  #Run the main driver.
    main()