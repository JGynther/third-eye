set -euo pipefail

if [ $# -lt 1 ]; then
    echo "Usage: $0 s3://your-bucket-name[/optional/prefix/]" >&2
    exit 1
fi

S3_BUCKET="$1"

case "$S3_BUCKET" in
    */) : ;;
    *)  S3_BUCKET="${S3_BUCKET}/" ;;
esac

DB_PATH="$HOME/.local/share/third-eye/collection.db"
DATE=$(date +%Y-%m-%d)
BACKUP_NAME="3i-backup-${DATE}.db"

if [[ ! -f "$DB_PATH" ]]; then
    echo "Error: Database not found at $DB_PATH"
    exit 1
fi

if ! aws sts get-caller-identity >/dev/null 2>&1; then
    echo "AWS credentials not found or expired. Running 'aws sso login'..."
    aws sso login
fi

aws s3 cp "$DB_PATH" "${S3_BUCKET}${BACKUP_NAME}"

echo "✅ Backup complete: ${BACKUP_NAME}"
