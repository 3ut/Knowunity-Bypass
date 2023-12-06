import httpx
import json
import img2pdf
import os
import tempfile
from bs4 import BeautifulSoup
from io import BytesIO
from PIL import Image


class KnowunityClient:
    def __init__(self):
        self._images = []

    @staticmethod
    def _download_image(url):
        response = httpx.get(url)
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            return image
        else:
            print(f"[!] Failed to download image from {url}")
            return None
        
    @staticmethod
    def _get_script_content(response):
        soup = BeautifulSoup(response.text, 'html.parser')
        script_tag = soup.find('script', {'id': '__NEXT_DATA__'})
        if script_tag:
            return script_tag.contents[0]
        return None
    
    @property
    def images(self):
        return self._images
    
    def download_images(self):
        images = []
        for url in self._images:
            image = self._download_image(url)
            if image:
                images.append(image)
        return images

    def convert_webp_to_pdf(self, output_pdf_path):
        images = self.download_images()

        if images:
            with tempfile.TemporaryDirectory() as temp_dir:
                image_paths = []
                for i, image in enumerate(images):
                    image_path = os.path.join(temp_dir, f"image_{i}.png")
                    image.save(image_path, format='PNG')
                    image_paths.append(image_path)

                pdf_bytes = img2pdf.convert(image_paths)

            with open(output_pdf_path, 'wb') as pdf_file:
                pdf_file.write(pdf_bytes)
            print(f"[!] PDF created successfully at {output_pdf_path}")
        else:
            print("[!] No images downloaded. PDF not created.")


    def connect(self, url: str = None):
        if url is None:
            url = input("[!] Enter KnowUnity URL: ")

        r = httpx.get(url, follow_redirects=True)
        r_ = httpx.get(r.url)

        script_content = self._get_script_content(r_)
        if script_content:
            data = json.loads(script_content)
            contents = data['props']['pageProps']['know']['knowDocumentPages']

            for content in contents:
                print(f"[!] Contents: [{content['imageUrl']}]")
                self._images.append(content['imageUrl'])

            self.convert_webp_to_pdf(output_pdf_path='output.pdf')
        else:
            print("[!] Script tag not found.")


if __name__ == '__main__':
    client = KnowunityClient()
    client.connect()