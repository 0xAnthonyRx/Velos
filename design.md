# Image Upload App Design

## Overview
A simple image upload application that allows users to upload images which are stored in a public S3 bucket and accessible via direct URLs.

## Architecture

### Components
1. **Frontend** - Web interface for image uploads
2. **Backend API** - Handles upload requests and S3 operations
3. **S3 Bucket** - Private bucket for image storage
4. **CloudFront** - CDN with Origin Access Control (OAC) for secure delivery

### Flow
```
User → Frontend → Backend API → S3 Bucket (Private)
                                      ↓
                              CloudFront OAC → Public HTTPS URL
```

## Infrastructure (Terraform)

### S3 Bucket Configuration
- **Bucket**: Private (all public access blocked)
- **Access**: Only via CloudFront OAC
- **CORS**: Enabled for browser uploads
- **Versioning**: Optional
- **Lifecycle**: Optional cleanup rules for old images

### CloudFront Configuration
- **Origin Access Control (OAC)**: Secure access to private S3 bucket
- **Protocol**: HTTPS only (redirect HTTP to HTTPS)
- **Caching**: Default TTL 24 hours
- **Distribution**: Global edge locations

### Required Resources
- `aws_s3_bucket` - Private storage bucket
- `aws_s3_bucket_public_access_block` - Block all public access
- `aws_s3_bucket_policy` - Allow CloudFront OAC access only
- `aws_s3_bucket_cors_configuration` - Enable cross-origin requests
- `aws_cloudfront_origin_access_control` - OAC for S3 access
- `aws_cloudfront_distribution` - CDN for image delivery
- `aws_iam_user` or `aws_iam_role` - For backend API access
- `aws_iam_policy` - PutObject permissions

## API Endpoints

### POST /upload
- Accepts: multipart/form-data with image file
- Validates: file type (jpg, png, gif, webp), size limit
- Generates: unique filename (UUID + extension)
- Uploads to S3 (private bucket)
- Returns: CloudFront URL (https://[distribution-id].cloudfront.net/[filename])

### GET /images (optional)
- Lists recently uploaded images
- Returns: array of CloudFront URLs

## Security Considerations

### CloudFront OAC Benefits
- S3 bucket remains private (no public access)
- Only CloudFront can access bucket contents
- HTTPS enforced for all image access
- DDoS protection via AWS Shield Standard
- Access logs available for monitoring

### Additional Security
- Rate limiting on upload endpoint
- File type validation (magic number check)
- File size limits (e.g., 5MB max)
- Filename sanitization
- Optional: API key for upload endpoint
- Optional: S3 lifecycle policy to auto-delete old files

## Technology Stack

### Backend Options
- Node.js + Express
- Python + Flask/FastAPI
- Go + Gin

### Frontend Options
- React/Vue/Vanilla JS
- Direct browser upload with presigned URLs (alternative)

### AWS SDK
- Backend uses AWS SDK to interact with S3
- Credentials via IAM user access keys or EC2/ECS role

## Deployment

### Infrastructure
```
terraform init
terraform plan
terraform apply
```

### Application
- Backend deployed to EC2, ECS, Lambda, or any compute service
- Frontend served as static files or via backend
- Environment variables: S3_BUCKET_NAME, CLOUDFRONT_DOMAIN, AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

## File Structure
```
/
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── terraform.tfvars
├── backend/
│   ├── server.js (or main.py, main.go)
│   └── package.json
└── frontend/
    ├── index.html
    └── upload.js
```

## Cost Considerations
- S3 storage: ~$0.023/GB/month
- S3 PUT requests: ~$0.005/1000 requests
- CloudFront data transfer: ~$0.085/GB (first 10TB)
- CloudFront requests: ~$0.0075/10,000 HTTP requests
- No S3 GET request charges (CloudFront retrieves from S3)

## Future Enhancements
- Image resizing/optimization before upload
- Thumbnail generation
- Metadata storage (DynamoDB)
- Upload progress tracking
- Batch uploads
- Image deletion endpoint
