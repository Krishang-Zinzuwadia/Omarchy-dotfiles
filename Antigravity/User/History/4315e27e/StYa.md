# Icarus

icarus is your most goated ai agent that controls your entire pc and all the data on it

[![Build](https://github.com/Krishang-Zinzuwadia/icarus/actions/workflows/build.yml/badge.svg)](https://github.com/Krishang-Zinzuwadia/icarus/actions/workflows/build.yml)

## What technologies are used for this project?

This project is built with:

**Landing page:**
- Vite
- TypeScript
- React
- shadcn-ui
- Tailwind CSS

**Desktop app:**
- Tauri
- Rust

**AI pipeline:**
- Python

**Mobile app:**
- Jetpack Compose
- Kotlin


## Project Structure

This repository contains the Icarus AI project with the following structure:

```
├── src/                     # Main website source (icarus-ai-orchestra)
├── landing-page/            # Simple landing page React app
├── website/                 # Original website backup
├── icarus-android-app/      # Android application
├── ai-agents/               # AI agent implementations
└── assets/                  # Shared assets
```

## Development

### Main Website (Port 8080)
The main Icarus website with full UI components and routing:
```bash
npm run dev:main
# or simply
npm run dev
```

### Landing Page (Port 3001)
Simple React landing page:
```bash
npm run dev:landing
```

## Building

### Build Main Website
```bash
npm run build:main
```

### Build Landing Page
```bash
npm run build:landing
```

### Build Both
```bash
npm run build:all
```

## Setup

Install dependencies for both projects:
```bash
npm run install:all
```

## Deployment Structure

- Main website builds to `./dist/`
- Landing page builds to `./dist/landing/`
- Both can be deployed together without conflicts

## Project info

**URL**: PLEASE INSERT HERE


to  connect phone 

ip addr show | grep "inet " | grep -v "127.0.0.1" | awk '{print $2}' | cut -d'/' -f1
ad put the first one in apiconfig,kt

incredible pt3
