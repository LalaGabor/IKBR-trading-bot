# Def Tests
"""
Test 1: rsi calculator module: test_append_rsi_to_dataframe.
-- Assert that the close column is type float

-- Implementation: ingest large sample dataframe. Assert dataframe['Closes'].type() = float

-- Status: Open

Test 2: divergence calculator module: test_get_open_candidate.
-- Test preparation. Find a row number in the sample big dataframe that fulfills the logical checks in the
conditional of get_open_candidate

-- Assert that is_divergence_open_candidate at row_number == 1

-- Implementation: ingest large sample dataframe. Make assertion using expected row number(s)

-- Status: Open

Test 3: divergence calculator module: test_get_close_candidates_nearest_open.
-- Test preparation. Find a row(s) number in the sample big dataframe where is_divergence_open_candidate == 1

-- Assert that the values in paired_divergence_opens_id & paired_divergence_opens_closing_price of rows where
is_divergence_open_candidate == 1, match the paired divergence open row

-- Implementation: ingest large sample dataframe. Make assertion using expected row number(s)

-- Status: Open

Test 4: divergence calculator module: test_limit_divergence_to_accepted_row.
-- Test preparation. Find a row(s) number in the sample big dataframe where is_divergence_open_candidate == 1

-- Assert that the values in paired_divergence_opens_id & paired_divergence_opens_closing_price of rows where
is_divergence_open_candidate == 1, match the paired divergence open row

-- Implementation: ingest large sample dataframe. Make assertion using expected row number(s)

-- Status: Open

Test 5: divergence calculator module: test_calculate_divergence.
-- Test preparation. Find a row(s) number in the sample big dataframe where the logical conditions to set
is_divergence_high == 1 are met

-- Assert that the value in is_divergence_high of rows where the logical conditions are met, == 1

-- Implementation: ingest large sample dataframe. Make assertion using expected row number(s)

-- Status: Open

Test 6: entry calculator module: test_get_entry_candidates.
-- Test preparation. Find a row(s) number in the sample big dataframe where the logical conditions to set
is_entry_candidate == 1 are met (if last_row['rsi'] >= 65 and last_row['is_divergence_high'] == 1)

-- Assert that the value in is_entry_candidate of rows where the logical conditions are met, == 1

-- Implementation: ingest large sample dataframe. Make assertion using expected row number(s)

-- Status: Open

Test 7: entry calculator module: test_get_entry_row.
-- Test preparation. Find a row(s) number in the sample big dataframe where is_entry_candidate == 1

-- Assert that the value in is_entry_candidate of rows which pass logical checks, == 1

-- Implementation: ingest large sample dataframe. Make assertion using expected row number(s)

-- Status: Open

"""