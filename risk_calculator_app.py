import tkinter as tk
from tkinter import messagebox
import json
import os
from datetime import datetime, time, timedelta

# ================= SETTINGS =================

SAVE_FILE = "risk_data.json"

START_EQUITY = 5000
TARGET_EQUITY = 5500
PERSONAL_DAILY_CAP = 100
ASSET_CAP = 150
FAIL_EQUITY = 4500

RESET_TIME = time(7, 30)

ASSETS = {
    "BTCUSDT": {"type": "crypto", "lev": 2},
    "ETHUSDT": {"type": "crypto", "lev": 2},
    "SOLUSDT": {"type": "crypto", "lev": 2},
    "XRPUSDT": {"type": "crypto", "lev": 2},
    "XAUUSD": {"type": "gold", "lev": 30},
    "EURUSD": {"type": "forex", "lev": 50},
    "USDJPY": {"type": "forex", "lev": 50},
}

# ================= STATE =================

def load_state():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                data = json.load(f)
        except:
            data = {}
    else:
        data = {}

    data.setdefault("equity", START_EQUITY)
    data.setdefault("personal_loss", 0)
    data.setdefault("asset_risk", {})
    data.setdefault("trades", {})
    data.setdefault("last_reset", str(datetime.now().date()))

    check_daily_reset(data)
    return data


def check_daily_reset(data):
    now = datetime.now()
    last = datetime.strptime(data["last_reset"], "%Y-%m-%d").date()

    if now.date() > last and now.time() >= RESET_TIME:
        data["personal_loss"] = 0
        data["asset_risk"] = {}
        data["trades"] = {}
        data["last_reset"] = str(now.date())


state = load_state()


def save_state():
    with open(SAVE_FILE, "w") as f:
        json.dump(state, f)


# ================= RESET =================

def reset_day():
    if not messagebox.askyesno("Reset", "Reset all trades today?"):
        return

    state["equity"] = float(equity_entry.get() or START_EQUITY)
    state["personal_loss"] = 0
    state["asset_risk"] = {}
    state["trades"] = {}
    state["last_reset"] = str(datetime.now().date())

    save_state()
    update_status()


# ================= POSITION CALC =================

def calculate_trade():
    try:
        price = float(price_entry.get())
        sl = float(sl_entry.get())
        asset = asset_var.get()
    except:
        messagebox.showerror("Error", "Enter valid numbers.")
        return

    config = ASSETS[asset]
    lev = config["lev"]
    a_type = config["type"]

    if a_type == "crypto":
        size = 30 / sl
        trade_value = size * price
        unit = f"{size:.6f} {asset.replace('USDT','')}"

    elif a_type == "gold":
        size = 30 / (sl * 100)
        trade_value = size * 100 * price
        unit = f"{size:.3f} lots"

    else:
        size = 30 / (sl * 100000)
        trade_value = size * 100000 * price
        unit = f"{size:.3f} lots"

    margin = trade_value / lev

    output_var.set(
        f"Trade Value: ${trade_value:,.0f}\n"
        f"Margin: ${margin:,.0f}\n"
        f"Size: {unit}"
    )


# ================= CONFIRM TRADE =================

def confirm_trade():
    asset = asset_var.get()

    try:
        new_equity = float(equity_entry.get())
    except:
        messagebox.showerror("Error", "Enter valid equity.")
        return

    old_equity = state["equity"]
    change = new_equity - old_equity

    # ===== PROFIT =====
    if change > 0:
        state["equity"] = new_equity
        save_state()
        update_status()
        messagebox.showinfo("Profit Recorded", f"+${change:.2f}")
        return

    # ===== LOSS =====
    loss = abs(change)

    if state["personal_loss"] + loss > PERSONAL_DAILY_CAP:
        messagebox.showwarning("Blocked", "Personal daily loss exceeded.")
        return

    asset_risk = state["asset_risk"].get(asset, 0)

    if asset_risk + loss > ASSET_CAP:
        messagebox.showwarning("Blocked", f"{asset} risk cap exceeded.")
        return

    if new_equity < FAIL_EQUITY:
        messagebox.showwarning("Blocked", "Would breach failure equity.")
        return

    if not messagebox.askyesno("Confirm", f"Record loss of ${loss:.2f}?"):
        return

    state["equity"] = new_equity
    state["personal_loss"] += loss
    state["asset_risk"][asset] = asset_risk + loss
    state["trades"][asset] = state["trades"].get(asset, 0) + 1

    save_state()
    update_status()


# ================= TIME TO RESET =================

def time_until_reset():
    now = datetime.now()
    reset_dt = datetime.combine(now.date(), RESET_TIME)

    if now >= reset_dt:
        reset_dt += timedelta(days=1)

    diff = reset_dt - now
    h, r = divmod(diff.seconds, 3600)
    m = r // 60
    return f"{h}h {m}m"


# ================= STATUS =================

def update_status():
    asset = asset_var.get()

    asset_risk = state["asset_risk"].get(asset, 0)
    trades_today = sum(state["trades"].values())

    trades_left = max(0, (PERSONAL_DAILY_CAP - state["personal_loss"]) // 30)

    profit = state["equity"] - START_EQUITY
    remaining = TARGET_EQUITY - state["equity"]

    status_var.set(
        f"Equity: ${state['equity']:,.0f}\n"
        f"Fail Level: ${FAIL_EQUITY}\n\n"
        f"Personal Loss: ${state['personal_loss']} / $100\n"
        f"Trades Left Today: {trades_left}\n\n"
        f"{asset} Risk Used: ${asset_risk} / $150\n"
        f"Total Trades Today: {trades_today}\n\n"
        f"Profit: ${profit:+,.0f}\n"
        f"To Target: ${remaining:,.0f}\n\n"
        f"Reset In: {time_until_reset()}"
    )


# ================= UI =================

root = tk.Tk()
root.title("Risk Calculator")
root.geometry("470x650")

tk.Button(root, text="Reset Day", command=reset_day,
          bg="red", fg="white").place(x=380, y=10)

tk.Label(root, text="Prop Risk Calculator",
         font=("Arial", 16)).pack(pady=15)

tk.Label(root, text="Asset").pack()
asset_var = tk.StringVar(value="BTCUSDT")
tk.OptionMenu(root, asset_var, *ASSETS.keys(),
              command=lambda _: update_status()).pack()

tk.Label(root, text="Current Price").pack()
price_entry = tk.Entry(root)
price_entry.pack()

tk.Label(root, text="Stop Distance (price units)").pack()
sl_entry = tk.Entry(root)
sl_entry.pack()

tk.Label(root, text="Current Equity").pack()
equity_entry = tk.Entry(root)
equity_entry.insert(0, str(state["equity"]))
equity_entry.pack()

tk.Button(root, text="Calculate Trade",
          command=calculate_trade).pack(pady=10)

tk.Button(root, text="Confirm Official Trade",
          command=confirm_trade).pack()

output_var = tk.StringVar()
tk.Label(root, textvariable=output_var,
         fg="blue").pack(pady=10)

status_var = tk.StringVar()
tk.Label(root, textvariable=status_var,
         fg="green", justify="left").pack()

update_status()

root.mainloop()