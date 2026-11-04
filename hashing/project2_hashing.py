#Vedangi Priyadarshini

#!/usr/bin/env python3
"""
Programming Project 2 - Lab Hashing

Purpose:
This program reads 5-digit keys from input file and executes the 14 
hashing schemes. For each scheme, the program records insertion cost 
statistics and writes a formatted hash table to an output file.
"""

import argparse
import re

def parse_command_line():   # Read input and output file names
    """
    Parse command-line arguments - Stores the input and output file names.
    """
    parser = argparse.ArgumentParser(
        description="Hash 5-digit keys from an input file."
    )
    parser.add_argument("input_file", help="Input file name") # Input file name.
    parser.add_argument("output_file", help="Output file name") # Output file name.
    return parser.parse_args()      # Return the parsed argument object.

def read_keys(input_path):   # Read valid 5-digit keys from the input file
    """
    Args: input_path (str) - Name of the input file.
    Returns: A list of valid keys and a list of ignored nonblank lines.
    """
    keys = []           # Store valid 5-digit keys here.
    ignored_lines = []  # Store nonblank lines that are not valid key lines here.

    with open(input_path, "r", encoding="utf-8") as file:   # Open the input file.
        for lines in file:        # Process the file one line at a time.
            line = lines.strip()  # Remove whitespace/newline characters.
            
            if not line:          # Skip completely blank lines.
                continue

            found_keys = re.findall(r"\b\d{5}\b", line)  # Find every exact 5-digit sequence on the line.

            if found_keys:    # If at least one valid key was found, add all of them.
                keys.extend(found_keys)
            else:             # Otherwise keep the line so it can be reported as ignored.
                ignored_lines.append(line)

    return keys, ignored_lines  # Return both valid keys and ignored lines.

def get_division_home_index(key, divisor, table_size):
    """
    Compute the home index for a division-based hash scheme.
    The raw modulo result is first computed with the required divisor.
    It is then mapped into the physical table range.
    Args: key (str) - 5-digit key as a string.
          divisor (int) - Divisor used in the hash function.
          table_size (int) - Physical size of the table.
    Returns: Home index in the physical table.
    """
    raw_index = int(key) % divisor  # Compute the raw division hash value.
    return raw_index % table_size   # Map the raw value into the actual physical table range.

def get_own_home_index(key, table_size): # Multiplication hash (non-division)
    """
    Compute the home index for the custom multiplication hash scheme.
    """
    a_value = 0.6180339887          # Constant used by the multiplication method.
    key_value = int(key)            # Convert the string key to an integer.
    product = key_value * a_value   # Multiply the key by the constant value
    fractional_part = product - int(product)  # Keep only the fractional part.
    return int(table_size * fractional_part)  # Scale the fractional part into the table range.

def create_table(table_size):   # Make empty table
    """
    Create an empty single-slot hash table.
    Args: table_size (int) - Number of table slots.
    Returns: Table initialized with empty markers.
    """
    return ["----"] * table_size   # Use "----" to represent an empty slot.

def create_chain_table(table_size):   # Make empty chaining table
    """
    Create an empty in-table chaining structure.
    Each slot stores a key and a next reference.
    Args: table_size (int) - Number of table slots.
    Returns: Chaining table with empty key/next fields.
    """
    table = []  # Create the full chaining table as a list of slot records.

    for _ in range(table_size):  # Each slot starts empty and has no next link.
        table.append({"key": "----", "next": -1})

    return table

def create_bucket_table(num_buckets, bucket_size):   # Make empty bucket table
    """
    Create an empty bucketed hash table.
    Args: num_buckets (int): Number of addressable buckets.
          bucket_size (int): Number of slots in each bucket.
    Returns: Bucket table initialized with empty markers.
    """
    table = []   # Outer list stores buckets; inner lists store the slots in each bucket.

    for _ in range(num_buckets):  # Build each bucket one by one.
        bucket = []

        for _ in range(bucket_size): # Fill each bucket with empty markers.
            bucket.append("----")

        table.append(bucket)  # Add the finished bucket to the table.

    return table

def create_free_stack(table_size):   # Stack of free positions
    """
    Create a stack of free positions for in-table chaining.
    Args: table_size (int) - Number of table slots.
    Returns: Stack of free slot indices.
    """
    stack = []  # This stack tracks candidate free positions for overflow storage.

    for index in range(table_size):  # Push every table index onto the stack.
        stack.append(index)

    return stack

def get_free_slot(chain_table, free_stack):   # Get next free slot
    """
    Return the next unused slot for in-table chaining.
    Args: chain_table (list[dict]) - Chaining table.
          free_stack (list[int]) - Stack of candidate free slots.
    Returns: Index of a free slot, or -1 if none remain.
    """
    while len(free_stack) > 0:  # Keep popping indices until a truly empty slot is found.
        index = free_stack.pop()

        if chain_table[index]["key"] == "----":  # A slot is free only if its key field is still empty.
            return index

    return -1  # If no free slot exists, report failure.

def linear_probe_insert(table, key, home_index, stats):  # Linear probing
    """
    Insert a key using linear probing.
    Args: table (list[str]) - Hash table.
          key (str): Key to insert.
          home_index (int): Home address for the key.
          stats (dict): Statistics dictionary for the scheme.
    Returns: True if the key was inserted, False otherwise.
    """
    table_size = len(table)  # Save the table size for modular wraparound.

    for step in range(table_size):  
        index = (home_index + step) % table_size   # Linear probing checks home, home+1, home+2, ...
        stats["comparisons"] += 1   # Each slot inspection counts as one comparison.

        if table[index] == "----":  # If the slot is empty, store the key and stop.
            table[index] = key
            return True

        if step == 0:   # Collision at the home slot counts as primary.
            stats["primary_collisions"] += 1
        else:
            stats["secondary_collisions"] += 1  # Any later occupied probe position counts as secondary.

    stats["keys_not_inserted"].append(key)  # If no empty slot was found, insertion failed.
    return False

def quadratic_probe_insert(table, key, home_index, stats):  # Quadratic probing
    """
    Insert a key using quadratic probing.
    The quadratic offset used is i(i+1)/2, which matches the
    c1 = c2 = 0.5 requirement.
    """
    table_size = len(table)

    for step in range(table_size):
        offset = (step * (step + 1)) // 2   # Offset sequence: 0, 1, 3, 6, 10, ...
        index = (home_index + offset) % table_size   # Probe the home slot plus the quadratic offset.
        stats["comparisons"] += 1

        if table[index] == "----":
            table[index] = key
            return True

        if step == 0:
            stats["primary_collisions"] += 1
        else:
            stats["secondary_collisions"] += 1

    stats["keys_not_inserted"].append(key)
    return False

def bucket_has_space(bucket):   # Check if bucket has open slot
    """
    Check whether a bucket still has an empty slot.
    Args: bucket (list[str]): One bucket from a bucketed table.
    Returns: True if an empty slot exists, False otherwise.
    """
    for item in bucket:  # Scan the bucket for any open slot.
        if item == "----":
            return True
        
    return False

def insert_into_bucket(bucket, key):   # Put key in first empty slot
    """
    Insert a key into the first open slot in a bucket.
    """
    for i in range(len(bucket)):  # Store the key in the first empty position within the bucket.
        if bucket[i] == "----":
            bucket[i] = key
            return True

    return False

def linear_bucket_insert(bucket_table, key, home_bucket, stats):  # Linear probing across buckets
    """
    Insert a key into a bucket-size-3 table using linear probing.
    Probing moves across addressable buckets, not across internal
    bucket slots.
    """
    num_buckets = len(bucket_table)  # Number of addressable buckets.

    for step in range(num_buckets):  # Probe across buckets in linear order.
        bucket_index = (home_bucket + step) % num_buckets
        stats["comparisons"] += 1  # One comparison is counted for each bucket checked.

        if bucket_has_space(bucket_table[bucket_index]):  # If the bucket has space, insert into its first empty slot.
            insert_into_bucket(bucket_table[bucket_index], key)
            return True

        if step == 0:  # Collision at the home bucket counts as primary.
            stats["primary_collisions"] += 1
        else:
            stats["secondary_collisions"] += 1  # Later occupied buckets count as secondary.

    stats["keys_not_inserted"].append(key) # If no bucket could accept the key, insertion failed.
    return False

def quadratic_bucket_insert(bucket_table, key, home_bucket, stats): # Quadratic probing across buckets
    """
    Insert a key into a bucket-size-3 table using quadratic probing.
    """
    num_buckets = len(bucket_table)

    for step in range(num_buckets):  # Probe across buckets using quadratic offsets.
        offset = (step * (step + 1)) // 2
        bucket_index = (home_bucket + offset) % num_buckets
        stats["comparisons"] += 1

        if bucket_has_space(bucket_table[bucket_index]):
            insert_into_bucket(bucket_table[bucket_index], key)
            return True

        if step == 0:
            stats["primary_collisions"] += 1
        else:
            stats["secondary_collisions"] += 1

    stats["keys_not_inserted"].append(key)
    return False

def find_chain_end(chain_table, start_index, stats):   # Find last node
    """
    Follow links until the last node in a chain is found.
    Args: chain_table (list[dict]) - Chaining table.
          start_index (int) - Starting slot of the chain.
    Returns: Index of the last node in the chain.
    """
    current = start_index  # Start at the home slot of the chain.

    while chain_table[current]["next"] != -1:  # Follow next links until the final node is reached.
        current = chain_table[current]["next"]
        stats["comparisons"] += 1           # Each link traversal counts as another comparison.
        stats["secondary_collisions"] += 1  # Moving deeper into the chain counts as a secondary collision.

    return current

def find_previous_link(chain_table, home_index, target_index, stats):  # Find node whose next points to target_index
    """
    Find the node whose next reference points to a target slot.
    Args: target_index (int) - Target slot whose predecessor is needed.
    Returns: Index of the predecessor node.
    """
    current = home_index   # Begin at the home slot of the chain.

    while chain_table[current]["next"] != target_index:  # Follow the chain until a node points to the target slot.
        current = chain_table[current]["next"]
        stats["comparisons"] += 1

    return current

def chain_insert(chain_table, free_stack, key, home_index, stats, home_func): # Insert with chaining inside the table
    """
    Insert a key using in-table chaining with a free-space stack.
    If the home slot is occupied by a key that belongs elsewhere,
    that displaced key is moved and the original chain is repaired.
    Args: chain_table (list[dict]) - Chaining table.
          free_stack (list[int]) - Stack of free slots.
          key (str) - Key to insert.
          home_index (int) - Home slot for the new key.
          stats (dict) - Statistics dictionary for the scheme.
          home_func (callable) - Function used to recompute a key's home slot.
    Returns: True if insertion succeeds, False otherwise.
    """
    stats["comparisons"] += 1   # Checking the home slot counts as one comparison.

    if chain_table[home_index]["key"] == "----":  # If the home slot is empty, place the key there immediately.
        chain_table[home_index]["key"] = key
        chain_table[home_index]["next"] = -1
        return True

    stats["primary_collisions"] += 1   # Occupied home slot means a primary collision.

    current_key = chain_table[home_index]["key"]   # Get the key currently stored at the home slot.
    current_key_home = home_func(current_key, len(chain_table))  # Determine where that current key truly belongs.

    if current_key_home == home_index:   # If the existing key belongs here, append the new key to the chain.
        end_index = find_chain_end(chain_table, home_index, stats)
        free_index = get_free_slot(chain_table, free_stack)

        if free_index == -1:   # If no free space remains, insertion fails.
            stats["keys_not_inserted"].append(key)
            return False

        stats["comparisons"] += 1   # Using the overflow slot counts as another comparison.
        chain_table[free_index]["key"] = key   # Store the new key in the overflow slot.
        chain_table[free_index]["next"] = -1
        chain_table[end_index]["next"] = free_index   # Extend the chain to the new slot.
        return True

    free_index = get_free_slot(chain_table, free_stack)   # Otherwise, the key occupying the home slot does not belong there.

    if free_index == -1:   # If no free space remains, insertion fails.
        stats["keys_not_inserted"].append(key)
        return False

    previous_index = find_previous_link(   # Find the node whose link points to the displaced slot.
        chain_table,
        current_key_home,
        home_index,
        stats
    )

    chain_table[free_index]["key"] = chain_table[home_index]["key"]   # Move the displaced key and its link to a free slot.
    chain_table[free_index]["next"] = chain_table[home_index]["next"]
    chain_table[previous_index]["next"] = free_index   # Repair the earlier link so the chain still works.

    chain_table[home_index]["key"] = key   # Put the new key into its correct home slot.
    chain_table[home_index]["next"] = -1
    stats["comparisons"] += 1   # Count the relocation/placement work as another comparison.

    return True

def make_stats():    # Create stats dictionary
    """
    Create and initialize a statistics dictionary for one scheme.
    Returns: Statistics structure used during insertion.
    """
    return {
        "comparisons": 0,
        "primary_collisions": 0,
        "secondary_collisions": 0,
        "keys_not_inserted": []
    }

def finish_stats_open(table, stats):   # Final stats for normal table
    """
    Finalize statistics for a single-slot open-addressing table.
    Args: table - Final hash table.
          stats (dict): Statistics dictionary to update.
    """
    stats["total_collisions"] = (   # Total collisions are the sum of primary and secondary collisions.
        stats["primary_collisions"] + stats["secondary_collisions"]
    )
    stats["records_inserted"] = len(table) - table.count("----")    # Count inserted records by subtracting empty slots.
    stats["load_factor"] = stats["records_inserted"] / len(table)   # Load factor is inserted records divided by table size.

def finish_stats_chain(chain_table, stats):   # Final stats for chain table
    """
    Finalize statistics for an in-table chaining scheme.
    Args: chain_table (list[dict]): Final chaining table.
          stats (dict): Statistics dictionary to update.
    """
    inserted = 0

    for slot in chain_table:   # Count every nonempty chaining slot.
        if slot["key"] != "----":
            inserted += 1

    stats["total_collisions"] = (   # Store final totals.
        stats["primary_collisions"] + stats["secondary_collisions"]
    )
    stats["records_inserted"] = inserted
    stats["load_factor"] = inserted / len(chain_table)

def finish_stats_bucket(bucket_table, bucket_size, stats):  # Final stats for bucket table
    """
    Finalize statistics for a bucket-size-3 scheme.
    Args: bucket_table - Final bucketed table.
          bucket_size - Number of slots per bucket.
          stats (dict) - Statistics dictionary to update.
    """
    inserted = 0

    for bucket in bucket_table:   # Count every nonempty slot across all buckets.
        for item in bucket:
            if item != "----":
                inserted += 1

    stats["total_collisions"] = (
        stats["primary_collisions"] + stats["secondary_collisions"]
    )                            
    stats["records_inserted"] = inserted
    stats["load_factor"] = inserted / (len(bucket_table) * bucket_size)

def run_open_division_scheme(keys, divisor, method):   # Linear or quadratic
    """
    Run a single-slot division-hashing scheme with probing.
    Returns: Final table and statistics.
    """
    table_size = 120
    table = create_table(table_size)
    stats = make_stats()

    for key in keys:  # Insert every key using the requested probing method.
        home_index = get_division_home_index(key, divisor, table_size)

        if method == "linear":
            linear_probe_insert(table, key, home_index, stats)
        else:
            quadratic_probe_insert(table, key, home_index, stats)

    finish_stats_open(table, stats)  # Finalize and return results for this scheme.
    return table, stats

def run_chain_division_scheme(keys, divisor):   # Chaining scheme
    """
    Run a division-hashing scheme that uses in-table chaining.
    Returns:Final chaining table and statistics.
    """
    table_size = 120
    chain_table = create_chain_table(table_size)
    free_stack = create_free_stack(table_size)
    stats = make_stats()

    def division_home_func(current_key, current_table_size): # Home-function wrapper used by chain_insert for this divisor.
        return get_division_home_index(
            current_key,
            divisor,
            current_table_size
        )

    for key in keys:
        home_index = get_division_home_index(key, divisor, table_size)
        chain_insert(
            chain_table,
            free_stack,
            key,
            home_index,
            stats,
            division_home_func
        )

    finish_stats_chain(chain_table, stats)
    return chain_table, stats

def run_bucket_division_scheme(keys, divisor, method): # Bucket size 3 schemes
    """
    Run a bucket-size-3 division-hashing scheme.
    Returns: Final bucket table and statistics.
    """
    num_buckets = 40
    bucket_size = 3
    bucket_table = create_bucket_table(num_buckets, bucket_size)
    stats = make_stats()

    for key in keys: 
        home_bucket = get_division_home_index(key, divisor, num_buckets)

        if method == "linear":
            linear_bucket_insert(bucket_table, key, home_bucket, stats)
        else:
            quadratic_bucket_insert(bucket_table, key, home_bucket, stats)

    finish_stats_bucket(bucket_table, bucket_size, stats) 
    return bucket_table, stats

def run_open_own_scheme(keys, method):  # Multiplication hash with linear or quadratic probing
    """
    Run the multiplication-hash scheme with probing.
    Returns: Final table and statistics.
    """
    table_size = 120
    table = create_table(table_size)
    stats = make_stats()

    for key in keys:  # Insert every key using the custom multiplication hash.
        home_index = get_own_home_index(key, table_size)

        if method == "linear":
            linear_probe_insert(table, key, home_index, stats)
        else:
            quadratic_probe_insert(table, key, home_index, stats)

    finish_stats_open(table, stats) 
    return table, stats

def run_chain_own_scheme(keys): 
    """
    Run the multiplication-hash scheme with in-table chaining.
    Returns: Final chaining table and statistics.
    """
    table_size = 120
    chain_table = create_chain_table(table_size)
    free_stack = create_free_stack(table_size)
    stats = make_stats()

    def own_home_func(current_key, current_table_size):  # Home-function wrapper used by chain_insert for custom hashing.
        return get_own_home_index(current_key, current_table_size)

    for key in keys: 
        home_index = get_own_home_index(key, table_size)
        chain_insert(
            chain_table,
            free_stack,
            key,
            home_index,
            stats,
            own_home_func
        )

    finish_stats_chain(chain_table, stats) 
    return chain_table, stats

def format_keys_five_across(keys):   # Print keys 5 across
    """
    Format input keys five across for readable output.
    """
    lines = []

    for index in range(0, len(keys), 5):  # Group the keys in blocks of five per line.
        group = keys[index:index + 5]
        lines.append(" ".join(group))

    return "\n".join(lines)

def format_table_five_across(table):   # Print normal table 5 across
    """
    Format a single-slot table five entries across.
    """
    lines = []

    for index in range(0, len(table), 5): # Format 24 lines of 5 entries each for a 120-slot table.
        group = table[index:index + 5]
        row = []

        for item in group:
            row.append(f"{item:<5}")

        lines.append(" ".join(row))

    return "\n".join(lines)

def format_chain_table_five_across(chain_table):   # Print chain table 5 across
    """
    Format a chaining table five entries across using stored keys only.
    """
    lines = []

    for index in range(0, len(chain_table), 5):  # Only print stored keys, not the internal next links.
        group = chain_table[index:index + 5]
        row = []

        for slot in group:
            row.append(f"{slot['key']:<5}")

        lines.append(" ".join(row))

    return "\n".join(lines)

def format_bucket_table(bucket_table):   # Print 40 buckets, one per line
    """
    Format a bucket-size-3 table one bucket per line.
    """
    lines = []

    for i in range(len(bucket_table)): # Each line shows one bucket number and its three slots.
        bucket = bucket_table[i]
        line = (
            f"{i + 1:>2} "
            f"{bucket[0]:<5} "
            f"{bucket[1]:<5} "
            f"{bucket[2]:<5}"
        )
        lines.append(line)

    return "\n".join(lines)


def write_divider(outfile):
    """
    Write a separator line between scheme outputs.
    """
    outfile.write("-" * 60 + "\n")

def write_scheme_output(outfile, scheme_title, formatted_table, stats):
    """
    Write one scheme's statistics and formatted table to the output file.
    Args: outfile - Open output file handle.
          scheme_title (str) - Display title for the scheme.
          formatted_table (str) - Already formatted table text.
          stats (dict) - Statistics for the scheme.
    """
    write_divider(outfile)               # Separate this scheme from the previous one.
    outfile.write(scheme_title + "\n")   # Print the scheme title and statistics.
    outfile.write("Primary collisions: " +
                  str(stats["primary_collisions"]) + "\n")
    outfile.write("Secondary collisions: " +
                  str(stats["secondary_collisions"]) + "\n")
    outfile.write("Total collisions: " +
                  str(stats["total_collisions"]) + "\n")
    outfile.write("Comparisons: " +
                  str(stats["comparisons"]) + "\n")

    if len(stats["keys_not_inserted"]) == 0:  # Report whether any items failed to insert.
        outfile.write("Items unable to be stored: 0\n")
    else:
        outfile.write("Items unable to be stored: " +
                      str(len(stats["keys_not_inserted"])) + "\n")
        outfile.write("Keys not inserted: " +
                      str(stats["keys_not_inserted"]) + "\n")

    outfile.write("Load factor: " +
                  str(stats["load_factor"]) + "\n")  # Print load factor and final table.
    outfile.write("\nResulting hash table:\n")
    outfile.write(formatted_table + "\n\n")

def write_output(output_path, input_path, keys, ignored_lines, results):
    """
    Write the full project output for all schemes.
    Args: results (list[tuple]) - Scheme titles, types, tables, and stats.
    """
    with open(output_path, "w", encoding="utf-8") as outfile:  # Open the output file and write the summary section first.
        outfile.write("Vedangi Priyadarshini\n")
        outfile.write("605.620 Algorithms for Bioinformatics\n")
        outfile.write("Project 2 - Hashing Results\n")
        outfile.write("=" * 50 + "\n")
        outfile.write("Input file: " + input_path + "\n")
        outfile.write("Number of valid 5-digit keys read: " +
                      str(len(keys)) + "\n")
        outfile.write("Number of ignored nonblank lines: " +
                      str(len(ignored_lines)) + "\n\n")

        outfile.write("Input keys:\n")  # Print the valid keys that were read.
        if keys:
            outfile.write(format_keys_five_across(keys) + "\n")
        else:
            outfile.write("No valid keys found.\n")

        outfile.write("\nIgnored lines:\n")  # Print ignored lines
        if ignored_lines:
            for line in ignored_lines:
                outfile.write(line + "\n")
        else:
            outfile.write("None\n")

        outfile.write("\n")

        for scheme_title, scheme_type, table, stats in results:  # Format and write each scheme's results.
            if scheme_type == "chain":
                formatted_table = format_chain_table_five_across(table)
            elif scheme_type == "bucket":
                formatted_table = format_bucket_table(table)
            else:
                formatted_table = format_table_five_across(table)

            write_scheme_output(outfile, scheme_title, formatted_table, stats)

def main():
    """
    Driver for the hashing project.
    Reads the input file, runs all required schemes, and writes the
    formatted results to the output file.
    """
    args = parse_command_line()    # Get file names from the command line.
    keys, ignored_lines = read_keys(args.input_file)  # Read valid keys and ignored text lines from the input file.

    scheme_specs = [      # Each tuple defines one scheme
        ("Scheme 1: Division Hash, Linear Probing, Mod 120, Bucket Size 1",
         "open", run_open_division_scheme, (120, "linear")),
        ("Scheme 2: Division Hash, Quadratic Probing, Mod 120, Bucket Size 1",
         "open", run_open_division_scheme, (120, "quadratic")),
        ("Scheme 3: Division Hash, Chaining, Mod 120, Bucket Size 1",
         "chain", run_chain_division_scheme, (120,)),
        ("Scheme 4: Division Hash, Linear Probing, Mod 127, Bucket Size 1",
         "open", run_open_division_scheme, (127, "linear")),
        ("Scheme 5: Division Hash, Quadratic Probing, Mod 127, Bucket Size 1",
         "open", run_open_division_scheme, (127, "quadratic")),
        ("Scheme 6: Division Hash, Chaining, Mod 127, Bucket Size 1",
         "chain", run_chain_division_scheme, (127,)),
        ("Scheme 7: Division Hash, Linear Probing, Mod 113, Bucket Size 1",
         "open", run_open_division_scheme, (113, "linear")),
        ("Scheme 8: Division Hash, Quadratic Probing, Mod 113, Bucket Size 1",
         "open", run_open_division_scheme, (113, "quadratic")),
        ("Scheme 9: Division Hash, Chaining, Mod 113, Bucket Size 1",
         "chain", run_chain_division_scheme, (113,)),
        ("Scheme 10: Division Hash, Linear Probing, Mod 41, Bucket Size 3",
         "bucket", run_bucket_division_scheme, (41, "linear")),
        ("Scheme 11: Division Hash, Quadratic Probing, Mod 41, Bucket Size 3",
         "bucket", run_bucket_division_scheme, (41, "quadratic")),
        ("Scheme 12: Multiplication Hash, Linear Probing, Bucket Size 1",
         "open", run_open_own_scheme, ("linear",)),
        ("Scheme 13: Multiplication Hash, Quadratic Probing, Bucket Size 1",
         "open", run_open_own_scheme, ("quadratic",)),
        ("Scheme 14: Multiplication Hash, Chaining, Bucket Size 1",
         "chain", run_chain_own_scheme, ())
    ]

    results = []   # Collect the final table and statistics for each scheme here.

    for scheme_title, scheme_type, run_function, extra_args in scheme_specs:   # Execute every required scheme in order.
        table, stats = run_function(keys, *extra_args)
        results.append((scheme_title, scheme_type, table, stats))

    write_output(    # Write the complete results file.
        args.output_file,
        args.input_file,
        keys,
        ignored_lines,
        results
    )

if __name__ == "__main__":
    main()