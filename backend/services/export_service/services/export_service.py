"""
Export Service — Business Logic
"""

from services.export_service.models.schemas import ExportRequest, ExportResponse
from services.export_service.utils.exporters import export_txt, export_docx, export_pdf
from shared.error_handler.exceptions import UnsupportedFormatException, ExportException
from shared.logger.logger import get_logger

logger = get_logger(__name__)


class ExportService:
    async def export(self, request: ExportRequest) -> tuple[bytes, str, str]:
        """
        Export content to the requested format.
        Returns (bytes, content_type, filename).
        """
        try:
            if request.format == "txt":
                content = await export_txt(request.content, request.title)
                return content, "text/plain", f"{request.title}.txt"
            elif request.format == "docx":
                content = await export_docx(request.content, request.title)
                return content, "application/vnd.openxmlformats-officedocument.wordprocessingml.document", f"{request.title}.docx"
            elif request.format == "pdf":
                content = await export_pdf(request.content, request.title, request.language)
                return content, "application/pdf", f"{request.title}.pdf"
            else:
                raise UnsupportedFormatException(
                    f"Unsupported export format: '{request.format}'. Use txt, docx, or pdf."
                )
        except (UnsupportedFormatException,):
            raise
        except Exception as e:
            logger.error("export_error", format=request.format, error=str(e))
            raise ExportException("Export failed. Please try a different format.")
