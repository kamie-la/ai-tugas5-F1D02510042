#!/usr/bin/env python3
"""Sistem Pakar Identifikasi Jenis Noda Pakaian dan Metode Pembersihannya.

Metode : Forward Chaining (mesin inferensi ditulis sendiri, tanpa library eksternal)
Jalankan:
    python sistem_pakar.py                      # mode interaktif
    python sistem_pakar.py --ya "fakta1;fakta2" # mode otomatis (untuk kasus uji)
Python 3.8+
"""
import argparse
import json
import os
import sys

FILE_ATURAN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kb_noda.json")


def muat_kb(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def fakta_dasar(aturan):
    """Fakta yang tidak pernah menjadi hasil aturan -> ditanyakan ke user (urutan kemunculan)."""
    hasil = {r["maka"] for r in aturan}
    urut = []
    for r in aturan:
        for syarat in r["jika"]:
            if syarat not in hasil and syarat not in urut:
                urut.append(syarat)
    return urut


def terpenuhi(aturan, memori):
    """mode 'dan' = semua syarat ada di memori, mode 'atau' = salah satu ada."""
    ada = [s in memori for s in aturan["jika"]]
    return all(ada) if aturan["mode"] == "dan" else any(ada)


def forward_chaining(aturan, fakta_ya):
    """Kembalikan (memori, asal, log).

    asal[x] = aturan yang menghasilkan x (bahan penyusun 'alasan').
    """
    memori = set(fakta_ya)
    asal = {}
    log = []
    siklus = 0
    while True:
        # aturan yang syaratnya terpenuhi DAN hasilnya belum ada di memori
        cocok = [r for r in aturan if terpenuhi(r, memori) and r["maka"] not in memori]
        if not cocok:
            log.append("Siklus %d: tidak ada aturan baru, berhenti" % (siklus + 1))
            break
        r = cocok[0]  # ambil aturan pertama
        siklus += 1
        memori.add(r["maka"])
        asal[r["maka"]] = r
        log.append("Siklus %d: %s -> %s" % (siklus, r["id"], r["maka"]))
    return memori, asal, log


def alasan(kesimpulan, asal, memori, tingkat=0, sudah=None):
    """Telusuri mundur aturan yang dipakai untuk sebuah kesimpulan."""
    if sudah is None:
        sudah = set()
    if kesimpulan not in asal or kesimpulan in sudah:
        return []
    sudah.add(kesimpulan)
    r = asal[kesimpulan]
    dipakai = [s for s in r["jika"] if s in memori]
    baris = ["  " * tingkat + "%s <- %s (%s)" % (kesimpulan, r["id"], ", ".join(dipakai))]
    for s in dipakai:
        baris += alasan(s, asal, memori, tingkat + 1, sudah)
    return baris


def tanya(pertanyaan_ke, fakta, otomatis_ya):
    print("Jawab y/t.")
    ya = []
    for i, f in enumerate(fakta, 1):
        if otomatis_ya is None:
            while True:
                j = input("%d. Apakah %s? (y/t) > " % (i, f)).strip().lower()
                if j in ("y", "t"):
                    break
                print("   Ketik y atau t saja.")
        else:
            j = "y" if f in otomatis_ya else "t"
            print("%d. Apakah %s? (y/t) > %s" % (i, f, j))
        if j == "y":
            ya.append(f)
    return ya


def main():
    ap = argparse.ArgumentParser(description="Sistem pakar identifikasi noda pakaian")
    ap.add_argument("--ya", help="daftar fakta yang dijawab 'ya', dipisah titik koma (mode otomatis)")
    ap.add_argument("--kb", default=FILE_ATURAN, help="path file aturan JSON")
    args = ap.parse_args()

    kb = muat_kb(args.kb)
    aturan = kb["aturan"]
    fakta = fakta_dasar(aturan)

    otomatis = None
    if args.ya is not None:
        otomatis = [x.strip() for x in args.ya.split(";") if x.strip()]
        tak_dikenal = [x for x in otomatis if x not in fakta]
        if tak_dikenal:
            print("Fakta tidak dikenal:", tak_dikenal)
            sys.exit(2)

    print(kb["judul"])
    ya = tanya(None, fakta, otomatis)
    print()
    print("Fakta awal: " + (", ".join(ya) if ya else "(tidak ada)"))

    memori, asal, log = forward_chaining(aturan, ya)
    for baris in log:
        print(baris)
    print()

    jenis = [r for r in aturan if r["maka"] in asal and r["tipe"] == "jenis"]
    metode = [r for r in aturan if r["maka"] in asal and r["tipe"] == "metode"]
    peringatan = [r for r in aturan if r["maka"] in asal and r["tipe"] == "peringatan"]

    if not (jenis or metode or peringatan):
        print("Kesimpulan: tidak ada kesimpulan yang dapat ditarik dari fakta tersebut.")
        print("Saran: jelaskan asal noda (misalnya berminyak, darah, kopi, tinta) lalu coba lagi.")
    else:
        print("Jenis noda:")
        for r in jenis:
            print("  - " + r["maka"])
        print("Metode pembersihan:")
        for n, r in enumerate(metode, 1):
            print("  %d. %s: %s" % (n, r["maka"], r["saran"]))
        for r in peringatan:
            print("Peringatan: %s" % r["saran"])
        print()
        print("Alasan:")
        for r in jenis + metode + peringatan:
            for baris in alasan(r["maka"], asal, memori):
                print("  " + baris)
        print()
        print("Sumber aturan yang dipakai:")
        dipakai = sorted({s for r in (jenis + metode + peringatan) for s in r["sumber"]},
                         key=lambda x: int(x[1:]))
        for s in dipakai:
            print("  [%s] %s" % (s, kb["sumber"][s]))

    print()
    print("Catatan: " + kb["batas"])


if __name__ == "__main__":
    main()
