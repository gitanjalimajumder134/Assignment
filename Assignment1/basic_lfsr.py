# Basic LFSR Implementation 

class BasicLFSR:
    def __init__(self, seed="0110"):
        """Initialize the LFSR with a fixed configuration (4-bit register)."""
        self.state = [int(bit) for bit in seed]  # Convert string to list of integers
    
    def get_state(self):
        """Return the current state as a binary string."""
        return ''.join(map(str, self.state))
    
    def next_bit(self):
        """Generate the next stream bit and update the state."""
        feedback = self.state[0] ^ self.state[2]  # XOR positions 1 and 3 (fixed feedback)
        output_bit = self.state[-1]  # Capture the rightmost bit as output
        self.state = self.state[1:] + [feedback]  # Shift left and append feedback
        return output_bit

# Initialize LFSR with state 0110
lfsr = BasicLFSR(seed="0110")
print("Initial State:", lfsr.get_state())

# Run LFSR for 20 iterations
for i in range(20):
    output_bit = lfsr.next_bit()
    print(f"Iteration {i+1}: State = {lfsr.get_state()}, Next Bit = {output_bit}")
