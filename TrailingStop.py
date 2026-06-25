import MetaTrader5 as mt5
import time

# ========================================================
# KONSOL CONFIGURASI (BISA LU UBAH SESUAI SELERA)
# ========================================================
SYMBOL_TARGET = "XAUUSD"      # Ketik "" jika ingin mengelola semua pair sekaligus
TRAILING_STOP_POIN = 2.0     # Jarak SL dari harga sekarang (2.0 Poin = 20 Pips di Gold)
TRAILING_STEP_POIN = 0.3     # SL baru hanya akan di-update jika harga sudah bergerak sejauh ini
JEDA_SCAN_DETIK = 1         # Kecepatan bot nge-scan market (1 detik sekali)

def hubungkan_ke_mt5():
    if not mt5.initialize():
        print("[-] Gagal mengubungkan ke MT5. Pastikan aplikasi MT5 di laptop lu sudah terbuka!")
        return False
    print("[+] Sukses Terhubung ke MT5! Bot Trailing SL Siap Menjaga.")
    return True

def eksekusi_modifikasi_sl(ticket, sl_baru, tp_lama):
    # Kirim perintah revisi ke server Broker
    request = {
        "action": mt5.TRADE_ACTION_SLTP,
        "position": ticket,
        "sl": round(sl_baru, 2), # Dibulatkan 2 desimal khas Gold (XAUUSD)
        "tp": tp_lama
    }
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"[-] Gagal geser SL untuk Tiket #{ticket} | Alasan: {result.comment}")
    else:
        print(f"[+] LOCK PROFIT AKTIF! Tiket #{ticket} | SL berhasil digeser ke: {round(sl_baru, 2)}")

def pantau_dan_kunci_posisi():
    # Ambil data posisi trade yang lagi berjalan
    if SYMBOL_TARGET != "":
        positions = mt5.positions_get(symbol=SYMBOL_TARGET)
    else:
        positions = mt5.positions_get()

    if positions is None or len(positions) == 0:
        return # Gak ada trade aktif, balik kanan bubar jalan

    for pos in positions:
        ticket = pos.ticket
        tipe_trade = pos.type
        harga_open = pos.price_open
        harga_now = pos.price_current
        sl_now = pos.sl
        tp_now = pos.tp

        # ----------------------------------------------------
        # LOGIKA TRAILING STOP UNTUK POSISI BUY
        # ----------------------------------------------------
        if tipe_trade == mt5.POSITION_TYPE_BUY:
            sl_ideal_baru = harga_now - TRAILING_STOP_POIN
            
            # Kondisi A: Belum ada SL, dan harga udah naik sejauh batas trailing dari harga entry
            if sl_now == 0:
                if harga_now > (harga_open + TRAILING_STOP_POIN):
                    eksekusi_modifikasi_sl(ticket, sl_ideal_baru, tp_now)
            
            # Kondisi B: Sudah ada SL, harga makin naik tinggi melampaui STEP
            elif sl_ideal_baru > (sl_now + TRAILING_STEP_POIN):
                eksekusi_modifikasi_sl(ticket, sl_ideal_baru, tp_now)

        # ----------------------------------------------------
        # LOGIKA TRAILING STOP UNTUK POSISI SELL
        # ----------------------------------------------------
        elif tipe_trade == mt5.POSITION_TYPE_SELL:
            sl_ideal_baru = harga_now + TRAILING_STOP_POIN
            
            # Kondisi A: Belum ada SL, dan harga udah terjun sejauh batas trailing dari harga entry
            if sl_now == 0:
                if harga_now < (harga_open - TRAILING_STOP_POIN):
                    eksekusi_modifikasi_sl(ticket, sl_ideal_baru, tp_now)
            
            # Kondisi B: Sudah ada SL, harga makin terjun bebas melampaui STEP
            elif sl_ideal_baru < (sl_now - TRAILING_STEP_POIN):
                eksekusi_modifikasi_sl(ticket, sl_ideal_baru, tp_now)

if __name__ == "__main__":
    if hubungkan_ke_mt5():
        try:
            while True:
                pantau_dan_kunci_posisi()
                time.sleep(JEDA_SCAN_DETIK)
        except KeyboardInterrupt:
            print("\n[-] Bot dimatikan secara manual oleh user.")
        finally:
            mt5.shutdown()
