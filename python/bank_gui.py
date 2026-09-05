
import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox

# ---------------------------------------------------------------------------
# Locate the compiled C++ backend executable.
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_NAME = "bank_app.exe" if os.name == "nt" else "bank_app"
BACKEND_PATH = os.path.join(PROJECT_ROOT, BACKEND_NAME)


def run_backend(*args):
    try:
        result = subprocess.run(
            [BACKEND_PATH, *[str(a) for a in args]],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=10,
        )
        output = result.stdout.strip()
        if not output:
            return ["FAIL", result.stderr.strip() or "No response from backend"]
        return output.split("|")
    except FileNotFoundError:
        return ["FAIL", f"Backend not found at {BACKEND_PATH}. Did you compile it?"]
    except Exception as exc:
        return ["FAIL", str(exc)]


# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------
class BankApp(tk.Tk):
    """Root window. Swaps between screens (Frames) as the user navigates."""

    def __init__(self):
        super().__init__()
        self.title("Banking App")
        self.geometry("420x420")
        self.resizable(False, False)

        self.session = {
            "id": None,
            "name": None,
            "balance": None,
            "type": None,
        }

        self.last_created_account = {
            "id": None,
            "name": None,
            "balance": None,
            "type": None,
        }

        # Container that all screens are stacked into.
        container = tk.Frame(self)
        container.pack(fill="both", expand=True)
        self.container = container

        self.frames = {}
        for ScreenClass in (
            WelcomeScreen,
            CreateAccountScreen,
            AccountCreatedScreen,
            FindAccountScreen,
            PasswordScreen,
            AccountDetailsScreen,
        ):
            frame = ScreenClass(container, self)
            self.frames[ScreenClass] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.show_screen(WelcomeScreen)

    def show_screen(self, screen_class):
        """Raises the requested screen to the top and lets it refresh itself."""
        frame = self.frames[screen_class]
        if hasattr(frame, "on_show"):
            frame.on_show()
        frame.tkraise()


# ---------------------------------------------------------------------------
# Screen 1: Welcome - "Create New Account" or "Find Account"
# ---------------------------------------------------------------------------
class WelcomeScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        tk.Label(self, text="Welcome to the Bank", font=("Helvetica", 20, "bold")).pack(pady=(60, 10))
        tk.Label(self, text="What would you like to do?", font=("Helvetica", 12)).pack(pady=(0, 40))

        tk.Button(
            self, text="Create New Account", width=25, height=2,
            command=lambda: app.show_screen(CreateAccountScreen)
        ).pack(pady=10)

        tk.Button(
            self, text="Find Account", width=25, height=2,
            command=lambda: app.show_screen(FindAccountScreen)
        ).pack(pady=10)


# ---------------------------------------------------------------------------
# Screen 2: Create New Account
# ---------------------------------------------------------------------------
class CreateAccountScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        tk.Label(self, text="Create New Account", font=("Helvetica", 16, "bold")).pack(pady=(30, 20))

        form = tk.Frame(self)
        form.pack(pady=5)

        tk.Label(form, text="Name:").grid(row=0, column=0, sticky="e", padx=5, pady=8)
        self.name_var = tk.StringVar()
        tk.Entry(form, textvariable=self.name_var, width=25).grid(row=0, column=1, pady=8)

        tk.Label(form, text="Password:").grid(row=1, column=0, sticky="e", padx=5, pady=8)
        self.password_var = tk.StringVar()
        tk.Entry(form, textvariable=self.password_var, width=25, show="*").grid(row=1, column=1, pady=8)

        tk.Label(form, text="Initial Deposit:").grid(row=2, column=0, sticky="e", padx=5, pady=8)
        self.balance_var = tk.StringVar(value="0")
        tk.Entry(form, textvariable=self.balance_var, width=25).grid(row=2, column=1, pady=8)

        tk.Label(form, text="Account Type:").grid(row=3, column=0, sticky="e", padx=5, pady=8)
        self.type_var = tk.StringVar(value="SAVINGS")
        type_frame = tk.Frame(form)
        type_frame.grid(row=3, column=1, sticky="w")
        tk.Radiobutton(type_frame, text="Savings", variable=self.type_var, value="SAVINGS").pack(side="left")
        tk.Radiobutton(type_frame, text="Current", variable=self.type_var, value="CURRENT").pack(side="left")

        self.status_label = tk.Label(self, text="", fg="red")
        self.status_label.pack(pady=10)

        tk.Button(self, text="Create Account", width=20, command=self.create_account).pack(pady=5)
        tk.Button(self, text="Back", width=20, command=self.go_back).pack(pady=5)

    def on_show(self):
        # Reset the form each time this screen is opened.
        self.name_var.set("")
        self.password_var.set("")
        self.balance_var.set("0")
        self.type_var.set("SAVINGS")
        self.status_label.config(text="")

    def create_account(self):
        name = self.name_var.get().strip()
        password = self.password_var.get().strip()
        balance_text = self.balance_var.get().strip()
        acc_type = self.type_var.get()

        if not name or not password:
            self.status_label.config(text="Name and password are required.")
            return

        try:
            balance = float(balance_text)
            if balance < 0:
                raise ValueError()
        except ValueError:
            self.status_label.config(text="Initial deposit must be a non-negative number.")
            return

        response = run_backend("create", name, password, acc_type, balance)

        if response[0] == "SUCCESS":
            _, acc_id, acc_name, acc_balance, acc_type_out = response
            self.app.last_created_account.update({
                "id": acc_id,
                "name": acc_name,
                "balance": float(acc_balance),
                "type": acc_type_out,
            })
            self.app.show_screen(AccountCreatedScreen)
        else:
            self.status_label.config(text=response[1] if len(response) > 1 else "Failed to create account.")

    def go_back(self):
        self.app.show_screen(WelcomeScreen)


# ---------------------------------------------------------------------------
# Screen 2b: Account Created - shows full details right after creation
# ---------------------------------------------------------------------------
class AccountCreatedScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        tk.Label(self, text="Account Created!", font=("Helvetica", 18, "bold"), fg="green").pack(pady=(50, 10))
        tk.Label(
            self, text="Please remember your Account ID and password -\nyou'll need both to log in.",
            font=("Helvetica", 10), justify="center"
        ).pack(pady=(0, 20))

        info_frame = tk.Frame(self)
        info_frame.pack(pady=10)

        self.id_label = tk.Label(info_frame, text="", font=("Helvetica", 13, "bold"))
        self.id_label.grid(row=0, column=0, sticky="w", pady=4)
        self.name_label = tk.Label(info_frame, text="", font=("Helvetica", 11))
        self.name_label.grid(row=1, column=0, sticky="w", pady=4)
        self.type_label = tk.Label(info_frame, text="", font=("Helvetica", 11))
        self.type_label.grid(row=2, column=0, sticky="w", pady=4)
        self.balance_label = tk.Label(info_frame, text="", font=("Helvetica", 11))
        self.balance_label.grid(row=3, column=0, sticky="w", pady=4)

        tk.Button(self, text="Back to Main Menu", width=20, command=self.go_back).pack(pady=(30, 5))

    def on_show(self):
        acc = self.app.last_created_account
        self.id_label.config(text=f"Account ID: {acc['id']}")
        self.name_label.config(text=f"Name: {acc['name']}")
        self.type_label.config(text=f"Account Type: {acc['type']}")
        self.balance_label.config(text=f"Balance: ${acc['balance']:.2f}")

    def go_back(self):
        self.app.show_screen(WelcomeScreen)


# ---------------------------------------------------------------------------
# Screen 3: Find Account (by ID)
# ---------------------------------------------------------------------------
class FindAccountScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        tk.Label(self, text="Find Account", font=("Helvetica", 16, "bold")).pack(pady=(60, 20))
        tk.Label(self, text="Enter your Account ID:").pack(pady=5)

        self.id_var = tk.StringVar()
        tk.Entry(self, textvariable=self.id_var, width=20, justify="center").pack(pady=5)

        self.status_label = tk.Label(self, text="", fg="red")
        self.status_label.pack(pady=10)

        tk.Button(self, text="Find Account", width=20, command=self.find_account).pack(pady=5)
        tk.Button(self, text="Back", width=20, command=self.go_back).pack(pady=5)

    def on_show(self):
        self.id_var.set("")
        self.status_label.config(text="")

    def find_account(self):
        id_text = self.id_var.get().strip()
        if not id_text.isdigit():
            self.status_label.config(text="Please enter a valid numeric Account ID.")
            return

        response = run_backend("find", id_text)

        if response[0] == "SUCCESS":
            # Account exists, but we don't reveal any details until the
            # password screen has authenticated the user.
            self.app.session["id"] = id_text
            self.app.show_screen(PasswordScreen)
        else:
            self.status_label.config(text=response[1] if len(response) > 1 else "Account not found.")

    def go_back(self):
        self.app.show_screen(WelcomeScreen)


# ---------------------------------------------------------------------------
# Screen 4: Password prompt (protects account info)
# ---------------------------------------------------------------------------
class PasswordScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        tk.Label(self, text="Enter Password", font=("Helvetica", 16, "bold")).pack(pady=(60, 20))
        self.id_label = tk.Label(self, text="")
        self.id_label.pack(pady=5)

        self.password_var = tk.StringVar()
        entry = tk.Entry(self, textvariable=self.password_var, width=20, justify="center", show="*")
        entry.pack(pady=5)
        entry.bind("<Return>", lambda event: self.check_password())

        self.status_label = tk.Label(self, text="", fg="red")
        self.status_label.pack(pady=10)

        tk.Button(self, text="Submit", width=20, command=self.check_password).pack(pady=5)
        tk.Button(self, text="Back", width=20, command=self.go_back).pack(pady=5)

    def on_show(self):
        self.password_var.set("")
        self.status_label.config(text="")
        self.id_label.config(text=f"Account ID: {self.app.session['id']}")

    def check_password(self):
        acc_id = self.app.session["id"]
        password = self.password_var.get()

        if not password:
            self.status_label.config(text="Password is required.")
            return

        response = run_backend("auth", acc_id, password)

        if response[0] == "SUCCESS":
            _, rid, rname, rbalance, rtype = response
            self.app.session.update({
                "id": rid,
                "name": rname,
                "balance": float(rbalance),
                "type": rtype,
            })
            self.app.show_screen(AccountDetailsScreen)
        else:
            self.status_label.config(text=response[1] if len(response) > 1 else "Incorrect password.")

    def go_back(self):
        self.app.show_screen(FindAccountScreen)


# ---------------------------------------------------------------------------
# Screen 5: Account Details + Withdraw / Deposit
# ---------------------------------------------------------------------------
class AccountDetailsScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        tk.Label(self, text="Account Details", font=("Helvetica", 16, "bold")).pack(pady=(20, 10))

        info_frame = tk.Frame(self)
        info_frame.pack(pady=5)

        self.name_label = tk.Label(info_frame, text="", font=("Helvetica", 11))
        self.name_label.grid(row=0, column=0, sticky="w", pady=3)
        self.id_label = tk.Label(info_frame, text="", font=("Helvetica", 11))
        self.id_label.grid(row=1, column=0, sticky="w", pady=3)
        self.type_label = tk.Label(info_frame, text="", font=("Helvetica", 11))
        self.type_label.grid(row=2, column=0, sticky="w", pady=3)
        self.balance_label = tk.Label(info_frame, text="", font=("Helvetica", 13, "bold"))
        self.balance_label.grid(row=3, column=0, sticky="w", pady=(10, 3))

        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=20, pady=15)

        tk.Label(self, text="Amount:").pack()
        self.amount_var = tk.StringVar()
        tk.Entry(self, textvariable=self.amount_var, width=20, justify="center").pack(pady=5)

        self.status_label = tk.Label(self, text="", fg="red")
        self.status_label.pack(pady=5)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Deposit", width=12, command=self.deposit).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Withdraw", width=12, command=self.withdraw).grid(row=0, column=1, padx=5)

        tk.Button(self, text="Back", width=20, command=self.go_back).pack(pady=(15, 5))

    def on_show(self):
        self.refresh_labels()
        self.amount_var.set("")
        self.status_label.config(text="")

    def refresh_labels(self):
        session = self.app.session
        self.name_label.config(text=f"Name: {session['name']}")
        self.id_label.config(text=f"Account ID: {session['id']}")
        self.type_label.config(text=f"Account Type: {session['type']}")
        self.balance_label.config(text=f"Balance: ${session['balance']:.2f}")

    def _get_amount(self):
        try:
            amount = float(self.amount_var.get().strip())
            if amount <= 0:
                raise ValueError()
            return amount
        except ValueError:
            self.status_label.config(text="Please enter a valid positive amount.", fg="red")
            return None

    def deposit(self):
        amount = self._get_amount()
        if amount is None:
            return
        self._transact("deposit", amount)

    def withdraw(self):
        amount = self._get_amount()
        if amount is None:
            return
        self._transact("withdraw", amount)

    def _transact(self, kind, amount):
        session = self.app.session
        # NOTE: we already authenticated on the password screen; the backend
        # still re-checks the password on every transaction as a safety net,
        # so we keep it cached in this simple demo rather than asking again.
        response = run_backend(kind, session["id"], self._cached_password(), amount)

        if response[0] == "SUCCESS":
            new_balance = float(response[1])
            session["balance"] = new_balance
            self.refresh_labels()
            self.amount_var.set("")
            self.status_label.config(text=f"{kind.capitalize()} successful.", fg="green")
        else:
            self.status_label.config(text=response[1] if len(response) > 1 else "Transaction failed.", fg="red")

    def _cached_password(self):
        # The password itself is intentionally not stored in self.app.session
        # (which holds account details shown on screen); it's kept only on
        # the PasswordScreen widget for re-use during this session.
        return self.app.frames[PasswordScreen].password_var.get()

    def go_back(self):
        self.app.show_screen(WelcomeScreen)


if __name__ == "__main__":
    app = BankApp()
    app.mainloop()
