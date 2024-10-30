#!/bin/sh

set -eo pipefail

if [ -f .env ]; then
    . .env
fi

# Wait for the ses service to be available before executing any post-run scripts
while ! nc -z localhost 4566; do
    echo "Waiting for s3 to launch on port 4566..."
    sleep 2
done

echo 'Running AWS verify identity command.'
aws ses verify-email-identity --email-address ${MAIL_FROM} --region ${AWS_DEFAULT_REGION} --endpoint-url=${LOCALSTACK_ENDPOINT}
echo "Verified ${MAIL_FROM}"