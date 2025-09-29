import os
import time
import math

# =========================================================
# ANSI COLORS (shared)
# =========================================================
WHITE_BG = "\u001b[48;2;255;255;255m"
BLACK_BG = "\u001b[40;1m"      # used for solid blocks (curve, bars)
BLACK_FG = "\u001b[30;1m"      # used for axis/labels text
RESET    = "\u001b[0m"

# =========================================================
# 1) FLAG — Poland
# =========================================================
def draw_flag_color():

    height = 6
    width = 30
    red_bg = "\u001b[48;2;255;0;0m"

    # White half
    for _ in range(height // 2):
        print(WHITE_BG + " " * width + RESET)

    # Red half
    for _ in range(height // 2, height):
        print(red_bg + " " * width + RESET)

# =========================================================
# 2) PATTERN d
# =========================================================
def draw_pattern(width=12, top_pad=2, bottom_pad=2):

    # Top white padding
    for _ in range(top_pad):
        print("".join([WHITE_BG + " " for _ in range(width)]) + RESET)

    # Row 1: full black bar
    print("".join([BLACK_BG + " " for _ in range(width)]) + RESET)

    # Row 2: only column 5 black
    row2 = "".join([BLACK_BG + " " if i == 5 else WHITE_BG + " "
                    for i in range(1, width + 1)])
    print(row2 + RESET)

    # Row 3: full black bar
    print("".join([BLACK_BG + " " for _ in range(width)]) + RESET)

    # Row 4: columns 3 and 8 black
    row4 = "".join([BLACK_BG + " " if i in (3, 8) else WHITE_BG + " "
                    for i in range(1, width + 1)])
    print(row4 + RESET)

    # Row 5: full black bar
    print("".join([BLACK_BG + " " for _ in range(width)]) + RESET)

    # Bottom white padding
    for _ in range(bottom_pad):
        print("".join([WHITE_BG + " " for _ in range(width)]) + RESET)

# =========================================================
# 3) FUNCTION y = x ^ 0.5
# =========================================================
def plot_sqrt_clean(x_max=100, width=90, height=20,
                    xtick_step=20, ytick_step=2, curve_thickness=0):

    y_max = math.sqrt(x_max)
    label_w = 5  # left margin for y tick labels

    # Pre-compute tick positions (grid indices)
    y_ticks = {round(t / y_max * height): f"{t:>3}"
               for t in range(0, int(y_max) + 1, ytick_step)}
    x_ticks = {round(t / x_max * width): str(t)
               for t in range(0, x_max + 1, xtick_step)}

    # Draw from top row down to zero
    for r in range(height, -1, -1):
        # Left y-label column (only on tick rows)
        if r in y_ticks:
            left = WHITE_BG + y_ticks[r].rjust(label_w - 1) + " " + RESET
        else:
            left = WHITE_BG + " " * label_w + RESET

        row = []
        for c in range(0, width + 1):
            # Axes
            if r == 0 and c == 0:
                row.append(BLACK_FG + "└" + RESET)   # origin
                continue
            if c == 0:
                row.append(BLACK_FG + "│" + RESET)   # y-axis
                continue
            if r == 0:
                row.append(BLACK_FG + "─" + RESET)   # x-axis
                continue

            # Curve y = sqrt(x)
            x_real = c / width * x_max
            y_real = math.sqrt(x_real)
            y_idx  = round(y_real / y_max * height)

            if abs(r - y_idx) <= curve_thickness:
                row.append(BLACK_BG + " " + RESET)
            else:
                row.append(WHITE_BG + " " + RESET)

        print(left + "".join(row))

    # X-labels row (one row below the x-axis)
    buf = [" "] * (width + 1)
    for col, text in x_ticks.items():
        start = max(0, min(width - len(text) + 1, col - len(text) // 2))
        for i, ch in enumerate(text):
            idx = start + i
            if 0 <= idx <= width:
                buf[idx] = ch

    print(WHITE_BG + " " * label_w + RESET +
          "".join(WHITE_BG + (BLACK_FG + ch if ch != " " else " ") + RESET for ch in buf))

# =========================================================
# 4) CONDITION
# =========================================================
def read_numbers(path="sequence.txt"):
    with open(path, "r") as f:
        content = f.read()
    tokens = content.replace(",", " ").split()
    return [float(x) for x in tokens]

def absolute_average(nums):
    return sum(abs(x) for x in nums) / len(nums)

def print_percentage_chart(avg1, avg2, width=50):
    total = avg1 + avg2
    if total == 0:
        print("All values are zero!")
        return
    p1 = avg1 / total
    p2 = avg2 / total

    bar1 = int(p1 * width)
    bar2 = int(p2 * width)

    print("First 125 avg (|x|):", round(avg1, 3))
    print("Second 125 avg (|x|):", round(avg2, 3))
    print()

    print("1:", BLACK_BG + " " * bar1 + RESET + WHITE_BG + " " * (width - bar1) + RESET, f"{p1*100:.1f}%")
    print("2:", BLACK_BG + " " * bar2 + RESET + WHITE_BG + " " * (width - bar2) + RESET, f"{p2*100:.1f}%")

# =========================================================
# MAIN PROGRAM
# =========================================================
if __name__ == "__main__":
    print("1) Poland Flag:\n")
    draw_flag_color()

    print("\n\n2) Pattern:\n")
    draw_pattern(width=12)  # or: draw_pattern(width=12, top_pad=2, bottom_pad=2)

    print("\n\n3) Function:\n")
    plot_sqrt_clean(
        x_max=100,
        width=100,
        height=22,
        xtick_step=20,
        ytick_step=2,
        curve_thickness=0
    )

    print("\n\n4) Condition:\n")
    try:
        numbers = read_numbers("sequence.txt")
    except FileNotFoundError:
        print("sequence.txt not found.")
    else:
        if len(numbers) < 250:
            print("At least 250 numbers are required (first 125 + second 125).")
        else:
            first125  = numbers[:125]
            second125 = numbers[125:250]
            avg1 = absolute_average(first125)
            avg2 = absolute_average(second125)
            print_percentage_chart(avg1, avg2, width=50)
