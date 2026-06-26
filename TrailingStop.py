import MetaTrader5 as mt5
import time

# ========================================================
# CONFIGURASI REVISI (TRIGGER MINIMAL PROFIT 1.7 POIN)
# ========================================================
SYMBOL_TARGET = ""            # Kosongin biar otomatis hajar semua pair (XAUUSD, XAUUSDm, dll)
TRIGGER_PROFIT_POIN = 1.7     # BOT BARU JALAN KALAU PROFIT SUDAH MINIMAL 1.7 POIN (17 Pips Gold)
FALLBACK_MEPET_POIN = 0.1     # Jarak aman jika broker setel Stops Level = 0
TRAILING_STEP_POIN = 0.02     # Seret SL tiap harga geser tipis biar ketat banget
JEDA_SCAN_DETIK = 0.2         # Speed scan kilat 0.2 detik biar gak kecolongan

def eksekusi_modifikasi_sl(ticket, sl_baru, tp_baru):
    request = {
        "action": mt5.TRADE_ACTION_SLTP,
        "position": ticket,
        "sl": float(sl_baru),
        "tp": float(tp_baru)
    }
    hasil = mt5.order_send(request)
    if hasil.retcode != mt5.TRADE_RETCODE_DONE:
        if hasil.retcode != 10016: # Abaikan error 10016 (harga loncat pas market ngebut)
            print(f"   [!] Gagal geser SL Tiket #{ticket}. Kode Error: {hasil.retcode}")

def pantau_dan_kunci_mepet():
    if SYMBOL_TARGET != "":
        positions = mt5.positions_get(symbol=SYMBOL_TARGET)
    else:
        positions = mt5.positions_get() # Ambil SEMUA posisi aktif

    if positions is None or len(positions) == 0:
        return 

    for pos in positions:
        ticket = pos.ticket
        tipe_trade = pos.type
        harga_open = pos.price_open
        harga_now = pos.price_current
        sl_now = pos.sl
        tp_now = pos.tp
        
        s_info = mt5.symbol_info(pos.symbol)
        if s_info is None:
            continue
            
        digits = s_info.digits
        point = s_info.point
        
        # Ambil Stops Level minimal broker
        stops_level_jarak = s_info.trade_stops_level * point
        if stops_level_jarak == 0:
            stops_level_jarak = FALLBACK_MEPET_POIN

        # ----------------------------------------------------
        # LOGIKA BUY (TRIGGER 1.7 POIN)
        # ----------------------------------------------------
        if tipe_trade == mt5.POSITION_TYPE_BUY:
            profit_poin = harga_now - harga_open
            
            # Bot baru bekerja kalau profit berjalan sudah melewati batas trigger
            if profit_poin >= TRIGGER_PROFIT_POIN:
                sl_ideal = round(harga_now - stops_level_jarak, digits)
                
                if sl_now == 0:
                    print(f"➔ [{pos.symbol}] BUY #{ticket} Tembus +{profit_poin:.2f} Poin! Pasang SL Kunci Profit: {sl_ideal}")
                    eksekusi_modifikasi_sl(ticket, sl_ideal, tp_now)
                else:
                    # Seret naik ketat mengikuti harga running
                    target_step = round(sl_now + TRAILING_STEP_POIN, digits)
                    if sl_ideal >= target_step:
                        print(f"➔ [{pos.symbol}] BUY #{ticket} Makin Naik! Seret SL: {sl_now} ➔ {sl_ideal}")
                        eksekusi_modifikasi_sl(ticket, sl_ideal, tp_now)

        # ----------------------------------------------------
        # LOGIKA SELL (TRIGGER 1.7 POIN)
        # ----------------------------------------------------
        elif tipe_trade == mt5.POSITION_TYPE_SELL:
            profit_poin = harga_open - harga_now
            
            # Bot baru bekerja kalau profit berjalan sudah melewati batas trigger
            if profit_poin >= TRIGGER_PROFIT_POIN:
                sl_ideal = round(harga_now + stops_level_jarak, digits)
                
                if sl_now == 0:
                    print(f"➔ [{pos.symbol}] SELL #{ticket} Tembus +{profit_poin:.2f} Poin! Pasang SL Kunci Profit: {sl_ideal}")
                    eksekusi_modifikasi_sl(ticket, sl_ideal, tp_now)
                else:
                    # Seret turun ketat mengikuti harga running
                    target_step = round(sl_now - TRAILING_STEP_POIN, digits)
                    if sl_ideal <= target_step:
                        print(f"➔ [{pos.symbol}] SELL #{ticket} Makin Turun! Seret SL: {sl_now} ➔ {sl_ideal}")
                        eksekusi_modifikasi_sl(ticket, sl_ideal, tp_now)

# ========================================================
# EXECUTION ENGINE
# ========================================================
if not mt5.initialize():
    print("[!] Gagal koneksi ke MT5.")
    quit()

print(f"[+] BOT AKTIF! Nunggu Profit Menyentuh {TRIGGER_PROFIT_POIN} Poin Baru Dikunci Mepet...")

while True:
    try:
        pantau_dan_kunci_mepet()
    except Exception as e:
        print(f"[!] Terjadi masalah: {e}")
    time.sleep(JEDA_SCAN_DETIK)
