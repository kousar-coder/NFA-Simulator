import tkinter as tk
from tkinter import messagebox
import math

class TransitionEntryWindow(tk.Toplevel):
    def __init__(self, num_transitions, callback):
        super().__init__()

        self.title("Transition Entry")
        self.callback = callback
        self.transition_entries = []

        for i in range(num_transitions):
            transition_frame = tk.Frame(self)
            transition_frame.pack()

            from_state_label = tk.Label(transition_frame, text=f"Transition {i+1}:", padx=5)
            from_state_label.grid(row=0, column=0)
            from_state_entry = tk.Entry(transition_frame, width=10)
            from_state_entry.grid(row=0, column=1)

            symbol_label = tk.Label(transition_frame, text="Symbol:", padx=5)
            symbol_label.grid(row=0, column=2)
            symbol_entry = tk.Entry(transition_frame, width=10)
            symbol_entry.grid(row=0, column=3)

            to_state_label = tk.Label(transition_frame, text="To State:", padx=5)
            to_state_label.grid(row=0, column=4)
            to_state_entry = tk.Entry(transition_frame, width=10)
            to_state_entry.grid(row=0, column=5)

            self.transition_entries.append((from_state_entry, symbol_entry, to_state_entry))

        submit_button = tk.Button(self, text="Submit", command=self.submit_transitions)
        submit_button.pack(pady=10)

    def submit_transitions(self):
        transitions = {}
        for entry in self.transition_entries:
            from_state = entry[0].get().strip()
            symbol = entry[1].get().strip()
            to_state = entry[2].get().strip()
            if from_state and symbol and to_state:
                transition_key = (from_state, to_state)
                if transition_key not in transitions:
                    transitions[transition_key] = []
                transitions[transition_key].append(symbol)
            else:
                messagebox.showerror("Error", "All transition fields must be filled.")
                return

        self.callback(transitions)

    def on_close(self):
        # Prevent the window from closing
        self.withdraw()


class NFAVisualizerWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("NFA Visualizer")

        self.state_label = tk.Label(self, text="Enter NFA states (comma-separated, use '-' for initial state and '+' for final states):")
        self.state_label.pack()
        self.state_entry = tk.Entry(self)
        self.state_entry.pack()

        self.num_transitions_label = tk.Label(self, text="Enter the number of transitions:")
        self.num_transitions_label.pack()
        self.num_transitions_entry = tk.Entry(self)
        self.num_transitions_entry.pack()

        # Button to open transition entry window
        self.transition_button = tk.Button(self, text="Enter Transitions", command=self.open_transition_entry)
        self.transition_button.pack()

        # Canvas to display the NFA
        self.canvas = tk.Canvas(self, width=750, height=550, bg="white")
        self.canvas.pack()

        # Label and entry field for input string
        self.string_label = tk.Label(self, text="Enter input string:")
        self.string_label.pack()
        self.string_entry = tk.Entry(self)
        self.string_entry.pack()

        self.check_string_button = tk.Button(self, text="Check String", command=self.check_string)
        self.check_string_button.pack()

        # Close button
        self.close_button = tk.Button(self, text="Close", command=self.close_windows, width=10)
        self.close_button.pack()

        # Keep a reference to the transition entry window
        self.transition_entry_window = None

        # Handle window closing event
        self.protocol("WM_DELETE_WINDOW", self.close_windows)

    def open_transition_entry(self):
        num_transitions = int(self.num_transitions_entry.get().strip())
        if num_transitions <= 0:
            messagebox.showerror("Error", "Number of transitions must be greater than zero.")
            return
        self.transition_entry_window = TransitionEntryWindow(num_transitions, self.set_transitions)

    def set_transitions(self, transitions):
        self.transitions = transitions
        self.draw_nfa()

    def draw_nfa(self):
        # Clear canvas
        self.canvas.delete("all")

        # Get input from entry fields
        states_input = self.state_entry.get().strip()
        nfa_states = []
        accepting_states = []  # Keep track of accepting states
        for state in states_input.split(","):
            if '+' in state:
                state = state.replace('+', '')
                nfa_states.append((state, 'final'))
                accepting_states.append(state)
            elif '-' in state:
                state = state.replace('-', '')
                nfa_states.append((state, 'initial'))
            else:
                nfa_states.append((state, 'normal'))

        num_states = len(nfa_states)
        radius = 150
        center_x = 400
        center_y = 300
        angle_increment = 360 / num_states

        # Draw states in a circular formation
        for i, (state, state_type) in enumerate(nfa_states):
            angle = math.radians(i * angle_increment)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            fill_color = "white"
            if state_type == 'initial':
                fill_color = "green"  # Initial state
            elif state_type == 'final':
                fill_color = "red"  # Final state
            self.canvas.create_oval(x - 30, y - 30, x + 30, y + 30, outline="black", fill=fill_color)
            self.canvas.create_text(x, y, text=state, font=("Arial", 12, "bold"))

        # Define colors for transition arrows
        colors = ["blue", "green", "orange", "purple", "cyan", "magenta","green","pink","red","beige","aqua"]

        # Draw transitions
        color_index = 0
        for transition, symbols in self.transitions.items():
            start_state, end_state = transition
            start_state = start_state.strip()
            end_state = end_state.strip()
            if start_state not in [state[0] for state in nfa_states] or end_state not in [state[0] for state in nfa_states]:
                messagebox.showerror("Error", f"Invalid transition: {transition}")
                return

            start_index = [state[0] for state in nfa_states].index(start_state)
            end_index = [state[0] for state in nfa_states].index(end_state)
            start_angle = math.radians(start_index * angle_increment)
            end_angle = math.radians(end_index * angle_increment)
            start_x = center_x + radius * math.cos(start_angle)
            start_y = center_y + radius * math.sin(start_angle)
            end_x = center_x + radius * math.cos(end_angle)
            end_y = center_y + radius * math.sin(end_angle)
            arrow_offset = 30

            # For self-loops, adjust arrow endpoint
            if start_state == end_state:
                mid_angle = math.radians(start_index * angle_increment)
                mid_x = center_x + 1.2 * radius * math.cos(mid_angle)
                mid_y = center_y + 1.2 * radius * math.sin(mid_angle)
                arrow_angle = mid_angle + math.pi / 2  # Angle of self-loop arrow
                arrow_end_x = mid_x + 15 * math.cos(arrow_angle)
                arrow_end_y = mid_y + 15 * math.sin(arrow_angle)
            else:
                arrow_angle = math.atan2(end_y - start_y, end_x - start_x)
                arrow_end_x = end_x - arrow_offset * math.cos(arrow_angle)
                arrow_end_y = end_y - arrow_offset * math.sin(arrow_angle)

            # Draw arrow
            self.canvas.create_line(start_x, start_y, arrow_end_x, arrow_end_y, arrow=tk.LAST, fill=colors[color_index])

            # Draw transition letter(s)
            text_angle = arrow_angle + math.pi / 6  # Adjust angle for text placement
            text_x = (start_x + arrow_end_x) / 2
            text_y = (start_y + arrow_end_y) / 2

            # Display symbols on top of arrow
            for symbol in symbols:
                self.canvas.create_text(text_x, text_y-10, text=symbol, font=("Arial", 12, "bold"), fill="black")
                text_y -= 20  # Move text upward

            # Increment color index
            color_index = (color_index + 1) % len(colors)

        # Draw circles around accepting states
        for state, _ in nfa_states:
            if state in accepting_states:
                state_index = [s[0] for s in nfa_states].index(state)
                angle = math.radians(state_index * angle_increment)
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                self.canvas.create_oval(x - 40, y - 40, x + 40, y + 40, outline="black", width=2, dash=(5, 5))

    def check_string(self):
        # Get input string from entry field
        input_string = self.string_entry.get().strip()

        # Get NFA states
        states_input = self.state_entry.get().strip()
        nfa_states = []
        for state in states_input.split(","):
            if '+' in state:
                state = state.replace('+', '')
                nfa_states.append((state, 'final'))
            elif '-' in state:
                state = state.replace('-', '')
                nfa_states.append((state, 'initial'))
            else:
                nfa_states.append((state, 'normal'))

        # Define a recursive DFS function to explore all possible paths
        def dfs(current_states, index):
            # Base case: end of input string
            if index == len(input_string):
                # Check if any of the current states are final states
                if any(state[0] in current_states and state[1] == 'final' for state in nfa_states):
                    return True
                else:
                    return False

            next_states = []
            # Check transitions for each current state
            for state in current_states:
                for transition, symbols in self.transitions.items():
                    if transition[0] == state and input_string[index] in symbols:
                        next_states.append(transition[1])
            
            # Recursively explore all possible paths
            for next_state in next_states:
                if dfs([next_state], index + 1):
                    return True

            return False

        # Initialize current set of states with the initial state
        current_states = [state[0] for state in nfa_states if state[1] == 'initial']

        # Start DFS from the initial state
        if dfs(current_states, 0):
            messagebox.showinfo("Accepted", "The input string is accepted by the NFA.")
        else:
            messagebox.showinfo("Rejected", "The input string is rejected by the NFA.")

    def close_windows(self):
        # Destroy both windows
        if self.transition_entry_window:
            self.transition_entry_window.on_close()
        self.destroy()

    def on_close(self):
        # Close both windows when the main window is closed
        self.close_windows()

if __name__ == "__main__":
    app = NFAVisualizerWindow()
    app.mainloop()