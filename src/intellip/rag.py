from langchain_upstage import UpstageLayoutAnalysisLoader

def pdfload(file):
    # path_cur = os.path.dirname(os.path.abspath(__file__))
    path_file = file
    layzer = UpstageLayoutAnalysisLoader(
        path_file, use_ocr=True, output_type="html"
    )
    # For improved memory efficiency, consider using the lazy_load method to load documents page by page.
    docs = layzer.load()  # or layzer.lazy_load()

    return docs
