import smtplib
import random
import string
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from fastapi import HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from enums import DataBaseCollectionNames, ResponseSignal
from .base import BaseService
from dto.otp import OTPRequest, OTPVerification, OTPResponse
from dependencies import get_db_client
import logging

class OTPService(BaseService):
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseCollectionNames.OTPS.value]
        self.logger = logging.getLogger(__name__)

    def generate_otp(self) -> str:
        """Generate a random numeric OTP"""
        return ''.join(random.choices(string.digits, k=self.app_settings.OTP_LENGTH))

    async def send_otp_email(self, email: str, otp: str, purpose: str = "verification") -> bool:
        """Send OTP via email using smtplib"""
        try:
            # Validate email configuration
            if not all([
                self.app_settings.SMTP_USERNAME, 
                self.app_settings.SMTP_PASSWORD, 
                self.app_settings.EMAIL_FROM
            ]):
                self.logger.error("Email configuration incomplete. Please set SMTP_USERNAME, SMTP_PASSWORD, and EMAIL_FROM in environment variables.")
                return False
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{self.app_settings.EMAIL_FROM_NAME} <{self.app_settings.EMAIL_FROM}>"
            msg['To'] = email
            msg['Subject'] = f"Your {purpose.title()} Code - {self.app_settings.APP_NAME}"

            # HTML email body
            html_body = f"""
            <html>
              <body>
                <h2>Your Verification Code</h2>
                <p>Hello,</p>
                <p>Your verification code is: <strong style="font-size: 24px; color: #007bff;">{otp}</strong></p>
                <p>This code will expire in {self.app_settings.OTP_EXPIRE_MINUTES} minutes.</p>
                <p>If you didn't request this code, please ignore this email.</p>
                <br>
                <p>Best regards,<br>{self.app_settings.EMAIL_FROM_NAME} Team</p>
              </body>
            </html>
            """
            
            msg.attach(MIMEText(html_body, 'html'))

            # Send email
            with smtplib.SMTP(self.app_settings.SMTP_SERVER, self.app_settings.SMTP_PORT) as server:
                if self.app_settings.SMTP_USE_TLS:
                    server.starttls()
                server.login(self.app_settings.SMTP_USERNAME, self.app_settings.SMTP_PASSWORD)
                server.send_message(msg)
            
            self.logger.info(f"OTP sent successfully to {email}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send OTP to {email}: {str(e)}")
            return False

    async def create_and_send_otp(self, email: str, purpose: str = "verification") -> dict:
        """Generate OTP, store in database, and send via email"""
        try:
            # Generate OTP
            otp_code = self.generate_otp()
            expires_at = datetime.utcnow() + timedelta(minutes=self.app_settings.OTP_EXPIRE_MINUTES)

            # Clear any existing OTPs for this email and purpose
            await self.collection.delete_many({"email": email, "purpose": purpose})

            # Store OTP in database
            otp_document = {
                "email": email,
                "otp_code": otp_code,
                "purpose": purpose,
                "expires_at": expires_at,
                "created_at": datetime.utcnow(),
                "is_verified": False,
                "attempts": 0
            }
            
            await self.collection.insert_one(otp_document)

            # Send OTP via email
            email_sent = await self.send_otp_email(email, otp_code, purpose)
            
            if not email_sent:
                # Clean up if email failed
                await self.collection.delete_one({"email": email, "otp_code": otp_code})
                raise HTTPException(
                    status_code=500, 
                    detail=ResponseSignal.OTP_EMAIL_SEND_FAILED.value
                )

            return {
                "status": "success",
                "message": ResponseSignal.OTP_SEND_SUCCESS.value,
                "expires_at": expires_at
            }

        except Exception as e:
            self.logger.error(f"Error in create_and_send_otp: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail=ResponseSignal.OTP_SEND_ERROR.value
            )

    async def verify_otp(self, email: str, otp_code: str, purpose: str = "verification") -> bool:
        """Verify OTP against stored value"""
        try:
            # Find the OTP record
            otp_record = await self.collection.find_one({
                "email": email,
                "purpose": purpose,
                "is_verified": False
            })

            if not otp_record:
                self.logger.warning(f"No active OTP found for {email}")
                return False

            # Check if OTP has expired
            if datetime.utcnow() > otp_record["expires_at"]:
                await self.collection.delete_one({"_id": otp_record["_id"]})
                self.logger.warning(f"Expired OTP attempt for {email}")
                raise HTTPException(
                    status_code=400, 
                    detail=ResponseSignal.OTP_EXPIRED.value
                )

            # Increment attempt counter
            await self.collection.update_one(
                {"_id": otp_record["_id"]},
                {"$inc": {"attempts": 1}}
            )

            # Check attempt limit (prevent brute force)
            if otp_record["attempts"] >= 3:
                await self.collection.delete_one({"_id": otp_record["_id"]})
                self.logger.warning(f"Too many OTP attempts for {email}")
                raise HTTPException(
                    status_code=429, 
                    detail=ResponseSignal.OTP_TOO_MANY_ATTEMPTS.value
                )

            # Verify OTP code
            if otp_record["otp_code"] == otp_code:
                # Mark as verified and clean up
                await self.collection.update_one(
                    {"_id": otp_record["_id"]},
                    {"$set": {"is_verified": True, "verified_at": datetime.utcnow()}}
                )
                self.logger.info(f"OTP verified successfully for {email}")
                
                # Post-verification callback for email verification
                if purpose == "verification":
                    await self._handle_email_verification_callback(email)
                
                return True
            else:
                self.logger.warning(f"Invalid OTP attempt for {email}")
                return False

        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Error in verify_otp: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail=ResponseSignal.OTP_VERIFY_ERROR.value
            )

    async def _handle_email_verification_callback(self, email: str):
        """Handle post-verification callback for email verification"""
        try:
            from services.user import UserService  # Import here to avoid circular imports
            user_service = UserService(self.db_client)
            
            success = await user_service.verify_user_email(email)
            if success:
                self.logger.info(f"User email marked as verified: {email}")
            else:
                self.logger.warning(f"Failed to mark user email as verified: {email}")
                
        except Exception as e:
            self.logger.error(f"Error in email verification callback: {str(e)}")
            # Don't raise exception here to avoid breaking OTP verification
    
    async def check_otp_cooldown(self, email: str, purpose: str = "verification", cooldown_minutes: int = 2) -> bool:
        """Check if user can request a new OTP (cooldown protection)"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(minutes=cooldown_minutes)
            recent_otp = await self.collection.find_one({
                "email": email,
                "purpose": purpose,
                "created_at": {"$gte": cutoff_time}
            })
            
            return recent_otp is None  # True if no recent OTP found (can send new one)
            
        except Exception as e:
            self.logger.error(f"Error checking OTP cooldown: {str(e)}")
            return True  # Allow sending if check fails

def get_otp_service(db_client: AsyncIOMotorClient = Depends(get_db_client)):
    return OTPService(db_client) 