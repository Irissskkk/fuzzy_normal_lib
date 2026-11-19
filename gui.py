"""Графический интерфейс с расчетом границ альфа-сечения и арифметикой."""
import json
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from fuzzy_lib import FuzzyNormal, FuzzySet, generate_set, kmeans, Logger


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Нечёткие величины: α-сечение, операции и кластеризация")
        self.geometry("1250x850")
        self.logger = Logger("fuzzy_log.txt")
        self.fuzzy_set = FuzzySet()
        self.filtered_set = None
        self.current_alpha = None
        self._build_ui()

    def _build_ui(self):
        # --- 1. Панель ввода (x0, sigma) ---
        top = ttk.Frame(self); top.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(top, text="x0:").pack(side=tk.LEFT)
        self.e_x0 = ttk.Entry(top, width=6); self.e_x0.insert(0, "0"); self.e_x0.pack(side=tk.LEFT)
        ttk.Label(top, text="sigma:").pack(side=tk.LEFT)
        self.e_sigma = ttk.Entry(top, width=6); self.e_sigma.insert(0, "1"); self.e_sigma.pack(side=tk.LEFT)
        ttk.Button(top, text="Добавить", command=self.add_fv).pack(side=tk.LEFT, padx=5)
        ttk.Button(top, text="Сгенерировать 200", command=self.gen).pack(side=tk.LEFT, padx=5)

        # --- 2. Панель фильтра, операций и кластеризации ---
        mid = ttk.Frame(self); mid.pack(fill=tk.X, padx=5, pady=2)
        
        # Фильтр Альфа
        ttk.Label(mid, text="Альфа-уровень (α):").pack(side=tk.LEFT)
        self.e_alpha = ttk.Entry(mid, width=6); self.e_alpha.insert(0, "0.2"); self.e_alpha.pack(side=tk.LEFT, padx=2)
        ttk.Button(mid, text="Применить фильтр", command=self.apply_alpha_filter).pack(side=tk.LEFT, padx=5)
        ttk.Button(mid, text="Сбросить фильтр", command=self.reset_filter).pack(side=tk.LEFT, padx=5)

        # Операции (НОВОЕ)
        ttk.Label(mid, text=" | Операция:").pack(side=tk.LEFT, padx=(15, 0))
        self.op_var = tk.StringVar(value="+")
        self.op_menu = ttk.Combobox(mid, textvariable=self.op_var, values=["+", "-", "*", "/"], width=3, state="readonly")
        self.op_menu.pack(side=tk.LEFT, padx=2)
        ttk.Button(mid, text="Выполнить (A, B)", command=self.apply_operation).pack(side=tk.LEFT, padx=5)

        # Кластеризация
        ttk.Label(mid, text=" | Кластеры (k):").pack(side=tk.LEFT, padx=(15, 0))
        self.e_k = ttk.Entry(mid, width=4); self.e_k.insert(0, "3"); self.e_k.pack(side=tk.LEFT)
        ttk.Button(mid, text="Кластеризовать", command=self.cluster).pack(side=tk.LEFT, padx=5)

        # --- 3. Таблица ---
        columns = ("name", "x0", "sigma", "x_left", "x_right")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=10)
        for c in columns:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=100, anchor=tk.CENTER)
        self.tree.column("name", width=250)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5)

        # --- 4. График ---
        self.fig, self.ax = plt.subplots(figsize=(8, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.status = ttk.Label(self, text="Готово. Задайте α и нажмите 'Применить фильтр'.")
        self.status.pack(fill=tk.X, padx=5, pady=3)

    def add_fv(self):
        try:
            x0 = float(self.e_x0.get()); sigma = float(self.e_sigma.get())
            fv = FuzzyNormal(x0, sigma)
            self.fuzzy_set.add(fv)
            self._insert_to_tree(fv)
            self.logger.log(f"Добавлена {fv.name}")
            self.redraw()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def gen(self):
        self.fuzzy_set = generate_set(200)
        self.filtered_set = None
        self.current_alpha = None
        self.tree.delete(*self.tree.get_children())
        for fv in self.fuzzy_set:
            self._insert_to_tree(fv)
        self.logger.log("Сгенерировано 200 величин")
        self.redraw()

    def _insert_to_tree(self, fv, alpha=None):
        xl, xr = "-", "-"
        if alpha is not None:
            res = fv.alpha_cut(alpha)
            if res:
                xl, xr = f"{res[0]:.3f}", f"{res[1]:.3f}"
        self.tree.insert("", tk.END, values=(fv.name, f"{fv.x0:.3f}", f"{fv.sigma:.3f}", xl, xr))

    def apply_alpha_filter(self):
        try:
            alpha = float(self.e_alpha.get())
            if not (0 < alpha <= 1):
                raise ValueError("α должно быть в диапазоне (0, 1]")
            
            self.current_alpha = alpha
            self.filtered_set = FuzzySet()
            self.tree.delete(*self.tree.get_children())
            
            count = 0
            for fv in self.fuzzy_set:
                if fv.alpha_cut(alpha) is not None:
                    self.filtered_set.add(fv)
                    self._insert_to_tree(fv, alpha)
                    count += 1
            
            self.logger.log(f"α-сечение α={alpha}: осталось {count} из {len(self.fuzzy_set)}")
            self.status.config(text=f"Фильтр α={alpha}: осталось {count} величин (границы в таблице)")
            self.redraw(alpha)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def reset_filter(self):
        self.filtered_set = None
        self.current_alpha = None
        self.tree.delete(*self.tree.get_children())
        for fv in self.fuzzy_set:
            self._insert_to_tree(fv)
        self.status.config(text="Фильтр сброшен. Показаны все данные.")
        self.redraw()

    def apply_operation(self):
        selected = self.tree.selection()
        if len(selected) != 2:
            messagebox.showwarning("Внимание", "Выделите ровно ДВЕ величины в таблице (зажмите Cmd/Ctrl)")
            return
        try:
            idx1 = self.tree.index(selected[0])
            idx2 = self.tree.index(selected[1])
            
            current_set = self.filtered_set if self.filtered_set else self.fuzzy_set
            fv1 = current_set[idx1]
            fv2 = current_set[idx2]
            
            op = self.op_var.get()
            if op == "+": result = fv1 + fv2
            elif op == "-": result = fv1 - fv2
            elif op == "*": result = fv1 * fv2
            elif op == "/": result = fv1 / fv2
            else: return

            result.name = f"({fv1.name} {op} {fv2.name})"
            self.fuzzy_set.add(result)
            
            if self.filtered_set:
                self.filtered_set.add(result)
                
            self._insert_to_tree(result, self.current_alpha)
            self.logger.log(f"Операция: {fv1.name} {op} {fv2.name} = {result.name}")
            self.redraw(self.current_alpha)
            self.status.config(text=f"Выполнено: {result.name}")
        except ZeroDivisionError:
            messagebox.showerror("Ошибка", "Деление на ноль (x0 ≈ 0)")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def cluster(self):
        target_set = self.filtered_set if self.filtered_set else self.fuzzy_set
        if len(target_set) == 0:
            messagebox.showwarning("Внимание", "Нет данных для кластеризации")
            return
        try:
            k = int(self.e_k.get())
            clusters = kmeans(target_set, k)
            self.show_clusters(clusters)
            self.status.config(text=f"Кластеры: {[len(c) for c in clusters]}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def redraw(self, alpha=None):
        self.ax.clear()
        target = self.filtered_set if self.filtered_set else self.fuzzy_set
        
        for fv in target:
            xs = [fv.x0 + i * fv.sigma / 20 for i in range(-60, 61)]
            ys = [fv.membership(x) for x in xs]
            self.ax.plot(xs, ys, alpha=0.3 if len(target) > 50 else 0.6)
            
        if alpha is not None:
            self.ax.axhline(y=alpha, color='black', linestyle='--', label=f'α={alpha}')
            
            for fv in target:
                res = fv.alpha_cut(alpha)
                if res:
                    self.ax.plot([res[0], res[1]], [alpha, alpha], 'r-', linewidth=2, alpha=0.5)

        self.ax.set_title(f"Функции принадлежности ({len(target)} шт.)")
        self.ax.set_ylim(0, 1) 
        self.canvas.draw()

    def show_clusters(self, clusters):
        self.ax.clear()
        colors = ["red", "blue", "green", "orange", "purple", "brown", "pink", "gray", "olive", "cyan"]
        for i, cl in enumerate(clusters):
            xs = [fv.x0 for fv in cl]
            ys = [fv.sigma for fv in cl]
            self.ax.scatter(xs, ys, c=colors[i % len(colors)], label=f"Кластер {i+1}", alpha=0.7)
        self.ax.set_xlabel("x0"); self.ax.set_ylabel("sigma")
        self.ax.set_title("Кластеры нечётких величин (k-means)")
        self.ax.legend()
        self.canvas.draw()


if __name__ == "__main__":
    App().mainloop()
