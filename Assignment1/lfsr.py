# a) A basic LFSR with a fixed configuration.
# b) A general LFSR that allows customization

class LFSR:
    def __init__(self, size, seed, taps):
        """
        Initialize the LFSR.
        :param size: Number of bits in the register
        :param seed: Initial state (binary string or integer)
        :param taps: List of indices (1-based) for XOR feedback
        """
        self.size = size
        self.state = [int(bit) for bit in format(seed, f'0{size}b')]
        self.taps = [size - tap for tap in taps]  # Convert to 0-based index
        self.initial_state = self.state.copy()
    
    def get_state(self):
        """Return the current state as a binary string."""
        return ''.join(map(str, self.state))
    
    def set_state(self, new_state):
        """Set a new state manually."""
        self.state = [int(bit) for bit in format(new_state, f'0{self.size}b')]
    
    def reset(self):
        """Reset to the initial state."""
        self.state = self.initial_state.copy()
    
    def next_bit(self):
        """Generate the next bit in the sequence and update the state."""
        feedback = 0
        for tap in self.taps:
            feedback ^= self.state[tap]
        
        output_bit = self.state[-1]  # Capture the output bit
        self.state = [feedback] + self.state[:-1]  # Shift right with feedback
        return output_bit
    
    def generate_sequence(self, length):
        """Generate a sequence of bits."""
        return [self.next_bit() for _ in range(length)]

# Example usage:
lfsr = LFSR(size=4, seed=0b0110, taps=[1, 3])  # 4-bit LFSR with taps at positions 1 and 3
print("Initial State:", lfsr.get_state())

sequence = lfsr.generate_sequence(20)
print("Generated Sequence:", sequence)

lfsr.reset()
print("State after reset:", lfsr.get_state())
