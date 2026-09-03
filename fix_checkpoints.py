with open("rust/src/lib.rs", "r") as f:
    text = f.read()

# Let's inspect the lines around CP01_ENTER
start_pos = text.find("log_checkpoint")
print("log_checkpoint found at:", start_pos)
print("Context around start:\n", text[max(0, start_pos - 100): start_pos + 600])

