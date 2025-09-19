import tkinter as tk
from time import sleep
import heapq
import itertools

N = 4
CELL_SIZE = 60
LIGHT_COLOR = "#f0d9b5"
DARK_COLOR = "#b58863"
ROOK_COLOR = "#1976d2"
FONT_FALLBACK = ("Segoe UI Symbol", int(CELL_SIZE * 0.6))
SLEEP_TIME = 0.5

def state_to_tuple(state):
    return tuple(tuple(r) for r in state)

def initial_board(n):
    return [[0 for _ in range(n)] for _ in range(n)]

def placed_rows(state):
    return sum(sum(r) for r in state)

def actions(state):
    row = placed_rows(state)
    if row >= N:
        return []
    used_cols = {c for r in state for c, val in enumerate(r) if val == 1}
    return [(row, c) for c in range(N) if c not in used_cols]

def make_child_state(state, action):
    row, col = action
    new_state = [r.copy() for r in state]
    new_state[row][col] = 1
    return new_state

def h_simple(state):
    return N - placed_rows(state)

def draw(canvas: tk.Canvas, rooks=None):
    canvas.delete("all")
    for r in range(N):
        for c in range(N):
            x0 = c * CELL_SIZE
            y0 = r * CELL_SIZE
            x1 = x0 + CELL_SIZE
            y1 = y0 + CELL_SIZE
            color = LIGHT_COLOR if (r + c) % 2 == 0 else DARK_COLOR
            canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline=color)

    # Ghi nhãn cột / hàng (gọn)
    for i in range(N):
        col_label = chr(ord('A') + i)
        canvas.create_text(i * CELL_SIZE + CELL_SIZE/2, 10,
                           text=col_label, font=("Arial", 10, "bold"))
        row_label = str(N - i)
        canvas.create_text(10, i * CELL_SIZE + CELL_SIZE/2,
                           text=row_label, font=("Arial", 10, "bold"))

    if rooks:
        for r in range(N):
            for c in range(N):
                if rooks[r][c] == 1:
                    x = c * CELL_SIZE + CELL_SIZE/2
                    y = r * CELL_SIZE + CELL_SIZE/2
                    canvas.create_text(x, y, text="♖", font=FONT_FALLBACK, fill=ROOK_COLOR)

def iterative_deepening_search(canvas, status_label):
    def dls(node_state, limit):
        draw(canvas, node_state)
        status_label.config(text=f"IDS: depth {placed_rows(node_state)} / limit {limit}")
        canvas.update()
        status_label.update()
        sleep(SLEEP_TIME)

        if placed_rows(node_state) == N:
            return node_state
        if limit == 0:
            return "cutoff"
        cutoff = False
        for act in actions(node_state):
            child = make_child_state(node_state, act)
            res = dls(child, limit - 1)
            if res == "cutoff":
                cutoff = True
            elif res != "failure":
                return res
        return "cutoff" if cutoff else "failure"

    for depth in range(N + 1):
        status_label.config(text=f"IDS: trying limit {depth}")
        status_label.update()
        root = initial_board(N)
        res = dls(root, depth)
        if res not in ("cutoff", "failure"):
            return res
    return None

def greedy_search(canvas, status_label):
    counter = itertools.count()
    start = initial_board(N)
    h0 = h_simple(start)
    heap = [(h0, next(counter), start)]
    explored = set()

    while heap:
        h_val, _, state = heapq.heappop(heap)
        draw(canvas, state)
        status_label.config(text=f"Greedy: h={h_val} placed={placed_rows(state)}")
        canvas.update()
        status_label.update()
        sleep(SLEEP_TIME)

        if placed_rows(state) == N:
            return state
        explored.add(state_to_tuple(state))
        for act in actions(state):
            child = make_child_state(state, act)
            tup = state_to_tuple(child)
            if tup in explored:
                continue
            heapq.heappush(heap, (h_simple(child), next(counter), child))
    return None

def a_star_search(canvas, status_label):
    counter = itertools.count()
    start = initial_board(N)
    g_start = 0
    h_start = h_simple(start)
    start_entry = (g_start + h_start, next(counter), start, g_start, h_start)
    heap = [start_entry]
    explored = dict()

    while heap:
        f_val, _, state, g_val, h_val = heapq.heappop(heap)
        draw(canvas, state)
        status_label.config(text=f"A*: f={f_val} g={g_val} h={h_val} placed={placed_rows(state)}")
        canvas.update()
        status_label.update()
        sleep(SLEEP_TIME)

        if placed_rows(state) == N:
            return state
        tup = state_to_tuple(state)
        if tup in explored and explored[tup] <= g_val:
            continue
        explored[tup] = g_val

        for act in actions(state):
            child = make_child_state(state, act)
            child_g = g_val + 1  # mỗi bước tăng 1
            child_h = h_simple(child)
            child_f = child_g + child_h
            child_tup = state_to_tuple(child)
            if child_tup in explored and explored[child_tup] <= child_g:
                continue
            heapq.heappush(heap, (child_f, next(counter), child, child_g, child_h))
    return None

# ---------- GUI ----------
def start(root: tk.Tk):
    global left_canvas, right_canvas, status_left, status_right
    root.title("IDS / Greedy / A* (Đặt N Quân Xe)")
    root.resizable(False, False)

    wrapper = tk.Frame(root)
    wrapper.pack(padx=12, pady=12)

    frame_ids = tk.Frame(wrapper)
    frame_ids.grid(row=0, column=0, padx=6)
    tk.Label(frame_ids, text="IDS (trái)", font=("Arial", 12)).pack(pady=(0, 8))
    canvas_ids = tk.Canvas(frame_ids, width=N*CELL_SIZE, height=N*CELL_SIZE,
                           highlightthickness=1, highlightbackground="#999")
    canvas_ids.pack()
    status_ids = tk.Label(frame_ids, text="IDS: -", font=("Arial", 10), fg="blue")
    status_ids.pack(pady=5)

    frame_greedy = tk.Frame(wrapper)
    frame_greedy.grid(row=0, column=1, padx=6)
    tk.Label(frame_greedy, text="Greedy (giữa)", font=("Arial", 12)).pack(pady=(0, 8))
    canvas_greedy = tk.Canvas(frame_greedy, width=N*CELL_SIZE, height=N*CELL_SIZE,
                              highlightthickness=1, highlightbackground="#999")
    canvas_greedy.pack()
    status_greedy = tk.Label(frame_greedy, text="Greedy: -", font=("Arial", 10), fg="blue")
    status_greedy.pack(pady=5)

    frame_astar = tk.Frame(wrapper)
    frame_astar.grid(row=0, column=2, padx=6)
    tk.Label(frame_astar, text="A* (phải)", font=("Arial", 12)).pack(pady=(0, 8))
    canvas_astar = tk.Canvas(frame_astar, width=N*CELL_SIZE, height=N*CELL_SIZE,
                             highlightthickness=1, highlightbackground="#999")
    canvas_astar.pack()
    status_astar = tk.Label(frame_astar, text="A*: -", font=("Arial", 10), fg="blue")
    status_astar.pack(pady=5)

    controls = tk.Frame(wrapper)
    controls.grid(row=1, column=0, columnspan=3, pady=10)

    def run_ids():
        draw(canvas_ids, None)
        status_ids.config(text="IDS: running...")
        root.update_idletasks()
        res = iterative_deepening_search(canvas_ids, status_ids)
        if res:
            draw(canvas_ids, res)
            status_ids.config(text=f"IDS: Found solution (placed={placed_rows(res)})")
        else:
            status_ids.config(text="IDS: No solution")

    def run_greedy():
        draw(canvas_greedy, None)
        status_greedy.config(text="Greedy: running...")
        root.update_idletasks()
        res = greedy_search(canvas_greedy, status_greedy)
        if res:
            draw(canvas_greedy, res)
            status_greedy.config(text=f"Greedy: Found solution (placed={placed_rows(res)})")
        else:
            status_greedy.config(text="Greedy: No solution")

    def run_astar():
        draw(canvas_astar, None)
        status_astar.config(text="A*: running...")
        root.update_idletasks()
        res = a_star_search(canvas_astar, status_astar)
        if res:
            draw(canvas_astar, res)
            status_astar.config(text=f"A*: Found solution (placed={placed_rows(res)})")
        else:
            status_astar.config(text="A*: No solution")

    tk.Button(controls, text="Chạy IDS", command=run_ids).pack(side="left", padx=8)
    tk.Button(controls, text="Chạy Greedy", command=run_greedy).pack(side="left", padx=8)
    tk.Button(controls, text="Chạy A*", command=run_astar).pack(side="left", padx=8)
    tk.Button(controls, text="Reset canvases", command=lambda: (draw(canvas_ids, None), draw(canvas_greedy, None), draw(canvas_astar, None),
                                                                status_ids.config(text="IDS: -"), status_greedy.config(text="Greedy: -"), status_astar.config(text="A*: -"))).pack(side="left", padx=8)
    
    draw(canvas_ids, None)
    draw(canvas_greedy, None)
    draw(canvas_astar, None)

# Main
root = tk.Tk()
start(root)

# căn giữa
root.update_idletasks()
width, height = root.winfo_width(), root.winfo_height()
sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
x, y = (sw // 2) - (width // 2), (sh // 2) - (height // 2)
root.geometry(f"{width}x{height}+{x}+{y}")
root.mainloop()