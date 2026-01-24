from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Dict, Optional
import logging
import os
from datetime import datetime
from backend.models import ThumbnailRequest, APIResponse
from backend.utils.logging_utils import log_execution
import json

logger = logging.getLogger(__name__)

router = APIRouter()

# Thumbnail Configuration
THUMBNAIL_CONFIG = {
    "styles": {
        "modern": {
            "font": "Roboto-Bold",
            "background": "gradient",
            "accent_color": "#FF0000",
            "text_color": "#FFFFFF",
            "layout": "centered"
        },
        "minimal": {
            "font": "Montserrat-Regular",
            "background": "solid",
            "accent_color": "#000000",
            "text_color": "#FFFFFF",
            "layout": "asymmetric"
        },
        "bold": {
            "font": "Impact",
            "background": "pattern",
            "accent_color": "#FFD700",
            "text_color": "#000000",
            "layout": "split"
        },
        "tech": {
            "font": "SpaceMono-Regular",
            "background": "circuit",
            "accent_color": "#00FF00",
            "text_color": "#FFFFFF",
            "layout": "grid"
        }
    },
    "dimensions": {
        "width": 1280,
        "height": 720
    },
    "output_dir": "images",
    "formats": ["jpg", "png", "webp"],
    "default_format": "jpg"
}

def ensure_output_dir():
    """Ensure the output directory exists."""
    os.makedirs(THUMBNAIL_CONFIG["output_dir"], exist_ok=True)

def generate_filename(title: str, style: str, format: str) -> str:
    """Generate a unique filename for the thumbnail."""
    # Clean title for filename
    clean_title = "".join(c for c in title if c.isalnum() or c in " -_").strip()
    clean_title = clean_title.replace(" ", "_")[:30]
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"thumb_{clean_title}_{style}_{timestamp}.{format}"

def process_title(title: str, style: str) -> Dict[str, str]:
    """
    Process title for thumbnail generation.
    
    Args:
        title (str): Video title
        style (str): Thumbnail style
        
    Returns:
        Dict[str, str]: Processed title components
    """
    # Split title into main and subtitle if possible
    parts = title.split(":", 1)
    if len(parts) > 1:
        main_title = parts[0].strip()
        subtitle = parts[1].strip()
    else:
        main_title = title
        subtitle = ""
    
    # Get style configuration
    style_config = THUMBNAIL_CONFIG["styles"].get(style, THUMBNAIL_CONFIG["styles"]["modern"])
    
    return {
        "main_title": main_title,
        "subtitle": subtitle,
        "font": style_config["font"],
        "text_color": style_config["text_color"],
        "accent_color": style_config["accent_color"]
    }

def _resolve_pil_format(format: str) -> str:
    fmt = format.lower().strip()
    if fmt == "jpg":
        return "JPEG"
    if fmt == "png":
        return "PNG"
    if fmt == "webp":
        return "WEBP"
    return "JPEG"

def _resize_to_target(img, target_width: int, target_height: int):
    target_ratio = target_width / target_height
    img_ratio = img.width / img.height

    if img_ratio > target_ratio:
        new_width = int(img.height * target_ratio)
        left = max(0, (img.width - new_width) // 2)
        img = img.crop((left, 0, left + new_width, img.height))
    else:
        new_height = int(img.width / target_ratio)
        top = max(0, (img.height - new_height) // 2)
        img = img.crop((0, top, img.width, top + new_height))

    try:
        from PIL import Image
        resample = Image.LANCZOS
    except Exception:
        resample = None

    if resample:
        return img.resize((target_width, target_height), resample=resample)
    return img.resize((target_width, target_height))

async def generate_thumbnail(
    title: str,
    style: str,
    colors: Optional[List[str]] = None,
    format: str = THUMBNAIL_CONFIG["default_format"]
) -> Dict[str, str]:
    """
    Generate thumbnail image.
    
    Args:
        title (str): Video title
        style (str): Thumbnail style
        colors (Optional[List[str]]): Custom colors
        format (str): Output image format
        
    Returns:
        Dict[str, str]: Path to generated thumbnail
    """
    try:
        # Ensure output directory exists
        ensure_output_dir()
        
        # Process title
        title_data = process_title(title, style)
        
        # Generate filename
        filename = generate_filename(title, style, format)
        output_path = os.path.join(THUMBNAIL_CONFIG["output_dir"], filename)
        
        # Implement actual thumbnail generation using OpenAI DALL-E 3
        from openai import AsyncOpenAI
        from backend.config.enhanced_settings import settings
        import httpx
        
        client = AsyncOpenAI(api_key=settings.ai.openai_api_key)
        
        # Create a detailed prompt based on title and style
        prompt = f"Professional YouTube thumbnail for a video titled: '{title}'. Style: {style}. Highly engaging, high contrast, 4k, digital art."
        
        response = await client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        
        image_url = response.data[0].url
        
        # Download and save the image
        async with httpx.AsyncClient() as http_client:
            img_response = await http_client.get(image_url)
            if img_response.status_code == 200:
                from io import BytesIO
                from PIL import Image

                img = Image.open(BytesIO(img_response.content))
                target_width = THUMBNAIL_CONFIG["dimensions"]["width"]
                target_height = THUMBNAIL_CONFIG["dimensions"]["height"]
                img = _resize_to_target(img, target_width, target_height)
                if format.lower() in ("jpg", "jpeg"):
                    img = img.convert("RGB")
                img.save(output_path, format=_resolve_pil_format(format))
                logger.info("Successfully generated and saved thumbnail to: %s", output_path)
            else:
                raise Exception(f"Failed to download generated image: {img_response.status_code}")
        
        # Log the generation
        log_execution(
            "thumbnail_generation",
            "success",
            {
                "title": title,
                "style": style,
                "colors": colors,
                "output_path": output_path
            }
        )
        
        return {
            "path": output_path,
            "format": format,
            "dimensions": THUMBNAIL_CONFIG["dimensions"],
            "style": style
        }
        
    except Exception as e:
        logger.error(f"Error generating thumbnail: {str(e)}")
        raise

@router.post("/generate", response_model=APIResponse)
async def generate_thumbnail_endpoint(
    request: ThumbnailRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate a thumbnail image.
    
    Args:
        request (ThumbnailRequest): Thumbnail generation parameters
        background_tasks (BackgroundTasks): FastAPI background tasks
        
    Returns:
        APIResponse: Generation status and metadata
    """
    try:
        # Validate style
        if request.style not in THUMBNAIL_CONFIG["styles"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid style. Valid styles: {list(THUMBNAIL_CONFIG['styles'].keys())}"
            )
        
        # Generate thumbnail
        result = await generate_thumbnail(
            request.title,
            request.style,
            request.colors
        )
        
        return APIResponse(
            status="success",
            data=result,
            message="Thumbnail generated successfully"
        )
        
    except Exception as e:
        logger.error(f"Error in thumbnail generation: {str(e)}")
        log_execution("thumbnail_generation", "error", {"error": str(e)})
        raise HTTPException(
            status_code=500,
            detail=f"Error generating thumbnail: {str(e)}"
        )

@router.get("/styles", response_model=APIResponse)
async def get_styles():
    """Get available thumbnail styles."""
    try:
        return APIResponse(
            status="success",
            data={"styles": THUMBNAIL_CONFIG["styles"]},
            message="Styles retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error retrieving styles: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving styles: {str(e)}"
        )

@router.get("/dimensions", response_model=APIResponse)
async def get_dimensions():
    """Get thumbnail dimensions."""
    try:
        return APIResponse(
            status="success",
            data={"dimensions": THUMBNAIL_CONFIG["dimensions"]},
            message="Dimensions retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error retrieving dimensions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving dimensions: {str(e)}"
        )
