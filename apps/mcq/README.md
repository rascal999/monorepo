# MCQ Quiz App

A multiple choice quiz application that supports both uploaded quizzes and quizzes from a directory.

## Adding New Quizzes

There are two ways to add quizzes to the application:

1. **Upload Quiz Files**: Use the upload button in the app to add quiz files. These can be modified or deleted through the app interface.

2. **Questions Directory**: Place JSON quiz files in the `public/questions` directory. These will be automatically loaded when the app starts. Files in this directory:
   - Are automatically available to all users
   - Cannot be deleted through the app interface
   - Will be loaded alongside any user-uploaded quizzes
   - Follow the same format as uploaded quizzes

### Quiz File Format

Quiz files should be JSON files with the following structure:

```json
{
    "title": "Quiz Title",
    "questions": [
        {
            "question": "Question text?",
            "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
            "correctAnswer": 1
        }
    ]
}
```

- `title`: The name of the quiz
- `questions`: Array of question objects
  - `question`: The question text
  - `options`: Array of possible answers
  - `correctAnswer`: Index of the correct answer (0-based)

### Example

See `public/questions/general-knowledge.json` for an example quiz file.

## Deployment with TLS

The application supports secure HTTPS deployment using LetsEncrypt certificates. Follow these steps to deploy with TLS:

### Prerequisites

- A domain name pointing to your server
- Docker and Docker Compose installed on your server
- Ports 80 and 443 available on your server

### Deployment Steps

1. Build and run the Docker container with required environment variables:

```bash
docker build -t mcq-app .
docker run -d \
  -p 80:80 \
  -p 443:443 \
  -e DOMAIN=your-domain.com \
  -e EMAIL=your-email@example.com \
  -v letsencrypt:/etc/letsencrypt \
  --name mcq-app \
  mcq-app
```

Replace:
- `your-domain.com` with your actual domain name
- `your-email@example.com` with your email address (used for LetsEncrypt notifications)

### Environment Variables

- `DOMAIN`: Your domain name (required)
- `EMAIL`: Your email address for LetsEncrypt notifications (required)

### Certificate Management

The application automatically handles:
- Initial certificate acquisition
- Certificate renewal (checked every 12 hours)
- HTTP to HTTPS redirection
- Modern SSL configuration with security headers

### Volume Management

The container uses a Docker volume to persist LetsEncrypt certificates:
- `letsencrypt:/etc/letsencrypt`: Stores SSL certificates and LetsEncrypt configuration

### Security Features

The TLS configuration includes:
- Modern SSL protocols (TLSv1.2, TLSv1.3)
- Strong cipher suites
- OCSP Stapling
- Security headers (X-Frame-Options, X-XSS-Protection, etc.)
- Automatic HTTP to HTTPS redirection

### Troubleshooting

1. **Certificate Issues**:
   - Check the container logs: `docker logs mcq-app`
   - Ensure your domain points to the server's IP
   - Verify ports 80 and 443 are accessible

2. **Container Access**:
   - Shell access: `docker exec -it mcq-app sh`
   - View nginx logs: `docker exec mcq-app cat /var/log/nginx/error.log`

3. **Manual Certificate Renewal**:
   - Force renewal: `docker exec mcq-app certbot renew --force-renewal`
