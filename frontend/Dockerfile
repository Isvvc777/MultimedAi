FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the frontend code
COPY . .

# Expose port for Vite
EXPOSE 3000

# Start the dev server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
