import boto3
from botocore.exceptions import ClientError
from core.config import settings
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class S3Handler:
    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        self.bucket = settings.AWS_BUCKET_NAME
        self.region = settings.AWS_REGION

    async def upload_image(self, image_data: bytes, original_filename: str) -> dict:
        """
        Upload an image to S3 and return its location details.

        Args:
            image_data: Raw image bytes
            original_filename: Original filename from upload

        Returns:
            dict with bucket, region, and key information
        """
        try:
            # Generate a unique key for the image
            timestamp = datetime.utcnow().strftime("%Y/%m/%d/%H%M%S")
            key = f"food_images/{timestamp}_{original_filename}"

            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=image_data,
                ContentType="image/jpeg",  # Assuming JPEG, adjust if needed
            )

            return {"bucket": self.bucket, "region": self.region, "key": key}

        except ClientError as e:
            logger.error(f"Error uploading to S3: {e}")
            raise

    def get_image_url(self, key: str) -> str:
        """
        Generate a presigned URL for accessing the image.

        Args:
            key: S3 object key

        Returns:
            Presigned URL for the image
        """
        try:
            url = self.s3_client.generate_presigned_url(
                "get_object", Params={"Bucket": self.bucket, "Key": key}, ExpiresIn=3600  # URL valid for 1 hour
            )
            return url
        except ClientError as e:
            logger.error(f"Error generating presigned URL: {e}")
            raise
