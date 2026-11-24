FROM node:24-alpine AS frontend
WORKDIR /frontend
COPY live-client/package*.json ./
RUN npm ci
COPY live-client/ .
RUN npm run build
FROM python:3.12-slim
WORKDIR /app
COPY requirements_v2.txt ./
RUN pip install --no-cache-dir -r requirements_v2.txt
COPY server.py ./
COPY caselab_logo_user.png caselab_logo_user_hires.png feedback_advisor.png alex_morgan_portrait.png legal_hero_courthouse.png ./
COPY --from=frontend /frontend/dist ./live-client/dist
CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port ${PORT:-8000}"]
