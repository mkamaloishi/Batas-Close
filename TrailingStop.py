# ========================================================
# CONFIGURASI SAKLEK (BUY 4002 -> 4004 -> SL 4003.5 -> JALAN PER 0.3)
# ========================================================
SYMBOL_TARGET = "XAUUSD"      
TRIGGER_PROFIT_POIN = 2.0     # Harga naik 2.0 poin baru bot aktif (4002 ke 4004)
TRAILING_DISTANCE_POIN = 0.5  # Jarak SL di belakang harga running (4004 - 0.5 = 4003.5)
TRAILING_STEP_POIN = 0.3      # SL BARU IKUT BERGESER TIAP ADA KENAIKAN 0.3 POIN
JEDA_SCAN_DETIK = 1         

def pantau_dan_kunci_posisi():
    if SYMBOL_TARGET != "":
        positions = mt5.positions_get(symbol=SYMBOL_TARGET)
    else:
        positions = mt5.positions_get()

    if positions is None or len(positions) == 0:
        return 

    for pos in positions:
        ticket = pos.ticket
        tipe_trade = pos.type
        harga_open = pos.price_open
        harga_now = pos.price_current
        sl_now = pos.sl
        tp_now = pos.tp

        # ----------------------------------------------------
        # LOGIKA BUY (TRAIL JALAN TIAP NAIK 0.3 POIN)
        # ----------------------------------------------------
        if tipe_trade == mt5.POSITION_TYPE_BUY:
            sl_ideal_baru = harga_now - TRAILING_DISTANCE_POIN
            
            if harga_now >= (harga_open + TRIGGER_PROFIT_POIN):
                
                # 1. Kancingan pertama pas running touch 4004.0 -> SL pasang di 4003.5
                if sl_now == 0:
                    eksekusi_modifikasi_sl(ticket, sl_ideal_baru, tp_now)
                
                # 2. SL baru ikut bergeser naik jika jarak SL baru ke SL lama minimal 0.3 poin
                elif sl_ideal_baru >= (sl_now + TRAILING_STEP_POIN):
                    eksekusi_modifikasi_sl(ticket, sl_ideal_baru, tp_now)

        # ----------------------------------------------------
        # LOGIKA SELL (TRAIL JALAN TIAP TURUN 0.3 POIN)
        # ----------------------------------------------------
        elif tipe_trade == mt5.POSITION_TYPE_SELL:
            sl_ideal_baru = harga_now + TRAILING_DISTANCE_POIN
            
            if harga_now <= (harga_open - TRIGGER_PROFIT_POIN):
                
                # 1. Kancingan pertama pas running profit 2.0 poin
                if sl_now == 0:
                    eksekusi_modifikasi_sl(ticket, sl_ideal_baru, tp_now)
                
                # 2. SL baru ikut bergeser turun jika jarak SL baru ke SL lama minimal 0.3 poin
                elif sl_ideal_baru <= (sl_now - TRAILING_STEP_POIN):
                    eksekusi_modifikasi_sl(ticket, sl_ideal_baru, tp_now)
