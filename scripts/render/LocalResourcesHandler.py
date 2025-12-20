import os

from scripts.blender.render.render_card_side import query_root_path


class LocalResourceHandler:
    match_pattern = "localhost.disk://**"

    def __init__(self):
        self.root_path = query_root_path()

    def __call__(self, route, request):
        cleaned_url = request.url.replace("localhost.disk://", "")
        cleaned_url = os.path.join(self.root_path, "assets", cleaned_url)

        if os.path.exists(cleaned_url):
            file_ext = os.path.splitext(cleaned_url)[1].lower()
            content_type_map = {
                # Images
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.gif': 'image/gif',
                '.bmp': 'image/bmp',
                '.webp': 'image/webp',
                '.svg': 'image/svg+xml',
                '.ico': 'image/x-icon',
                # Text files
                '.css': 'text/css',
                '.html': 'text/html',
                '.htm': 'text/html',
                '.txt': 'text/plain',
                '.js': 'text/javascript',
                '.json': 'application/json',
                '.xml': 'text/xml',
                # Fonts
                '.woff': 'font/woff',
                '.woff2': 'font/woff2',
                '.ttf': 'font/ttf',
                '.otf': 'font/otf',
            }
            content_type = content_type_map.get(file_ext, 'application/octet-stream')

            with open(f"{cleaned_url}", "rb") as resource:
                file_data = resource.read()

            route.fulfill(
                status=200,
                content_type=content_type,
                body=file_data
            )
        else:
            print(f"> File not found: {cleaned_url}")
            route.continue_()
