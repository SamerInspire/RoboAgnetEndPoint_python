import easyocr


def extract_numbers_and_symbols_from_image(image_path):
    reader = easyocr.Reader(['en', 'ar'], gpu=False)  # Specify the languages you want to use

    results = reader.readtext(image_path)

    extracted_text = ""
    for detection in results:
        text = detection[1]
        extracted_text += text

    return extracted_text


if __name__ == "__main__":
    image_path = "https://qiwacare.zendesk.com/sc/attachments/conversations/655d940e594b87a83415c887/4NctiLAXy5sM_TwLDcGQYSV6/%D9%81%D8%B1%D8%AC.jpeg"  # Replace with the path to your image
    extracted_text = extract_numbers_and_symbols_from_image(image_path)

    if extracted_text:
        print("Extracted Numbers and Symbols:")
        print(extracted_text)
    else:
        print("No numbers and symbols could be extracted from the image.")
