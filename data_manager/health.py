from django.db import connection
from django.http import JsonResponse
from django.views import View

from data_manager.models import CropRecord


class HealthView(View):
    def get(self, request):
        db_ok = True
        tables_ok = True
        error = ""

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        except Exception as exc:
            db_ok = False
            error = str(exc)

        try:
            CropRecord.objects.count()
        except Exception as exc:
            tables_ok = False
            if not error:
                error = str(exc)

        status = 200 if db_ok and tables_ok else 503
        return JsonResponse(
            {
                "status": "ok" if status == 200 else "error",
                "database": db_ok,
                "tables": tables_ok,
                "detail": error,
            },
            status=status,
        )
