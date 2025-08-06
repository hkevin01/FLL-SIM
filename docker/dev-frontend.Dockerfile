# Frontend Development Container
# Optimized for modern frontend development with all major frameworks
FROM node:20-alpine

# Install system dependencies
RUN apk add --no-cache \
    git \
    curl \
    wget \
    bash \
    zsh \
    vim \
    nano \
    python3 \
    py3-pip \
    build-base \
    cairo-dev \
    jpeg-dev \
    pango-dev \
    musl-dev \
    giflib-dev \
    pixman-dev \
    pangomm-dev \
    libjpeg-turbo-dev \
    freetype-dev

# Set working directory
WORKDIR /workspace

# Create development user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S frontend -u 1001 -G nodejs && \
    mkdir -p /workspace && \
    chown -R frontend:nodejs /workspace

# Install global Node.js tools and package managers
RUN npm install -g \
    # Package managers
    npm@latest \
    yarn@latest \
    pnpm@latest \
    # Build tools
    vite@latest \
    webpack@latest \
    webpack-cli@latest \
    parcel@latest \
    esbuild@latest \
    rollup@latest \
    # Framework CLIs
    @angular/cli@latest \
    @vue/cli@latest \
    create-react-app@latest \
    create-next-app@latest \
    @sveltejs/kit@latest \
    # Development tools
    typescript@latest \
    ts-node@latest \
    tsx@latest \
    nodemon@latest \
    concurrently@latest \
    # Code quality
    eslint@latest \
    prettier@latest \
    stylelint@latest \
    # Testing tools
    jest@latest \
    vitest@latest \
    playwright@latest \
    cypress@latest \
    # Build analysis
    webpack-bundle-analyzer@latest \
    size-limit@latest \
    # CSS tools
    sass@latest \
    less@latest \
    postcss@latest \
    autoprefixer@latest \
    tailwindcss@latest \
    # Utilities
    serve@latest \
    http-server@latest \
    live-server@latest

# Install browser dependencies for testing
RUN npx playwright install-deps

# Install additional development tools
RUN npm install -g \
    storybook@latest \
    chromatic@latest \
    netlify-cli@latest \
    vercel@latest \
    surge@latest \
    firebase-tools@latest

# Install Python tools for hybrid projects
RUN pip3 install --no-cache-dir \
    pre-commit \
    black \
    flake8

# Setup Oh My Zsh for better terminal experience
RUN sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended

# Create common project directories
RUN mkdir -p /workspace/projects && \
    mkdir -p /workspace/templates && \
    mkdir -p /workspace/tools && \
    mkdir -p /workspace/cache && \
    chown -R frontend:nodejs /workspace

# Setup cache directories for package managers
RUN mkdir -p /home/frontend/.npm && \
    mkdir -p /home/frontend/.yarn && \
    mkdir -p /home/frontend/.pnpm-store && \
    chown -R frontend:nodejs /home/frontend

# Health check script
COPY docker/scripts/frontend-healthcheck.sh /usr/local/bin/healthcheck.sh
RUN chmod +x /usr/local/bin/healthcheck.sh

# Switch to development user
USER frontend

# Setup shell configuration
RUN echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc && \
    echo 'export EDITOR=vim' >> ~/.zshrc && \
    echo 'alias ll="ls -la"' >> ~/.zshrc && \
    echo 'alias serve="npx serve"' >> ~/.zshrc && \
    echo 'alias dev="npm run dev"' >> ~/.zshrc && \
    echo 'alias build="npm run build"' >> ~/.zshrc && \
    echo 'alias test="npm test"' >> ~/.zshrc

# Set environment variables
ENV NODE_ENV=development
ENV BROWSER=none
ENV CHOKIDAR_USEPOLLING=true
ENV WATCHPACK_POLLING=true

# Expose common frontend ports
EXPOSE 3000 3001 4000 4200 5173 8080 8000 9000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD /usr/local/bin/healthcheck.sh

# Default command
CMD ["zsh"]
