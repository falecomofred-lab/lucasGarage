"""
💾 BACKUP DO BANCO - Lucas Garage

Copia o banco (data/lucas_garage.db) para data/backups/ com data e hora no nome,
e mantém só os 20 backups mais recentes.

USAR:
    python backup_db.py

Para backup automático, agende este comando (Windows: Agendador de Tarefas;
PythonAnywhere: aba "Tasks" → agendar "python /home/SEU-USUARIO/lucasGarage/backup_db.py").
"""

import shutil
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).parent
DB = BASE / "data" / "lucas_garage.db"
BACKUP_DIR = BASE / "data" / "backups"
MANTER = 20  # quantos backups guardar


def backup():
    if not DB.exists():
        print(f"❌ Banco não encontrado em {DB}")
        return
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    carimbo = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = BACKUP_DIR / f"lucas_garage_{carimbo}.db"
    shutil.copy2(DB, destino)
    print(f"✅ Backup criado: {destino.name}")

    # limpa backups antigos (mantém os MANTER mais recentes)
    backups = sorted(BACKUP_DIR.glob("lucas_garage_*.db"), key=lambda p: p.stat().st_mtime, reverse=True)
    for velho in backups[MANTER:]:
        velho.unlink()
        print(f"🗑️  Removido backup antigo: {velho.name}")


if __name__ == "__main__":
    backup()
