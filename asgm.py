from tkinter import *
from tkinter import messagebox, ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg



# ================= File Manager Base Class =================
class FileManager:
    def __init__(self, filename):
        self._filename = None
        self._data = {}
        self.set_filename(filename)  # use setter

    # === Java-style Getter & Setter ===
    def get_filename(self):
        return self._filename

    def set_filename(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Filename must be a non-empty string")
        self._filename = value.strip()

    def get_data(self):
        return self._data.copy()

    def set_data(self, value):
        if not isinstance(value, dict):
            raise ValueError("Data must be a dictionary")
        self._data = value.copy()

    # Abstract methods
    def load_data(self):
        raise NotImplementedError("Subclasses must implement load_data()")

    def save_data(self):
        raise NotImplementedError("Subclasses must implement save_data()")


# ================= Grade Manager (inherits FileManager) =================
class GradeTextFileManager(FileManager):
    DEFAULT_GRADES = {
        "A": 4.0000,
        "A-": 3.7500,
        "B+": 3.5000,
        "B": 3.0000,
        "B-": 2.7500,
        "C+": 2.5000,
        "C": 2.0000,
        "F": 0.0000,
    }

    def __init__(self, filename="grades.txt"):
        super().__init__(filename)
        self._grades = {}
        self.load_data()

    # === Java-style Getter & Setter for grades ===
    def get_grades(self):
        return self._grades.copy()

    def set_grades(self, value):
        if not isinstance(value, dict):
            raise ValueError("Grades must be a dictionary")
        for g, p in value.items():
            if not isinstance(g, str):
                raise ValueError("Grade name must be a string")
            if not isinstance(p, (int, float)) or not (0.0 <= p <= 4.0):
                raise ValueError(f"Invalid grade point for {g}: {p}")
        self._grades = value.copy()

    def load_data(self):
        self._grades.clear()
        try:
            with open(self.get_filename(), "r") as f:
                for line in f:
                    if line.strip():
                        grade, point = line.strip().split()
                        self._grades[grade] = float(point)
        except FileNotFoundError:
            self._grades = self.DEFAULT_GRADES.copy()
            self.save_data()

    def save_data(self):
        with open(self.get_filename(), "w") as f:
            for grade, point in self._grades.items():
                f.write(f"{grade} {point}\n")

    def get_grades_list(self):
        return list(self._grades.keys())

    def get_grade_point(self, grade):
        return self._grades.get(grade, None)



# ================= GPA Calculator =================
class GPACalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("GPA Calculator")
        self.root.geometry("1000x600")
        self.root.configure(bg="lightblue")
        
        # Title
        Label(root, text="GPA Calculator", font=("Arial", 20, "bold"), bg="lightblue").pack(pady=10)

        # Use GradeTextFileManager instead of GradeSystem
        self.grade_manager = GradeTextFileManager()

        # Main layout: chart (left) | input (center) | grade list (right)
        main_frame = Frame(root, bg="lightblue")
        main_frame.pack(expand=True, fill=BOTH)

        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # === Left frame (Pie Chart) ===
        self.chart_frame = Frame(main_frame, bg="lightblue", width=400, height=400)
        self.chart_frame.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")
        self.chart_frame.grid_propagate(False)

        # 初始化图表
        self.fig = Figure(figsize=(4, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.chart_canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.chart_canvas.get_tk_widget().pack()

        # 显示 "No Data Yet"
        self.ax.text(0.5, 0.5, "No Data Yet", ha="center", va="center",
                     fontsize=12, color="gray")
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.chart_canvas.draw()

        # === Middle frame (Input area) ===
        middle_frame = Frame(main_frame, bg="lightblue")
        middle_frame.grid(row=0, column=1, padx=20, pady=10, sticky="nsew")

        self.subject_frame = Frame(middle_frame, bg="lightblue")
        self.subject_frame.pack(pady=10)

        # Table header
        header = Frame(self.subject_frame, bg="lightblue")
        header.pack(pady=5)
        Label(header, text="Subject", width=11, bg="lightblue", font=("Arial", 10, "bold")).grid(row=0, column=0)
        Label(header, text="Credit", width=8, bg="lightblue", font=("Arial", 10, "bold")).grid(row=0, column=1)
        Label(header, text="Grade", width=12, bg="lightblue", font=("Arial", 10, "bold")).grid(row=0, column=2)

        self._rows = []
        self.add_row()

        # Buttons
        button_frame = Frame(middle_frame, bg="lightblue")
        button_frame.pack(pady=10)
        self.styled_button(button_frame, "Add Subject", self.add_row).pack(pady=5)
        self.styled_button(button_frame, "Calculate GPA", self.calculate_gpa).pack(pady=5)
        self.styled_button(button_frame, "Reset All", self.confirm_reset_all).pack(pady=5)

        # Result labels
        self.result_label = Label(middle_frame, text="", font=("Arial", 14, "bold"), bg="lightblue")
        self.result_label.pack(pady=5)
        self.credit_label = Label(middle_frame, text="", font=("Arial", 12, "bold"), bg="lightblue")
        self.credit_label.pack(pady=5)

               # === Right frame (Grade list + editor) ===
        self.gpa_frame = Frame(main_frame, bg="white", bd=2, relief=SOLID)
        self.gpa_frame.grid(row=0, column=2, padx=20, pady=10, sticky="n")

        Label(self.gpa_frame, text="Grade List", font=("Arial", 14, "bold"), bg="white").pack(pady=5)

        self.grade_list_frame = Frame(self.gpa_frame, bg="white")
        self.grade_list_frame.pack()
        self.show_grade_list()

        # Edit button
        self.styled_button(self.gpa_frame, "Edit Grade List", self.open_edit_popup).pack(pady=10)

    def styled_button(self, parent, text, command):
        return Button(parent, text=text, command=command, bg="white", fg="black",
                      font=("Arial", 10, "bold"), width=14)

    def add_row(self):
        if len(self._rows) >= 10:
            messagebox.showwarning("Warning", "Maximum of 10 subjects allowed.")
            return

        row_frame = Frame(self.subject_frame, bg="lightblue")
        row_frame.pack(pady=2)

        subject = Entry(row_frame, width=15, justify="center")
        subject.grid(row=0, column=0, padx=5)

        credit = Entry(row_frame, width=8, justify="center")
        credit.grid(row=0, column=1, padx=5)

        grade = ttk.Combobox(row_frame, values=self.grade_manager.get_grades_list(),
                             width=12, state="readonly", justify="center")
        grade.grid(row=0, column=2, padx=5)

        remove_btn = Button(row_frame, text="❌", fg="red", width=3, command=lambda rf=row_frame: self.remove_row(rf)) 
        remove_btn.grid(row=0, column=3, padx=5)

        self._rows.append((subject, credit, grade, row_frame))

    # Remove row 
    def remove_row(self, row_frame): 
        if len(self._rows) > 1: 
            for row in self._rows: 
                if row[3] == row_frame: 
                    self._rows.remove(row) 
                    row_frame.destroy() 
                    break 
        else: messagebox.showwarning("Warning", "At least one subject must remain.")
                    
       # Show grade list
    def show_grade_list(self):
        for widget in self.grade_list_frame.winfo_children():
            widget.destroy()

        for i, (grade, point) in enumerate(self.grade_manager.get_grades().items()):
            Label(self.grade_list_frame, text=grade, font=("Arial", 11), bg="white",
                width=15, anchor="w").grid(row=i, column=0, padx=5, pady=2)
            Label(self.grade_list_frame, text=f"{point:.4f}", font=("Arial", 11),
                bg="white", width=8).grid(row=i, column=1, padx=5, pady=2)


    # Open grade editor
    def open_edit_popup(self):
        popup = Toplevel(self.root)
        popup.title("Edit Grade List")
        popup.geometry("300x400")
        popup.configure(bg="white")
        popup.transient(self.root)
        popup.grab_set()

        Label(popup, text="Edit Grade List", font=("Arial", 14, "bold"), bg="white").pack(pady=10)

        grade_frame = Frame(popup, bg="white")
        grade_frame.pack()

        self.grade_entries = {}
        for i, (grade, point) in enumerate(self.grade_manager.get_grades().items()):
            Label(grade_frame, text=grade, font=("Arial", 11), bg="white",
                  width=15, anchor="w").grid(row=i, column=0, padx=5, pady=2)
            entry = Entry(grade_frame, width=8, justify="center")
            entry.insert(0, f"{point:.4f}")
            entry.grid(row=i, column=1, padx=5, pady=2)
            self.grade_entries[grade] = entry

        button_frame = Frame(popup, bg="white")
        button_frame.pack(pady=10)
        self.styled_button(button_frame, "Save", lambda: self.save_changes(popup)).grid(row=0, column=0, padx=5)
        self.styled_button(button_frame, "Reset", lambda: self.reset_grades(popup)).grid(row=0, column=1, padx=5)

     # Save changes
    def save_changes(self, popup):
        try:
            new_map = {}
            for grade, entry in self.grade_entries.items():
                new_map[grade] = float(entry.get())

            # === Validation: grade order must be descending ===
            order = ["A", "A-", "B+", "B", "B-", "C+", "C", "F"]
            for i in range(len(order) - 1):
                g1, g2 = order[i], order[i + 1]
                if new_map[g1] < new_map[g2]:
                    messagebox.showerror(
                        "Error",
                        f"Invalid grade order: {g1} must be greater than or equal to {g2}."
                    )
                    return

            self.grade_manager.set_grades(new_map)  # update object
            self.grade_manager.save_data()       # save to grades.txt
            self.show_grade_list()
            popup.destroy()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    # Reset grades to default values
    def reset_grades(self, popup=None):
        self.grade_manager.set_grades(self.grade_manager.DEFAULT_GRADES.copy())
        self.grade_manager.save_data()   # save to grades.txt
        self.show_grade_list()
        if popup:
            popup.destroy()



    def calculate_gpa(self):
        total_points, total_credits = 0, 0
        subjects, contributions, subject_names = [], [], set()

        for subject, credit, grade, _ in self._rows:
            subj_name = subject.get().strip()
            if subj_name in subject_names:
                messagebox.showerror("Error", f"Duplicate subject: {subj_name}")
                return
            subject_names.add(subj_name)

            if not subj_name.replace(" ", "").isalpha():
                messagebox.showerror("Error", f"Subject names must contain only letters/spaces: {subj_name}")
                return

            # ✅ safer conversion for credit input
            try:
                c = int(credit.get())
            except ValueError:
                messagebox.showerror("Error", f"Invalid credit input for {subj_name}. Must be an integer.")
                return

            if c < 1 or c > 4:
                messagebox.showerror("Error", f"Credit for {subj_name} must be 1–4.")
                return

            g = self.grade_manager.get_grade_point(grade.get())
            if g is None:
                messagebox.showerror("Error", f"Select a grade for {subj_name}")
                return

            total_points += c * g
            total_credits += c
            subjects.append(subj_name)
            contributions.append(c * g)

        # ✅ valid even if GPA = 0.0000
        gpa = total_points / total_credits if total_credits else 0
        self.result_label.config(text=f"Your GPA: {gpa:.4f}")
        self.credit_label.config(text=f"Total Credit Hours: {total_credits}")

        self.show_pie_chart(subjects, contributions)


    def show_pie_chart(self, subjects, contributions):
        # 如果还没创建 fig 和 canvas，就创建一次
        if self.fig is None:
            self.fig = Figure(figsize=(4, 4), dpi=100)
            self.ax = self.fig.add_subplot(111)
            self.chart_canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
            self.chart_canvas.get_tk_widget().pack()

        # 清除旧图
        self.ax.clear()

        if subjects and contributions:
            self.ax.pie(contributions, labels=subjects, autopct="%1.1f%%", startangle=90)
            self.ax.set_title("Subject Contribution to GPA")
        else:
            # 空白时显示提示
            self.ax.text(0.5, 0.5, "No Data Yet", ha="center", va="center",
                     fontsize=12, color="gray")
            self.ax.set_xticks([])
            self.ax.set_yticks([])

        self.chart_canvas.draw()


    def reset_all(self):
        # Remove all rows
        for subject, credit, grade, row_frame in self._rows:
            row_frame.destroy()
        self._rows.clear()

        # Add back one empty row
        self.add_row()

        # Clear GPA result and total credits
        self.result_label.config(text="")
        self.credit_label.config(text="")

        # Reset 饼图内容
        self.ax.clear()
        self.ax.text(0.5, 0.5, "No Data Yet", ha="center", va="center",
             fontsize=12, color="gray")
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.chart_canvas.draw()
    
    def confirm_reset_all(self):
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset all inputs?"):
            self.reset_all()



# ================= Run =================
if __name__ == "__main__":
    root = Tk()
    app = GPACalculator(root)
    root.mainloop()