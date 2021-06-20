def is_hex_string(s, expected_len=0, non_zero_value=True):

    if (expected_len > 0):
        actual_len = len(s)
        if (actual_len != expected_len):
            print(f"s={s},exp_len={expected_len},actual_len={l}", file=sys.stderr)
            return False

    try:
        val = int(f"0x{s}", 16)
        if (non_zero_value and val == 0):
            print(f"s={s},zero valued", file=sys.stderr)
            return False
    except ValueError:
        print(f"s={s},not in hex", file=sys.stderr)
        return False

    return True

