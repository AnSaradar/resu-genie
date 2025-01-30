from fastapi import FastAPI, APIRouter, Depends , status
from fastapi.responses import JSONResponse, FileResponse
from core.config import get_settings ,Settings
from enums import ResponseSignal,TemplateEnum
from schemas import Resume
from controllers import ResumeController
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import pdfkit
import logging
import os
import asyncio
from pyppeteer import launch


resume_router = APIRouter(
    prefix = "/api/v1/resume",
    tags = ["api_v1"]
)

logger = logging.getLogger(__name__)

# Initialize Jinja2 environment
env = Environment(loader=FileSystemLoader("resume_templates"))


@resume_router.post("/build")
async def build_resume(resume_data: Resume, app_settings: Settings = Depends(get_settings)):
    try:

        resume_data_dict = ResumeController().prepare_resume_data(resume = resume_data)
        template = env.get_template(TemplateEnum.IMAGINE.value)
        rendered_html = template.render(**resume_data_dict)

        #html_file_path = "outputs/rendered_resume.html"
        # with open(html_file_path, "w", encoding="utf-8") as html_file:
        #     html_file.write(rendered_html)

        pdf_file_path = "outputs/resume_output.pdf"
        HTML(string=rendered_html).write_pdf(pdf_file_path)
        
        # browser = await launch()
        # page = await browser.newPage()

        # await page.setContent(rendered_html)
        # await page.pdf({'path': pdf_file_path, 'format': 'A4'})
        # await browser.close()

        return FileResponse(
            pdf_file_path,
            media_type="application/pdf",
            filename="resume.pdf"
        )
    
    except Exception as e:
        logger.error(f"Error building resume: {str(e)}")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
                                              "signal" : ResponseSignal.RESUME_BUILT_FAILURE.value
                                              })
    
    finally:
        # Clean up temporary PDF file
        if os.path.exists("resume_output.pdf"):
            os.remove("resume_output.pdf")