# Frontend Setup & Testing Guide

## Prerequisites

- Node.js 18+ (required for Vite + React)
- npm or pnpm

## Setup

### 1. Install Dependencies

```bash
cd src/sd_model_manager/ui/frontend
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

**Note**: The dev server is configured with proxies:
- `/api/*` → `http://localhost:8000`
- `/ws/*` → `ws://localhost:8000`

### 3. Start Backend (in another terminal)

```bash
cd /Users/kuniaki-k/Code/SD-Model-Manager
python -m src.sd_model_manager
```

The backend will be available at `http://localhost:8000`

## Manual Testing

Once both frontend and backend are running:

1. Open `http://localhost:5173/download` in your browser
2. Enter a Civitai model URL: `https://civitai.com/models/{id}/{name}`
3. Enter a filename: `model.safetensors`
4. Click "Start Download"
5. Watch the progress bar update in real-time via WebSocket
6. Wait for completion message

## Running E2E Tests

### Run all E2E tests

```bash
npm run test:e2e
```

### Run tests with interactive UI

```bash
npm run test:e2e:ui
```

### Run tests in debug mode

```bash
npm run test:e2e:debug
```

## Building for Production

```bash
npm run build
```

Output will be in `dist/` directory.

## Project Structure

```
frontend/
├── src/
│   ├── main.tsx              # React entry point
│   ├── App.tsx               # Main router
│   ├── index.css             # Tailwind CSS
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Sidebar.tsx
│   │   │   └── MainLayout.tsx
│   │   └── download/
│   │       ├── DownloadForm.tsx
│   │       └── ProgressBar.tsx
│   ├── hooks/
│   │   └── useDownload.ts    # Download logic hook
│   └── pages/
│       └── DownloadPage.tsx
├── e2e/
│   └── download-flow.spec.ts # Playwright tests
├── index.html                # HTML entry point
├── package.json
├── vite.config.ts
├── playwright.config.ts
├── tsconfig.json
├── tailwind.config.js
└── postcss.config.js
```

## Development Commands

| Command | Purpose |
|---------|---------|
| `npm run dev` | Start dev server with HMR |
| `npm run build` | Build for production |
| `npm run preview` | Preview production build locally |
| `npm run test:e2e` | Run all E2E tests |
| `npm run test:e2e:ui` | Run E2E tests with UI |
| `npm run test:e2e:debug` | Run E2E tests with debugger |

## Notes

- The frontend uses React 18 with TypeScript
- Styling is done with Tailwind CSS
- Navigation uses React Router v6
- WebSocket communication is handled by the `useDownload` hook
- All API calls include proper error handling
- Form validation is client-side (URL format, required fields)

## Troubleshooting

### WebSocket connection fails
- Ensure the backend is running on `http://localhost:8000`
- Check the vite.config.ts proxy settings
- Check browser console for WebSocket error messages

### API calls return 404
- Ensure the backend is running
- Check that the vite proxy is configured correctly
- Verify the API endpoint path in useDownload.ts

### Progress bar not updating
- Check browser DevTools Network tab for WebSocket messages
- Verify the task_id is being returned from the POST request
- Check backend logs for any errors

## Next Steps

Once manual testing is complete and verified:
1. Commit Phase 2 implementation to `phase2/download-implementation` branch
2. Create pull request to merge into `main`
3. Begin Phase 3: Download history tracking
