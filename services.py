import requests

class ImagesAdaptor:
    def __init__(self, resource_url):
        self.resource_url = resource_url
        print(f"Created ImagesAdaptor for {resource_url}")

    def save_image(self, image):
        print("ImagesAdaptor.save_image()...")
        response = requests.post(
            self.resource_url,
            headers={"Content-Type": "application/json"},
            json=image
        )

        if response.ok:
            selected_image = response.json()
            return selected_image
        else:
            # response text provides the HTTP error information
            print(response, response.text if not response.text else "")
            return None
