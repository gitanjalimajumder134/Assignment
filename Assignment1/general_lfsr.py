# General (Reconfigurable) LFSR Implementation

class GeneralLFSR:
    def __init__(self, size=4, seed="0110", taps=[0, 2]):
        """Initialize the LFSR with a given size, seed state, and tap sequence."""
        self.size = size
        self.initial_state = [int(bit) for bit in seed]
        self.state = self.initial_state[:]
        self.taps = taps

    def get_state(self):
        """Return the current state as a binary string."""
        return ''.join(map(str, self.state))

    def set_state(self, new_state):
        """Set a new state for the LFSR."""
        self.state = [int(bit) for bit in new_state]

    def reset(self):
        """Reset LFSR to its initial state."""
        self.state = self.initial_state[:]

    def next_bit(self):
        """Generate the next stream bit, update the state, and return the output bit."""
        feedback = 0
        for tap in self.taps:
            feedback ^= self.state[tap]  # XOR all tap positions
        
        output_bit = self.state[-1]  # Capture the rightmost bit as output
        self.state = self.state[1:] + [feedback]  # Shift left and insert feedback
        return output_bit

# Instantiate the General LFSR to match the Basic LFSR case
lfsr = GeneralLFSR(size=4, seed="0110", taps=[0, 2])

print("Initial State:", lfsr.get_state())

# Run for 20 iterations and compare output with basic LFSR
for i in range(20):
    output_bit = lfsr.next_bit()
    print(f"Iteration {i+1}: State = {lfsr.get_state()}, Next Bit = {output_bit}")
