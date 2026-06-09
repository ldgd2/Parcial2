"""fix_vps_deuda_acumulada

Revision ID: 8e3905619334
Revises: 7087994e3fa8
Create Date: 2026-06-08 20:21:28.228123

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8e3905619334'
down_revision: Union[str, None] = '7087994e3fa8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Agregamos la columna usando raw SQL con IF NOT EXISTS para que funcione tanto si
    # la columna ya existe (local) como si no existe (VPS desincronizado).
    op.execute("ALTER TABLE public.emergencia ADD COLUMN IF NOT EXISTS deuda_acumulada FLOAT NOT NULL DEFAULT 0.0;")


def downgrade() -> None:
    # No hacemos drop column aquí para no arriesgarnos a borrar datos accidentalmente
    pass
