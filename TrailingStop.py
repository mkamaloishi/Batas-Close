import MetaTrader5 as mt5
import time

# ========================================================
# CONFIGURASI SAKLEK (ANY PROFIT - AUTO MEPEET STOPS LEVEL)
# ========================================================
SYMBOL_TARGET = "XAUUSD"      
FALLBACK_MEPET_POIN = 0.1     # Jarak aman (1 pip Gold) jika broker setel Stops Level = 0
TRAILING_STEP_POIN = 0.02     # Seret SL tiap harga geser tipis biar ketat banget
JEDA_SCAN_DETIK = 0.5         # Kecepatan scan kilat setengah detik

def eksekusi_modifikasi_sl(ticket, sl_baru, tp_baru):
    request = {
        "action": mt5.TRADE_ACTION_SLTP,
        "position": ticket,
        "sl": float(sl_baru),
        "tp": float(tp_baru)
    }
    hasil = mt5.order_send(request)
    if hasil.retcode != mt5.TRADE_RETCODE_DONE:
        # Kode 10016 artinya direject broker karena terlalu dekat / Stops Level melar pas market ngebut
        if hasil.retcode == 10016:
            pass 
        else:
            print(f"   [!] Gagal geser SL Tiket #{ticket}. Kode Error: {hasil.retcode}")

def pantau_dan_kunci_mepet():
    if SYMBOL_TARGET != "":
        positions = mt5.positions_get(symbol=SYMBOL_TARGET)
        symbol_info = mt5.symbol_info(SYMBOL_TARGET)
    else:
        positions = mt5.positions_get()
        symbol_info = None

    if positions is None or len(positions) == 0:
        return 

    for pos in positions:
        ticket = pos.ticket
        tipe_trade = pos.type
        harga_open = pos.price_open
        harga_now = pos.price_current
        sl_now = pos.sl
        tp_now = pos.tp
        
        # Ambil spesifikasi simbol (buat jaga-jaga kalau ganti pair)
        s_info = symbol_info if SYMBOL_TARGET != "" else mt5.symbol_info(pos.symbol)
        if s_info is None:
            continue
            
        digits = s_info.digits
        point = s_info.point
        
        # OTOMATIS NGINTIP BATAS MINIMAL (STOPS LEVEL) BROKER DETIK INI
        stops_level_jarak = s_info.trade_stops_level * point
        if stops_level_jarak == 0:
            stops_level_jarak = FALLBACK_MEPET_POIN

        # ----------------------------------------------------
        # LOGIKA BUY (ANY PROFIT - TEMPEL BATAS BAWAH SPREAD)
        # ----------------------------------------------------
        if tipe_trade == mt5.POSITION_TYPE_BUY:
            if harga_now > harga_open: # Lolos spread & ijo bersih!
                sl_ideal = round(harga_now - stops_level_jarak, digits)
                
                if sl_now == 0:
                    print(f"➔ [{pos.symbol}] BUY #{ticket} Ijo! Pasang SL Mepet Broker: {sl_ideal}")
                    eksekusi_modifikasi_sl(ticket, sl_ideal, tp_now)
                else:
                    # Geser naik terus tanpa ampun tiap menyentuh step minimum
                    target_step = round(sl_now + TRAILING_STEP_POIN, digits)
                    if sl_ideal >= target_step:
                        print(f"➔ [{pos.symbol}] BUY #{ticket} Naik! Seret SL: {sl_now} ➔ {sl_ideal}")
                        eksekusi_modifikasi_sl(ticket, sl_ideal, tp_now)

        # ----------------------------------------------------
        # LOGIKA SELL (ANY PROFIT - TEMPEL BATAS ATAS SPREAD)
        # ----------------------------------------------------
        elif tipe_trade == mt5.POSITION_TYPE_SELL:
            if harga_now < harga_open: # Lolos spread & ijo bersih!
                sl_ideal = round(harga_now + stops_level_jarak, digits)
                
                if sl_now == 0:
                    print(f"➔ [{pos.symbol}] SELL #{ticket} Ijo! Pasang SL Mepet Broker: {sl_ideal}")
                    eksekusi_modifikasi_sl(ticket, sl_ideal, tp_now)
                else:
                    # Geser turun terus tanpa ampun tiap menyentuh step minimum
                    target_step = round(sl_now - TRAILING_STEP_POIN, digits)
                    if sl_ideal <= target_step:
                        print(f"➔ [{pos.symbol}] SELL #{ticket} Turun! Seret SL: {sl_now} ➔ {sl_ideal}")
                        eksekusi_modifikasi_sl(ticket, sl_ideal, tp_now)

# ========================================================
# EXECUTION ENGINE
# ========================================================
if not mt5.initialize():
    print("[!] Gagal koneksi ke MT5.")
    quit()

print("[+] BOT AKTIF! Mode: Any Profit Mepet Broker (Selagi bisa ditaroh, langsung taroh)...")

while True:
    try:
        pantau_dan_kunci_mepet()
    except Exception as e:
        print(f"[!] Terjadi masalah: {e}")
    time.sleep(JEDA_SCAN_DETIK)
