import MetaTrader5 as mt5
import time

# ========================================================
# CONFIGURASI SAKLEK (UNTUNG 20 PIPS, SL NEMPEL 3 PIPS, SCAN KILAT)
# ========================================================
SYMBOL_TARGET = "XAUUSD"      
TRIGGER_PROFIT_POIN = 2.0     # Profit 20 pips baru bot aktif
TRAILING_DISTANCE_POIN = 0.3  # JARAK SL DI BELAKANG HARGA (3 PIPS SAKLEK)
TRAILING_STEP_POIN = 0.1      # Tiap untung nambah 0.1 poin, SL langsung diseret
JEDA_SCAN_DETIK = 0.5         # Kecepatan scan dipercepat jadi setengah detik biar gak lemot

def eksekusi_modifikasi_sl(ticket, sl_baru, tp_baru):
    request = {
        "action": mt5.TRADE_ACTION_SLTP,
        "position": ticket,
        "sl": float(sl_baru),
        "tp": float(tp_baru)
    }
    hasil = mt5.order_send(request)
    if hasil.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"   [!] Gagal geser SL Tiket #{ticket}. Kode Error: {hasil.retcode}")

def pantau_dan_kunci_posisi():
    if SYMBOL_TARGET != "":
        positions = mt5.positions_get(symbol=SYMBOL_TARGET)
        symbol_info = mt5.symbol_info(SYMBOL_TARGET)
        digits = symbol_info.digits if symbol_info is not None else 3
    else:
        positions = mt5.positions_get()
        digits = 3

    if positions is None or len(positions) == 0:
        return 

    for pos in positions:
        ticket = pos.ticket
        tipe_trade = pos.type
        harga_open = pos.price_open
        harga_now = pos.price_current
        sl_now = pos.sl
        tp_now = pos.tp
        
        if SYMBOL_TARGET == "":
            s_info = mt5.symbol_info(pos.symbol)
            digits = s_info.digits if s_info else 3

        # ----------------------------------------------------
        # LOGIKA BUY (NEMPEL KETAT 0.3 POIN)
        # ----------------------------------------------------
        if tipe_trade == mt5.POSITION_TYPE_BUY:
            sl_ideal_baru = round(harga_now - TRAILING_DISTANCE_POIN, digits)
            trigger_price = round(harga_open + TRIGGER_PROFIT_POIN, digits)
            
            if harga_now >= trigger_price:
                if sl_now == 0:
                    print(f"➔ [{pos.symbol}] BUY #{ticket} Aktif! SL awal: {sl_ideal_baru}")
                    eksekusi_modifikasi_sl(ticket, sl_ideal_baru, tp_now)
                else:
                    target_step_sl = round(sl_now + TRAILING_STEP_POIN, digits)
                    if sl_ideal_baru >= target_step_sl:
                        print(f"➔ [{pos.symbol}] BUY #{ticket} Running! Seret SL: {sl_now} ➔ {sl_ideal_baru}")
                        eksekusi_modifikasi_sl(ticket, sl_ideal_baru, tp_now)

        # ----------------------------------------------------
        # LOGIKA SELL (NEMPEL KETAT 0.3 POIN)
        # ----------------------------------------------------
        elif tipe_trade == mt5.POSITION_TYPE_SELL:
            sl_ideal_baru = round(harga_now + TRAILING_DISTANCE_POIN, digits)
            trigger_price = round(harga_open - TRIGGER_PROFIT_POIN, digits)
            
            if harga_now <= trigger_price:
                if sl_now == 0:
                    print(f"➔ [{pos.symbol}] SELL #{ticket} Aktif! SL awal: {sl_ideal_baru}")
                    eksekusi_modifikasi_sl(ticket, sl_ideal_baru, tp_now)
                else:
                    target_step_sl = round(sl_now - TRAILING_STEP_POIN, digits)
                    if sl_ideal_baru <= target_step_sl:
                        print(f"➔ [{pos.symbol}] SELL #{ticket} Running! Seret SL: {sl_now} ➔ {sl_ideal_baru}")
                        eksekusi_modifikasi_sl(ticket, sl_ideal_baru, tp_now)

# ========================================================
# RUNNING ENGINE UTAMA
# ========================================================
if not mt5.initialize():
    print("[!] Gagal menginisialisasi MT5.")
    quit()

print("[+] KODE BARU AKTIF! Bot Trailing Super Responsif Siap Menjaga...")

while True:
    try:
        pantau_dan_kunci_posisi()
    except Exception as e:
        print(f"[!] Terjadi error: {e}")
    time.sleep(JEDA_SCAN_DETIK)
