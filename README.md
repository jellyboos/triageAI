# Party 4 U

A Vue.js application for party planning and management.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/party-4-u.git
cd party-4-u
```

2. Install dependencies:

```bash
npm install
```

3. Start the development server:

```bash
npm run dev
```

4. Build for production:

```bash
npm run build
```

## Development

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally
- `npm run lint` - Run ESLint
- `npm run test` - Run tests

## Tech Stack

- Vue 3
- Vite
- TypeScript
- Tailwind CSS

## Requirements

- Node.js 16.x or higher
- npm 7.x or higher

# Party 4 U - Nurse Portal

## 🔥 Firebase Emulator Setup

### ⚙️ Step 1: Initial Setup

#### 🔧 Prerequisites

- Install Node.js
- Install Firebase CLI:

```bash
npm install -g firebase-tools
```

#### 🚀 Initialize Firebase

In your project folder:

```bash
firebase init
```

Select:

- Emulators
- Authentication
- (Optional) Firestore, Functions, etc.

### 🔥 Step 2: Use a Demo Project (recommended)

This keeps everything local and risk-free.

```bash
firebase use --add
```

Choose `demo-myapp` as the project ID (or anything with a `demo-` prefix).

### 🏃‍♂️ Running the Emulators

```bash
firebase emulators:start --project demo-myapp
```

The emulators will be available at:

- Auth Emulator: http://127.0.0.1:9099
- Emulator UI: http://localhost:4000

### 🔐 Environment Variables

Create a `.env` file in the root directory with:

```
VITE_FIREBASE_API_KEY=your_api_key
VITE_FIREBASE_AUTH_DOMAIN=your_auth_domain
VITE_FIREBASE_PROJECT_ID=your_project_id
VITE_FIREBASE_STORAGE_BUCKET=your_storage_bucket
VITE_FIREBASE_MESSAGING_SENDER_ID=your_messaging_sender_id
VITE_FIREBASE_APP_ID=your_app_id
```

### 🚀 Development

```bash
npm install
npm run dev
```

### 🧪 Testing Auth

1. Start the emulators
2. Run the development server
3. Try signing in with:
   - Email/Password
   - Google Sign-In (simulated in emulator)

### 📝 Notes

- The emulator provides a safe environment for testing auth flows
- No real Firebase credentials needed for development
- Auth state persists between emulator restarts
- Emulator UI provides debugging tools and auth state inspection

## Installation
