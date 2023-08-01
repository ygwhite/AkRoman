import os, io, zipfile
from django.http import HttpResponse
from django.conf import settings

from customers.models import Customer


def home(req, *args, **kwargs):
    return HttpResponse(
        f"""
<p> 
    <a href="https://t.me/hotalgobot?start=123">Ссылка на бота</a>
</p>
    """
    )


def get_logs_zip(req, *args, **kwargs):
    if req.user.is_authenticated:
        file_name = "logs.zip"
        logs_path = settings.BASE_DIR / "logs"

        try:
            buffer = io.BytesIO()

            with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for root, dirs, files in os.walk(logs_path):
                    for file in files:
                        zip_file.write(
                            os.path.join(root, file),
                            os.path.relpath(
                                os.path.join(root, file),
                                os.path.join(logs_path, '..')
                            )
                        )

            response = HttpResponse(buffer.getvalue(),
                                    content_type='application/zip',
                                    status=200)
            response['Content-Disposition'] = f'attachment; filename={file_name}'

            return response

        except Exception as e:
            return HttpResponse("Something went wrong", status=500)
    else:
        return HttpResponse("You are not authenticated.")
