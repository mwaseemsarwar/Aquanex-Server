set -e

echo "🚀 Starting project with Docker Compose..."

docker-compose up --build -d

echo "✅ Services started:"
docker-compose ps

echo ""
echo "🌍 API available at: http://localhost"
echo "📖 Docs: http://localhost/docs"
echo "💓 Health check: http://localhost/health"
