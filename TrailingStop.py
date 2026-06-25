# Jika posisi sekarang adalah BUY
if posisi_sekarang == "BUY":
    harga_tertinggi = max(harga_tertinggi, harga_sekarang)
    if harga_tertinggi >= entry_price + 2.000:
        sl_seharusnya = harga_tertinggi - 0.300
        if sl_seharusnya > current_sl:
            current_sl = sl_seharusnya

# Jika posisi sekarang adalah SELL
elif posisi_sekarang == "SELL":
    harga_terendah = min(harga_terendah, harga_sekarang) # Catat harga paling rendah
    if harga_terendah <= entry_price - 2.000:            # Cek apakah sudah turun 20 pips
        sl_seharusnya = harga_terendah + 0.300          # Jarak trailing di atas harga terendah
        if sl_seharusnya < current_sl or current_sl == 0: # SL hanya boleh makin turun
            current_sl = sl_seharusnya
            print(f"SL SELL Auto Turun ke: {current_sl}")
