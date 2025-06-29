from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from dto.otp import OTPRequest, OTPVerification, OTPResponse
from services.otp import OTPService, get_otp_service
from enums import ResponseSignal
from controllers.BaseController import BaseController
import logging

logger = logging.getLogger(__name__)

otp_router = APIRouter(
    prefix="/api/v1/otp",
    tags=["api_v1", "otp"],
    responses={404: {"description": "Not found"}},
)

@otp_router.post("/send", response_model=OTPResponse, status_code=status.HTTP_200_OK)
async def send_otp(
    otp_request: OTPRequest,
    otp_service: OTPService = Depends(get_otp_service)
):
    """
    Send OTP to user's email address.
    
    - **email**: User's email address
    - **purpose**: Purpose of OTP (verification, password-reset, etc.)
    """
    try:
        result = await otp_service.create_and_send_otp(
            email=otp_request.email,
            purpose=otp_request.purpose
        )
        
        otp_data = BaseController().get_json_serializable_object(result)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "signal": ResponseSignal.OTP_SEND_SUCCESS.value,
                "otp": otp_data
            }
        )
        
    except HTTPException as http_exc:
        logger.error(f"HTTP Error in send_otp: {http_exc.detail}")
        raise http_exc
    except Exception as e:
        logger.error(f"Error in send_otp: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ResponseSignal.OTP_SEND_ERROR.value
        )

@otp_router.post("/verify", status_code=status.HTTP_200_OK)
async def verify_otp(
    otp_verification: OTPVerification,
    otp_service: OTPService = Depends(get_otp_service)
):
    """
    Verify OTP submitted by user.
    
    - **email**: User's email address
    - **otp_code**: 6-digit OTP code
    - **purpose**: Purpose of OTP verification
    """
    try:
        is_valid = await otp_service.verify_otp(
            email=otp_verification.email,
            otp_code=otp_verification.otp_code,
            purpose=otp_verification.purpose
        )
        
        if is_valid:
            # Provide different messages based on purpose
            if otp_verification.purpose == "verification":
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "signal": ResponseSignal.EMAIL_VERIFICATION_SUCCESS.value,
                        "message": "Email verified successfully. You can now log in.",
                        "purpose": otp_verification.purpose
                    }
                )
            else:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "signal": ResponseSignal.OTP_VERIFY_SUCCESS.value,
                        "message": "OTP verified successfully",
                        "purpose": otp_verification.purpose
                    }
                )
        else:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.OTP_VERIFY_ERROR.value,
                    "message": "Invalid or expired OTP"
                }
            )
            
    except HTTPException as http_exc:
        logger.error(f"HTTP Error in verify_otp: {http_exc.detail}")
        raise http_exc
    except Exception as e:
        logger.error(f"Error in verify_otp: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ResponseSignal.OTP_VERIFY_ERROR.value
        ) 