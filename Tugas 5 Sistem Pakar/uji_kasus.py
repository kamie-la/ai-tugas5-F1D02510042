"""Uji otomatis: memastikan kesimpulan sesuai harapan. Jalankan: python uji_kasus.py"""
import os
from sistem_pakar import muat_kb, forward_chaining, FILE_ATURAN

KASUS = [
    ("Kasus 1 - noda minyak",
     ["noda teraba licin atau berminyak", "noda berasal dari masakan berlemak, oli, atau minyak goreng"],
     {"noda minyak/lemak"}),
    ("Kasus 2 - noda darah, masih membekas, kain tahan pemutih",
     ["noda berasal dari darah, daging, ikan, telur, atau susu",
      "noda masih terlihat setelah dicuci", "kain tahan pemutih"],
     {"noda protein (darah, telur, susu, keringat)", "metode lanjutan pemutih"}),
    ("Kasus 3 - kombinasi minyak + protein",
     ["noda teraba licin atau berminyak", "noda berasal dari darah, daging, ikan, telur, atau susu"],
     {"noda minyak/lemak", "noda protein (darah, telur, susu, keringat)",
      "noda kombinasi (minyak + protein)"}),
    ("Kasus 4 - tinta pulpen",
     ["noda berasal dari pulpen atau spidol"], {"noda tinta"}),
    ("Kasus 5 - noda tidak diketahui",
     ["asal noda tidak diketahui"], {"noda tidak dikenal"}),
    ("Kasus 6 - negatif (hanya kain tahan pemutih)",
     ["kain tahan pemutih"], set()),
]

kb = muat_kb(FILE_ATURAN)
akhir = {r["maka"] for r in kb["aturan"] if r["tipe"] in ("jenis", "metode", "peringatan")}
gagal = 0
for nama, ya, harap in KASUS:
    memori, _, _ = forward_chaining(kb["aturan"], ya)
    didapat = memori & akhir
    ok = harap <= didapat and (harap or not didapat)
    print("%s %s" % ("LULUS" if ok else "GAGAL", nama))
    if not ok:
        gagal += 1
        print("   harapan:", harap, "| didapat:", didapat)
raise SystemExit(1 if gagal else 0)
