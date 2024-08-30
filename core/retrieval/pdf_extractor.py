import pdfplumber
import fitz  # PyMuPDF
import pdftotext

support_fonts_list = ['TrueType', 'Type1', 'Type0']


class PDFTextExtractor:
    def __init__(self, library="pdfplumber"):
        """
        初始化 PDF 文本提取器，可以选择不同的库。
        :param library: 可选的值为 'pdfplumber', 'pymupdf', 'pdftotext'。
        """
        self.library = library.lower()

    def check_fonts(self, pdf_path):
        fonts = self.list_pdf_fonts(pdf_path)
        for font in fonts:
            if font not in support_fonts_list:
                return False
        return True

    def list_pdf_fonts(self, pdf_path):
        doc = fitz.open(pdf_path)

        all_fonts = set()  # 使用集合来避免重复
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            for font in page.get_fonts():
                font_name = font[2]  # 可以获取更多字体信息
                all_fonts.add(font_name)
                # if font_name.lower() not in FONT_LIST:
                #     print(pdf_path, f": {font}")

        doc.close()
        return all_fonts

    def extract_text(self, pdf_path, page_number=None):
        """
        根据配置提取 PDF 文本，支持指定页面。
        :param pdf_path: PDF 文件路径。
        :param page_number: 指定提取第几页文本，默认为 None 提取所有页面。
        :return: 提取的文本内容。
        """
        if not self.check_fonts(pdf_path):
            return ""

        if self.library == "pdfplumber":
            return self._extract_with_pdfplumber(pdf_path, page_number)
        elif self.library == "pymupdf":
            return self._extract_with_pymupdf(pdf_path, page_number)
        elif self.library == "pdftotext":
            return self._extract_with_pdftotext(pdf_path, page_number)
        else:
            raise ValueError(f"不支持的库: {self.library}")

    def _extract_with_pdftotext(self, pdf_path, page_number):
        with open(pdf_path, "rb") as f:
            pdf = pdftotext.PDF(f)

        if page_number >= len(pdf):
            return ""

        return pdf[page_number]

    def _extract_with_pdfplumber(self, pdf_path, page_number):
        """使用 pdfplumber 提取文本"""
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            if page_number is None:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
            else:
                text = pdf.pages[page_number - 1].extract_text()
        return text

    def _extract_with_pymupdf(self, pdf_path, page_number):
        """使用 PyMuPDF 提取文本"""
        text = ""
        doc = fitz.open(pdf_path)
        if page_number is None:
            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                text += page.get_text("text") + "\n"
        else:
            page = doc.load_page(page_number - 1)
            text = page.get_text("text")
        return text

    def get_page_count(self, pdf_path):
        """
        获取 PDF 总页数。
        :param pdf_path: PDF 文件路径。
        :return: 总页数。
        """
        if self.library == "pdfplumber":
            with pdfplumber.open(pdf_path) as pdf:
                return len(pdf.pages)
        elif self.library == "pymupdf":
            doc = fitz.open(pdf_path)
            return doc.page_count
        elif self.library == "pdftotext":
            with open(pdf_path, "rb") as f:
                pdf = pdftotext.PDF(f)
                return len(pdf)
        else:
            raise ValueError(f"不支持的库: {self.library}")
