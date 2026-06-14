from app.database import Base
# Import all models here so Alembic can discover them
from app.models.analysis import Analysis, ModalityResult, Report, ChatMessage
